# Native modules
import os

# Third-party modules
import yaml

# Project modules
import allocation_calculator.calc as calc


# Select more difficult adventures first
ORDERED_DATA_DIRS = [
    'data/18-砂牆空洞-厚重通道',
    'data/15-清涼結冰洞-光滑通道',
    'data/12-樹根隧道-中途',
]
# Read only one funghis spec
FUNGHI_PATH = 'data/all/funghis.yaml'
# Limit the number of global allocations (set to 0 to ignore)
GLOBAL_ALLOCATIONS_LIMIT = 0


def gen_all_best_results():
    allocated_counts = {}
    data_dir_idx = 0
    first_results = gen_single_best_results(data_dir_idx, allocated_counts)
    before_results = [first_results]
    before_pointers = [0]
    while data_dir_idx >= 0:
        # Check whether to generate new best results
        if data_dir_idx >= len(before_pointers):
            results = gen_single_best_results(data_dir_idx, allocated_counts)
            before_results.append(results)
            before_pointers.append(0)
            # Check whether to yield the output
            if len(before_pointers) >= len(ORDERED_DATA_DIRS):
                output = []
                for results, pointer in zip(before_results, before_pointers):
                    max_score = results['max_score']
                    rate_and_combinations = results['rate_and_combinations']
                    selected = [rate_and_combinations[pointer]]
                    output.append({
                        'max_score': max_score,
                        'rate_and_combinations': selected,
                    })
                yield output
                before_results.pop()
                before_pointers.pop()
                data_dir_idx -= 1
                before_pointers[data_dir_idx] += 1
        else:
            # Get the last best results
            best_results = before_results[data_dir_idx]
            rate_and_combinations = best_results['rate_and_combinations']
            # Get the pointer to the last best results
            pointer = before_pointers[data_dir_idx]
            # Check whether to remove the allocated counts added from the
            # previous round
            if pointer > 0:
                prev_combination = rate_and_combinations[pointer - 1][1]
                remove_combination_from_allocated_counts(
                    prev_combination, allocated_counts)
            # Check whether the pointer has reached the end
            if pointer >= len(rate_and_combinations):
                before_results.pop()
                before_pointers.pop()
                data_dir_idx -= 1
                if data_dir_idx >= 0:
                    before_pointers[data_dir_idx] += 1
            else:
                combination = rate_and_combinations[pointer][1]
                add_combination_to_allocated_counts(
                    combination, allocated_counts)
                data_dir_idx += 1


def gen_single_best_results(data_dir_idx, allocated_counts):
    data_dir = ORDERED_DATA_DIRS[data_dir_idx]
    data = load_data(data_dir)
    calc.normalize_data(data)
    filter_out_allocated_funghis(data, allocated_counts)
    filter_out_subset_funghis(data)
    total_adventure_capacity = calc.calc_total_adventure_capacity(data)
    total_funghi_capacity = calc.calc_total_funghi_capacity(data)
    funghi_combinations = calc.gen_funghi_combinations(
        data, total_adventure_capacity, total_funghi_capacity)
    results = calc.calc_allocations_results(data, funghi_combinations)
    funghi_combinations = calc.gen_funghi_combinations(
        data, total_adventure_capacity, total_funghi_capacity)
    return calc.filter_best_results(funghi_combinations, results)


def load_data(data_dir):
    adventures_path = os.path.join(data_dir, 'adventures.yaml')
    funghis_path = FUNGHI_PATH
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


def filter_out_allocated_funghis(data, allocated_counts):
    funghis = data['funghis']
    for funghi_id, count in allocated_counts.items():
        funghis[funghi_id]['capacity'] -= count
        if funghis[funghi_id]['capacity'] <= 0:
            del funghis[funghi_id]


def filter_out_subset_funghis(data):
    adventures = data['adventures']
    funghis = data['funghis']
    adventure_capacity = calc.calc_total_adventure_capacity(data)
    funghi_capacity = calc.calc_total_funghi_capacity(data)
    remove = True
    # We need to have enough funghis for all adventures
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


def remove_combination_from_allocated_counts(combination, allocated_counts):
    for funghis in combination.values():
        for funghi in funghis:
            allocated_counts[funghi] -= 1
            if allocated_counts[funghi] <= 0:
                del allocated_counts[funghi]


def add_combination_to_allocated_counts(combination, allocated_counts):
    for funghis in combination.values():
        for funghi in funghis:
            if funghi in allocated_counts:
                allocated_counts[funghi] += 1
            else:
                allocated_counts[funghi] = 1


def main():
    data_list = [load_data(data_dir) for data_dir in ORDERED_DATA_DIRS]
    print('All global allocations:')
    for idx, all_results in enumerate(gen_all_best_results()):
        print('Global Allocation #{}'.format(idx + 1))
        print()
        for data, results in zip(data_list, all_results):
            calc.list_best_allocations(data, results)
        print('-----')
        # Check the limit
        if GLOBAL_ALLOCATIONS_LIMIT > 0 and idx + 1 >= GLOBAL_ALLOCATIONS_LIMIT:
            print('The limit has been reached')
            break


if __name__ == '__main__':
    main()
