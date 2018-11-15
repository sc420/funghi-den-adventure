# Native modules
import argparse
import os

# Third-party modules
import yaml

# Project modules
import allocation_calculator.calc as calc


# Limit the number of allocations (set to 0 to ignore)
ALLOCATIONS_LIMIT = 10


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', help='data directory')
    return parser.parse_args()


def load_data(args):
    adventures_path = os.path.join(args.data_dir, 'adventures.yaml')
    funghis_path = os.path.join(args.data_dir, 'funghis.yaml')
    rewards_path = os.path.join(args.data_dir, 'rewards.yaml')
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


def limit_best_results(best_results):
    if ALLOCATIONS_LIMIT <= 0:
        return
    rate_and_combinations = best_results['rate_and_combinations']
    if len(rate_and_combinations) > ALLOCATIONS_LIMIT:
        rate_and_combinations = rate_and_combinations[:ALLOCATIONS_LIMIT]
        best_results['rate_and_combinations'] = rate_and_combinations
        return True
    else:
        return False


def main():
    args = parse_args()
    data = load_data(args)
    calc.normalize_data(data)
    total_adventure_capacity = calc.calc_total_adventure_capacity(data)
    total_funghi_capacity = calc.calc_total_funghi_capacity(data)
    funghi_combinations = calc.gen_funghi_combinations(
        data, total_adventure_capacity, total_funghi_capacity)
    results = calc.calc_allocations_results(data, funghi_combinations)
    funghi_combinations = calc.gen_funghi_combinations(
        data, total_adventure_capacity, total_funghi_capacity)
    best_results = calc.filter_best_results(funghi_combinations, results)
    limited = limit_best_results(best_results)
    calc.list_best_allocations(data, best_results)
    if limited:
        print('The limit has been reached')


if __name__ == '__main__':
    main()
