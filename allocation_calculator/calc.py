import copy
import itertools

REQUIRED_ADVENTURE_SPEC_NAMES = ['stats', 'skills']
REQUIRED_FUNGHI_SPEC_NAMES = ['stats', 'skills']
EMPTY_ID = -1
EMPTY_FUNGHI = {
    'capacity': 0,
    'name': '<EMPTY>',
    'stats': [],
    'skills': [],
}


def normalize_data(data):
    normalize_adventures(data['adventures'])
    normalize_funghis(data['funghis'])


def normalize_adventures(adventures):
    for adventure in adventures.values():
        requirements = adventure['requirements']
        for requirement in requirements.values():
            for spec_name in REQUIRED_ADVENTURE_SPEC_NAMES:
                if spec_name not in requirement:
                    requirement[spec_name] = []


def normalize_funghis(funghis):
    for funghi in funghis.values():
        for spec_name in REQUIRED_FUNGHI_SPEC_NAMES:
            if spec_name not in funghi:
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


def gen_funghi_combinations(data, adventure_capacity, funghi_capacity):
    """Generate funghi combinations.

    For example, if the funghis are (1, 2, 3, 4) and the adventure capacities
    are (1, 2), then the combinations will be [((1), (2, 3)), ((1), (2, 4)),
    ((1), (3, 4)), ((2), (1, 3)), ((2), (1, 4)), ((2), (3, 4)), ...,
    ((4), (1, 2)), ((4), (1, 3)), ((4), (2, 3))]
    Empty funghis will be generated if there are not enough funghis for
    allocations.
    """
    candidates = []
    # Generate funghi candidates
    funghis = data['funghis']
    for funghi_id, funghi in funghis.items():
        fungi_repeated_ids = itertools.repeat(funghi_id, funghi['capacity'])
        candidates.extend(list(fungi_repeated_ids))
    # If there are not enough funghis, generate negative IDs as empty funghis
    # TODO: It would fail if there are multiple funghis
    if funghi_capacity < adventure_capacity:
        empty_size = adventure_capacity - funghi_capacity
        for i in range(-1, -1 * (empty_size + 1), -1):
            candidates.append(i)
    # Generate combinations of funghis in each adventure, then proceed with the
    # remaining unused funghis
    adventures = data['adventures']
    adventures_keys = list(adventures)
    adventures_values = list(adventures.values())
    generators = []
    candidates_list = []
    remaining_list = []
    # Add the generator for the first adventure
    first_adventure = adventures_values[0]
    local_capacity = first_adventure['capacity']
    local_comb = itertools.combinations(candidates, local_capacity)
    generators.append(local_comb)
    # Add dummy candidates
    candidates_list.append([])
    # Add the original candidates in the remaining list
    remaining_list.append(set(candidates))
    # Generate combinations
    while len(generators) > 0:
        next_idx = len(generators)
        local_candidates = next(generators[-1], None)
        if local_candidates is None:
            generators.pop()
            candidates_list.pop()
            remaining_list.pop()
        else:
            candidates_list.append(local_candidates)
            remaining_candidates = remaining_list[next_idx - 1] - \
                set(local_candidates)
            if len(remaining_candidates) == 0 or \
                    next_idx >= len(adventures_values):
                output = {}
                for adventure_id, candidates_item in \
                        zip(adventures_keys, candidates_list[1:]):
                    output[adventure_id] = candidates_item
                yield output
                candidates_list.pop()
            else:
                # Add next generator
                next_adventure = adventures_values[next_idx]
                local_capacity = next_adventure['capacity']
                sorted_remaining_candidates = sorted(remaining_candidates)
                local_comb = itertools.combinations(
                    sorted_remaining_candidates, local_capacity)
                generators.append(local_comb)
                # Add next remaining candidates
                remaining_list.append(remaining_candidates)


def calc_allocations_results(data, funghi_combinations):
    results = []
    adventures = data['adventures']
    rewards = data['rewards']
    # Calculate score for each allocation
    for funghi_combination in funghi_combinations:
        score = 0.0
        success_count = 0
        requirement_count = 0
        # Look through each adventure
        for adventure_id, adventure_allocation in funghi_combination.items():
            # If an empty funghi is in the allocation, the adventure fails
            if EMPTY_ID in adventure_allocation:
                continue
            allocated_funghis = gen_allocated_funghis(
                data, adventure_allocation)
            adventure = adventures[adventure_id]
            requirements = adventure['requirements']
            # Look through each requirement
            all_requirements_met = True
            for requirement in requirements.values():
                augmented_funghis = gen_augmented_funghis(
                    requirement, allocated_funghis)
                requirement_met = is_non_reduce_requirement_met(
                    data, requirement, augmented_funghis, 'stats') and \
                    is_non_reduce_requirement_met(
                    data, requirement, augmented_funghis, 'skills') and \
                    is_reduce_requirement_met(
                        data, requirement, augmented_funghis)
                if requirement_met:
                    req_rewards = requirement['rewards']
                    score += calc_weighted_score(rewards, req_rewards)
                    success_count += 1
                else:
                    all_requirements_met = False
                requirement_count += 1
            # Add score of perfect reward if all requirements are met
            if all_requirements_met:
                req_rewards = adventure['perfect_rewards']
                score += calc_weighted_score(rewards, req_rewards)
        results.append({
            'score': score,
            'success_count': success_count,
            'requirement_count': requirement_count,
        })
    return results


def gen_allocated_funghis(data, adventure_allocation):
    allocated_funghis = []
    funghis = data['funghis']
    for funghi_id in adventure_allocation:
        if funghi_id == EMPTY_ID:
            allocated_funghis.append(EMPTY_FUNGHI)
        else:
            allocated_funghis.append(funghis[funghi_id])
    return allocated_funghis


def is_non_reduce_requirement_met(data, requirement, augmented_funghis, spec):
    # Generate permutations such that each spec is paired to a funghis
    req_specs = requirement[spec]
    is_met = True
    specs_permutations = itertools.permutations(
        augmented_funghis, len(req_specs))
    # Try each permutation
    for permutated_funghis in specs_permutations:
        # Specify each spec object to a funghi
        for req_spec_obj, funghi in zip(req_specs, permutated_funghis):
            funghi_specs = funghi[spec]
            # The funghi has to pass all the specs
            for spec_name, spec_value in req_spec_obj.items():
                if spec_name in funghi_specs and \
                        funghi_specs[spec_name] >= spec_value:
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
    if 'reduce_stats' not in requirement:
        return True
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
    augmented_funghis = gen_augmented_funghis_logic(
        requirement, allocated_funghis, False)
    return gen_augmented_funghis_logic(
        requirement, augmented_funghis, True)


def gen_augmented_funghis_logic(requirement, allocated_funghis, is_reduce):
    augmented_funghis = []
    if is_reduce:
        if 'reduce_boosts' in requirement:
            req_boosts = requirement['reduce_boosts']
        else:
            return allocated_funghis
    else:
        if 'boosts' in requirement:
            req_boosts = requirement['boosts']
        else:
            return allocated_funghis
    # Check each funghi to see if it can be augmented
    for funghi in allocated_funghis:
        final_augmented_funghi = copy.deepcopy(funghi)
        # Check each boost
        for req_boost in req_boosts:
            augmented_funghi = None
            funghi_skills = funghi['skills']
            # The funghi has to pass all the skills
            for skill_name, boost_stats in req_boost.items():
                if skill_name in funghi_skills and \
                        funghi_skills[skill_name] > 0:
                    if augmented_funghi is None:
                        augmented_funghi = copy.deepcopy(
                            final_augmented_funghi)
                    augmented_funghi_stats = augmented_funghi['stats']
                    for boost_stat_name, boost_value in boost_stats.items():
                        augmented_funghi_stats[boost_stat_name] += boost_value
                else:
                    # If the funghi fails any skill, the augmented funghi
                    # should be discarded
                    augmented_funghi = None
                    # if it is in reduce mode, it should return the original
                    # funghis, otherwise, we should try the next boost
                    if is_reduce:
                        return allocated_funghis
                    else:
                        break
            # Check whether to save the final augmented funghi
            if augmented_funghi is not None:
                final_augmented_funghi = augmented_funghi
        # Add the augmented funghi
        augmented_funghis.append(final_augmented_funghi)
    return augmented_funghis


def calc_weighted_score(rewards, req_rewards):
    score = 0.0
    for req_reward_name, req_reward_value in req_rewards.items():
        if req_reward_name in rewards:
            score += rewards[req_reward_name] * req_reward_value
    return score


def list_best_allocations(data, funghi_combinations, results):
    scores = [result['score'] for result in results]
    max_score = max(scores)
    # Print the max score
    print('Max score: {}'.format(max_score))
    # List all allocations of the max score
    print('Best allocations:')
    idx = 0
    for funghi_combination, result in zip(funghi_combinations, results):
        score = result['score']
        success_count = result['success_count']
        requirement_count = result['requirement_count']
        if requirement_count > 0:
            success_rate = success_count / requirement_count * 100.0
        else:
            success_rate = 0.0
        if score >= max_score:
            print('#{}'.format(idx + 1))
            print('Success rate: {:.2f}%'.format(success_rate))
            print_best_allocation(data, funghi_combination)
            print()
            idx += 1


def print_best_allocation(data, funghi_combination):
    adventures = data['adventures']
    funghis = data['funghis']
    for adventure_id, adventure_allocation in funghi_combination.items():
        adventure = adventures[adventure_id]
        funghi_names = []
        for funghi_id in adventure_allocation:
            if funghi_id == EMPTY_ID:
                funghi_names.append(EMPTY_FUNGHI['name'])
            else:
                funghi = funghis[funghi_id]
                funghi_names.append(funghi['name'])
        print('{}: {}'.format(adventure['name'], ', '.join(funghi_names)))
