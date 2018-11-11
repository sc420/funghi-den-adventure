import copy
import itertools
import yaml

# STAT_NAMES = ['vitality', 'intelligence', 'speed']
# SKILL_NAMES = ['luck', 'insensitive', 'horn', 'agile', 'night_eyes', 'stealth',
#                'cute', 'food', 'swimmer', 'big_eater', 'short_range_attack',
#                'submerge', 'flight', 'luminescent', 'cold_resist', 'hard_head',
#                'photosynthesis', 'weaponry', 'motivated', 'long_range_attack',
#                'poison', 'courage', 'smart', 'iron_fist', 'sensor']

REQUIRED_ADVENTURE_SPEC_NAMES = ['stats', 'skills', 'boosts']
REQUIRED_FUNGHI_SPEC_NAMES = ['stats', 'skills']
EMPTY_ID = -1
EMPTY_FUNGHI = {
    'capacity': 0,
    'name': '<EMPTY>',
    'stats': [],
    'skills': [],
}


def load_data():
    with open('data/adventures.yaml', 'r', encoding='utf8') as stream:
        adventures = yaml.load(stream)
    with open('data/funghis.yaml', 'r', encoding='utf8') as stream:
        funghis = yaml.load(stream)
    with open('data/rewards.yaml', 'r', encoding='utf8') as stream:
        rewards = yaml.load(stream)
    return {
        'adventures': adventures,
        'funghis': funghis,
        'rewards': rewards,
    }


def normalize_data(data):
    normalize_adventures(data['adventures'])
    normalize_funghis(data['funghis'])


def normalize_adventures(adventures):
    for adventure in adventures.values():
        requirements = adventure['requirements']
        for requirement in requirements.values():
            for spec_name in REQUIRED_ADVENTURE_SPEC_NAMES:
                if not spec_name in requirement:
                    requirement[spec_name] = []


def normalize_funghis(funghis):
    for funghi in funghis.values():
        for spec_name in REQUIRED_FUNGHI_SPEC_NAMES:
            if not spec_name in funghi:
                funghi[spec_name] = []


def calc_total_adventure_capacity(data):
    count = 0
    adventures = data['adventures']
    for adventure in adventures.values():
        count += adventure['capacity']
    return count


def calc_total_funghi_capacity(data):
    count = 0
    funghis = data['funghis']
    for funghi in funghis.values():
        count += funghi['capacity']
    return count


def gen_funghi_permutations(data, adventure_capacity, funghi_capacity):
    candidates = []
    # Generate funghi candidates
    funghis = data['funghis']
    for funghi_id, funghi in funghis.items():
        fungi_repeated_ids = itertools.repeat(funghi_id, funghi['capacity'])
        candidates.append(*list(fungi_repeated_ids))
    # If there are not enough funghis, generate empty funghis
    if funghi_capacity < adventure_capacity:
        empty_size = adventure_capacity - funghi_capacity
        empty_repeated_ids = itertools.repeat(EMPTY_ID, empty_size)
        candidates.append(*list(empty_repeated_ids))
    return itertools.permutations(candidates, adventure_capacity)


def convert_permutations_to_allocations(data, funghi_permutations):
    allocations = []
    adventures = data['adventures']
    for permutation in funghi_permutations:
        allocation = {}
        ofs_start = 0
        for adventure_id, adventure in adventures.items():
            capacity = adventure['capacity']
            ofs_end = ofs_start + capacity
            allocation[adventure_id] = permutation[ofs_start:ofs_end]
            ofs_start = ofs_end
        allocations.append(allocation)
    return allocations


def calc_allocations_scores(data, funghi_allocations):
    scores = []
    adventures = data['adventures']
    rewards = data['rewards']
    # Calculate score for each allocation
    for funghi_allocation in funghi_allocations:
        # Look through each adventure
        for adventure_id, adventure_allocation in funghi_allocation.items():
            score = 0.0
            allocated_funghis = gen_allocated_funghis(
                data, adventure_allocation)
            adventure = adventures[adventure_id]
            requirements = adventure['requirements']
            # Look through each requirement
            for requirement in requirements.values():
                augmented_funghis = gen_augmented_funghis(
                    requirement, allocated_funghis)
                requirement_met = is_non_reduce_requirement_met(
                    data, requirement, augmented_funghis) or \
                    is_reduce_requirement_met(
                        data, requirement, augmented_funghis)
                if requirement_met:
                    score += calc_weighted_score(rewards, requirement)
            scores.append(score)
    return scores


def gen_allocated_funghis(data, adventure_allocation):
    allocated_funghis = []
    funghis = data['funghis']
    for funghi_id in adventure_allocation:
        if funghi_id == EMPTY_ID:
            allocated_funghis.append(EMPTY_FUNGHI)
        else:
            allocated_funghis.append(funghis[funghi_id])
    return allocated_funghis


def is_non_reduce_requirement_met(data, requirement, augmented_funghis):
    # Generate permutations such that each stat is paired to a funghis
    req_stats = requirement['stats']
    is_met = False
    stats_permutations = itertools.permutations(
        augmented_funghis, len(req_stats))
    # Try each permutation
    for permutated_funghis in stats_permutations:
        # Specify each stat object to a funghi
        for req_stat_obj, funghi in zip(req_stats, permutated_funghis):
            funghi_stats = funghi['stats']
            # The funghi has to pass all the stats
            for stat_name, stat_value in req_stat_obj.items():
                if stat_name in funghi_stats and \
                        funghi_stats[stat_name] >= stat_value:
                    is_met = True
                else:
                    is_met = False
                    break
                # If any check fails, it should try the next permutation
            if not is_met:
                break
        # If any check succeeds, it should stop trying
        if is_met:
            break
    return is_met


def is_reduce_requirement_met(data, requirement, augmented_funghis):
    if not 'reduce_stats' in requirement:
        return False
    req_reduce_stats = requirement['reduce_stats']
    # Check each reduce stats
    for stat_name, reduce_target in req_reduce_stats.items():
        reduced_sum = 0
        # Calculate the reduced value from all funghis
        for funghi in augmented_funghis:
            funghi_stats = funghi['stats']
            if stat_name in funghi_stats:
                reduced_sum += funghi_stats[stat_name]
        # Check whether the reduced sum passes the requirement
        if reduced_sum < reduce_target:
            return False
    # All funghis have passed the reduce targets, the requirement is met
    return True


def gen_augmented_funghis(requirement, allocated_funghis):
    # Generate permutations such that each boost is paired to a funghis
    req_boosts = requirement['boosts']
    can_augment = False
    boost_permutations = itertools.permutations(
        allocated_funghis, len(req_boosts))
    # Try each permutation
    for permutated_funghis in boost_permutations:
        augmented_funghis = []
        # Specify each boost to a funghi
        for req_boost, funghi in zip(req_boosts, permutated_funghis):
            augmented_funghi = copy.deepcopy(funghi)
            funghi_skills = funghi['skills']
            # The funghi has to pass all the skills
            for skill_name, boost_stats in req_boost.items():
                if skill_name in funghi_skills and \
                        funghi_skills[skill_name] > 0:
                    augmented_funghi_stats = augmented_funghi['stats']
                    for boost_stat_name, boost_value in boost_stats.items():
                        augmented_funghi_stats[boost_stat_name] += boost_value
                    can_augment = True
                else:
                    can_augment = False
                    break
            # If any augmentation fails, it should try the next permutation
            if can_augment:
                augmented_funghis.append(augmented_funghi)
            else:
                break
        # If any augmentation succeeds, it should stop trying
        if can_augment:
            break
    if can_augment:
        return augmented_funghis
    else:
        return copy.deepcopy(allocated_funghis)


def calc_weighted_score(rewards, requirement):
    score = 0.0
    req_rewards = requirement['rewards']
    for req_reward_name, req_reward_value in req_rewards.items():
        if req_reward_name in rewards:
            score += rewards[req_reward_name] * req_reward_value
    return score


def main():
    data = load_data()
    normalize_data(data)
    total_adventure_capacity = calc_total_adventure_capacity(data)
    total_funghi_capacity = calc_total_funghi_capacity(data)
    funghi_permutations = gen_funghi_permutations(
        data, total_adventure_capacity, total_funghi_capacity)
    funghi_allocations = convert_permutations_to_allocations(
        data, funghi_permutations)
    scores = calc_allocations_scores(data, funghi_allocations)
    print(scores)


if __name__ == '__main__':
    main()
