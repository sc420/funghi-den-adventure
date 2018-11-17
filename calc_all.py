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
    parser.add_argument('--max', type=int, default=1,
                        help='the maximum number of global allocations'
                        ' (set 0 to be unlimited)')
    args = parser.parse_args()
    args.data_dirs = args.data_dirs.split(',')
    return args


def gen_all_best_results(args):
    allocated_counts = {}
    data_dir_idx = 0
    first_results = gen_single_best_results(
        args, data_dir_idx, allocated_counts)
    before_results = [first_results]
    before_pointers = [0]
    while data_dir_idx >= 0:
        # Check whether to generate new best results
        if data_dir_idx >= len(before_pointers):
            results = gen_single_best_results(
                args, data_dir_idx, allocated_counts)
            before_results.append(results)
            before_pointers.append(0)
            # Check whether to yield the output
            if len(before_pointers) >= len(args.data_dirs):
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


def gen_single_best_results(args, data_dir_idx, allocated_counts):
    data_dir = args.data_dirs[data_dir_idx]
    data = load_data(data_dir, args.funghis_path)
    filter_out_allocated_funghis(data, allocated_counts)
    calc.normalize_data(data)
    calc.filter_out_subset_funghis(data)
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


def filter_out_allocated_funghis(data, allocated_counts):
    funghis = data['funghis']
    for funghi_id, count in allocated_counts.items():
        funghis[funghi_id]['capacity'] -= count
        if funghis[funghi_id]['capacity'] <= 0:
            del funghis[funghi_id]


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
    args = parse_args()
    data_list = [load_data(data_dir, args.funghis_path)
                 for data_dir in args.data_dirs]
    print('All global allocations:')
    has_global = False
    for idx, all_results in enumerate(gen_all_best_results(args)):
        print('Global Allocation #{}'.format(idx + 1))
        print()
        for data, results in zip(data_list, all_results):
            calc.list_best_allocations(data, results)
        print('-----')
        has_global = True
        # Check the limit
        if args.max > 0 and idx + 1 >= args.max:
            print('The limit has been reached')
            break
    if not has_global:
        print('There are no global allocations')


if __name__ == '__main__':
    main()
