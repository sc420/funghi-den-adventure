# Native modules
import argparse
import os

# Third-party modules
import yaml

# Project modules
import allocation_calculator.calc as calc


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--data_dirs', help='data directories separated by commas')
    parser.add_argument('--funghis_path', help='funghis spec path')
    parser.add_argument('--max', type=int, default=10,
                        help='the maximum number of allocations'
                        ' (set 0 to be unlimited)')
    args = parser.parse_args()
    args.data_dirs = args.data_dirs.split(',')
    return args


def gen_compatible_best_results(args):
    # Load all data
    all_data = load_all_data(args)
    # Set the intersected allowed funghis to each adventure
    intersected_allowed_funghis = gen_intersected_allowed_funghis(all_data)
    set_intersected_allowed_funghis(all_data, intersected_allowed_funghis)
    # Get adventure capacities
    adventure_capacities = get_adventure_capacities(all_data)
    # Generate compatible combinations
    compatible_combinations = None
    for data, adventure_capacity in zip(all_data, adventure_capacities):
        results = gen_single_best_results(data)
        combinations_set = convert_to_combinations_set(results)
        if compatible_combinations is None:
            compatible_combinations = combinations_set
        else:
            compatible_combinations = gen_compatible_combinations(
                compatible_combinations, combinations_set, adventure_capacity)
        if len(compatible_combinations) <= 0:
            break
    return compatible_combinations


def load_all_data(args):
    return [load_data(data_dir, args.funghis_path)
            for data_dir in args.data_dirs]


def gen_intersected_allowed_funghis(all_data):
    intersected_funghis = None
    for data in all_data:
        adventures = data['adventures']
        if 'allowed_funghis' in adventures:
            allowed_funghis = set(adventures['allowed_funghis'])
            if allowed_funghis is None:
                intersected_funghis = allowed_funghis
            else:
                intersected_funghis = intersected_funghis.intersection(
                    allowed_funghis)
    return intersected_funghis


def set_intersected_allowed_funghis(all_data, intersected_allowed_funghis):
    if intersected_allowed_funghis is None:
        return
    for data in all_data:
        adventures = data['adventures']
        adventures['allowed_funghis'] = intersected_allowed_funghis


def get_adventure_capacities(all_data):
    capacities = []
    for data in all_data:
        adventures = data['adventures']
        if len(adventures) > 1:
            raise ValueError('The number of adventures should be 1')
        first_adventure = next(iter(adventures.values()))
        capacity = first_adventure['capacity']
        capacities.append(capacity)
    return capacities


def gen_single_best_results(data):
    calc.normalize_data(data)
    total_adventure_capacity = calc.calc_total_adventure_capacity(data)
    total_funghi_capacity = calc.calc_total_funghi_capacity(data)
    funghi_combinations = calc.gen_funghi_combinations(
        data, total_adventure_capacity, total_funghi_capacity)
    results = calc.calc_allocations_results(data, funghi_combinations)
    funghi_combinations = calc.gen_funghi_combinations(
        data, total_adventure_capacity, total_funghi_capacity)
    return calc.filter_best_results(funghi_combinations, results)


def load_data(data_dir, funghis_path):
    adventures_path = os.path.join(data_dir, 'adventures.yaml')
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


def convert_to_combinations_set(best_results):
    rate_and_combinations = best_results['rate_and_combinations']
    combinations = []
    for rate_and_combination in rate_and_combinations:
        combination = rate_and_combination[1]
        funghis = next(iter(combination.values()))
        combinations.append(set(funghis))
    return combinations


def gen_compatible_combinations(combinations, new_combinations,
                                new_capacity):
    # Check whether the current combinations is empty
    if len(combinations) <= 0:
        return new_combinations
    compatible_combinations = []
    first_combination = next(iter(combinations))
    cur_capacity = len(first_combination)
    # Check whether the current capacity is larger
    if cur_capacity > new_capacity:
        # Check whether any combination is a subset of each current combination
        # If so, the current combination is compatible with the new combination
        for combination in combinations:
            for new_combination in new_combinations:
                if new_combination.issubset(combination):
                    compatible_combinations.append(combination)
                    break
    else:
        # Check whether any new combination is a subset of each new combination
        # If so, the new combination is compatible with the current combination
        for new_combination in new_combinations:
            for combination in combinations:
                if combination.issubset(new_combination):
                    compatible_combinations.append(new_combination)
                    break
    return compatible_combinations


def main():
    args = parse_args()
    data_list = [load_data(data_dir, args.funghis_path)
                 for data_dir in args.data_dirs]
    funghis = data_list[0]['funghis']
    print('All compatible allocations:')
    has_compatible = False
    for idx, combinations in enumerate(gen_compatible_best_results(args)):
        print('#{}'.format(idx + 1))
        funghi_names = [funghis[funghi_id]['name']
                        for funghi_id in sorted(combinations)]
        print(', '.join(funghi_names))
        print()
        has_compatible = True
        # Check the limit
        if args.max > 0 and idx + 1 >= args.max:
            print('The limit has been reached')
            break
    if not has_compatible:
        print('There are no compatible allocations')


if __name__ == '__main__':
    main()
