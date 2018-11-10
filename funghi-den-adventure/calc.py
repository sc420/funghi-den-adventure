import itertools
import yaml

# STAT_NAMES = ['vitality', 'intelligence', 'speed']
# SKILL_NAMES = ['luck', 'insensitive', 'horn', 'agile', 'night_eyes', 'stealth',
#                'cute', 'food', 'swimmer', 'big_eater', 'short_range_attack',
#                'submerge', 'flight', 'luminescent', 'cold_resist', 'hard_head',
#                'photosynthesis', 'weaponry', 'motivated', 'long_range_attack',
#                'poison', 'courage', 'smart', 'iron_fist', 'sensor']
# SPEC = {
#     'stats': STAT_NAMES,
#     'skills': SKILL_NAMES,
#     'boosts': SKILL_NAMES,
# }
# REQUIRED_SPEC_NAMES = ['stats', 'skills', 'boosts']

REQUIRED_ADVENTURE_SPEC_NAMES = ['stats', 'skills', 'boosts']
REQUIRED_FUNGHI_SPEC_NAMES = ['stats', 'skills']
CHECK_QUALIFICATION_SPEC_NAMES = ['stats', 'skills']


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


def filter_qualified_funghis(data):
    qualified_funghis = {}
    adventures = data['adventures']
    funghis = data['funghis']
    for adventure_id, adventure in adventures.items():
        requirements = adventure['requirements']
        per_adventure = {}
        for requirement_id, requirement in requirements.items():
            per_adventure[requirement_id] = []
            for funghi_id, funghi in funghis.items():
                if is_funghi_qualified_for_requirement(funghi, requirement):
                    per_adventure[requirement_id].append(funghi_id)
        qualified_funghis[adventure_id] = per_adventure
    return qualified_funghis


def is_funghi_qualified_for_requirement(funghi, requirement):
    # If the funghi is not available, it is not qualified
    if funghi['capacity'] <= 0:
        return False
    # Check the stats and skills
    for spec_name in CHECK_QUALIFICATION_SPEC_NAMES:
        funghi_spec = funghi[spec_name]
        req_spec = requirement[spec_name]
        for req_obj in req_spec:
            for name, value in req_obj.items():
                # If the funghi has no corresponding second-level spec name, it
                # is not qualified
                if not name in funghi_spec:
                    return False
                # If the value is a list, ignore it
                if not isinstance(value, list):
                    # If the requirement value is higher than the funghi value,
                    # it is not qualified
                    if value > funghi_spec[name]:
                        return False
    # The test has passed, the funghi is qualified
    return True


def calc_total_adventure_capacities(data):
    count = 0
    adventures = data['adventures']
    for adventure in adventures.values():
        count += adventure['capacity']
    return count


def gen_funghi_permutations(data, total_capacity):
    candidates = []
    funghis = data['funghis']
    for funghi_id, funghi in funghis.items():
        fungi_repeated_ids = itertools.repeat(funghi_id, funghi['capacity'])
        candidates.append(*list(fungi_repeated_ids))
    return itertools.permutations(candidates, total_capacity)


def calc_funghi_permutations_scores(data, funghi_permutations, qualified_funghis):
    for permutation in funghi_permutations:
        print(permutation)


def main():
    data = load_data()
    normalize_data(data)
    qualified_funghis = filter_qualified_funghis(data)
    total_capacity = calc_total_adventure_capacities(data)
    funghi_permutations = gen_funghi_permutations(data, total_capacity)
    calc_funghi_permutations_scores(
        data, funghi_permutations, qualified_funghis)


if __name__ == '__main__':
    main()
