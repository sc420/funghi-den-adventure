# Native modules
import os

# Third-party modules
import yaml

# Project modules
import allocation_calculator.calc as calc


ORDERED_DATA_DIRS = [
    'data/18-砂牆空洞-厚重通道',
    'data/15-清涼結冰洞-光滑通道',
    'data/12-樹根隧道-中途',
]


def load_data(data_dir):
    adventures_path = os.path.join(data_dir, 'adventures.yaml')
    funghis_path = os.path.join(data_dir, 'funghis.yaml')
    rewards_path = os.path.join(data_dir, 'rewards.yaml')
    with open(adventures_path, 'r', encoding='utf8') as stream:
        adventures = yaml.load(stream)
    with open(funghis_path, 'r', encoding='utf8') as stream:
        funghis = yaml.load(stream)
    with open(rewards_path, 'r', encoding='utf8') as stream:
        rewards = yaml.load(stream)
    return {
        'adventures': adventures,
        'funghis': funghis,
        'rewards': rewards,
    }


def filter_out_subset_funghis(data):
    adventures = data['adventures']
    funghis = data['funghis']
    adventure_capacity = calc.calc_total_adventure_capacity(data)
    funghi_capacity = calc.calc_total_funghi_capacity(data)
    remove = True
    while remove and funghi_capacity > adventure_capacity:
        remove = False
        for funghi_id in funghis:
            signature = gen_adventure_requirement_met_signature(
                data, funghi_id, adventures)
            for other_funghi_id in funghis:
                if other_funghi_id == funghi_id:
                    continue
                other_signature = gen_adventure_requirement_met_signature(
                    data, other_funghi_id, adventures)
                if check_super_signature(signature, other_signature) and \
                        check_super_stats(funghis, funghi_id, other_funghi_id):
                    remove = True
                    break
            if remove:
                del funghis[funghi_id]
                funghi_capacity -= 1
                break


def gen_adventure_requirement_met_signature(data, funghi_id, adventures):
    signature = {}
    adventure_allocation = [funghi_id]
    for adventure_id, adventure in adventures.items():
        met_list = []
        allocated_funghis = calc.gen_allocated_funghis(
            data, adventure_allocation)
        requirements = adventure['requirements']
        # Look through each requirement
        for requirement in requirements.values():
            augmented_funghis = calc.gen_augmented_funghis(
                requirement, allocated_funghis)
            is_met = calc.is_requirement_met(requirement, augmented_funghis)
            met_list.append(is_met)
        signature[adventure_id] = met_list
    return signature


def check_super_stats(funghis, funghi_id, super_funghi_id):
    stats = funghis[funghi_id]['stats']
    super_stats = funghis[super_funghi_id]['stats']
    for stat_name, stat_value in stats.items():
        if stat_name in super_stats:
            if stat_value > super_stats[stat_name]:
                return False
    return True


def check_super_signature(sig, super_sig):
    for met_list, super_met_list in zip(sig.values(), super_sig.values()):
        for met, super_met in zip(met_list, super_met_list):
            if met and not super_met:
                return False
    return True


def filter_out_chosen_funghis(data, chosen_funghis):
    funghis = data['funghis']
    for chosen_funghi in chosen_funghis:
        funghis.pop(chosen_funghi, None)


def keep_first_best_result(best_results):
    rate_and_combinations = best_results['rate_and_combinations']
    rate_and_combinations = [rate_and_combinations[0]]
    best_results['rate_and_combinations'] = rate_and_combinations


def add_best_results_to_chosen_funghis(best_results, chosen_funghis):
    rate_and_combinations = best_results['rate_and_combinations']
    combination = rate_and_combinations[0][1]
    funghis = list(combination.values())
    chosen_funghis.extend(funghis[0])


def main():
    chosen_funghis = []
    for idx, data_dir in enumerate(ORDERED_DATA_DIRS):
        data = load_data(data_dir)
        calc.normalize_data(data)
        filter_out_chosen_funghis(data, chosen_funghis)
        filter_out_subset_funghis(data)
        total_adventure_capacity = calc.calc_total_adventure_capacity(data)
        total_funghi_capacity = calc.calc_total_funghi_capacity(data)
        funghi_combinations = calc.gen_funghi_combinations(
            data, total_adventure_capacity, total_funghi_capacity)
        results = calc.calc_allocations_results(data, funghi_combinations)
        funghi_combinations = calc.gen_funghi_combinations(
            data, total_adventure_capacity, total_funghi_capacity)
        best_results = calc.filter_best_results(funghi_combinations, results)
        keep_first_best_result(best_results)
        add_best_results_to_chosen_funghis(best_results, chosen_funghis)
        print('#{} {}'.format(idx + 1, data_dir))
        calc.list_best_allocations(data, best_results)


if __name__ == '__main__':
    main()
