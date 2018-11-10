import yaml


SPECS = ['stats', 'skills']


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
            for spec in SPECS:
                if not spec in requirement:
                    requirement[spec] = []


def normalize_funghis(funghis):
    for funghi in funghis.values():
        for spec in SPECS:
            if not spec in funghi:
                funghi[spec] = []


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
    # Check whether there is any funghi available
    if funghi['count'] <= 0:
        return False
    # Check the stats and skills
    for spec in SPECS:
        funghi_abilities = funghi[spec]
        req_abilities = requirement[spec]
        for req_obj in req_abilities:
            for name, value in req_obj.items():
                if value > funghi_abilities[name]:
                    return False
    # The test has passed, the funghi is qualified
    return True


def main():
    data = load_data()
    normalize_data(data)
    qualified_funghis = filter_qualified_funghis(data)
    print(qualified_funghis)


if __name__ == '__main__':
    main()
