# Native modules
import argparse
import os
import sys

# Third-party modules
import yaml

# Project modules
import allocation_calculator.calc as calc
import allocation_calculator.program_args as p_args


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', default=None,
                        help='data directory containing adventures, funghis'
                        ' and rewards spec files')
    parser.add_argument('--adventures_path', default=None,
                        help='adventures spec path')
    parser.add_argument('--funghis_path', default=None,
                        help='funghis spec path')
    parser.add_argument('--rewards_path', default=None,
                        help='rewards spec path')
    parser.add_argument(
        '--max', type=int, default=10, help='the maximum number of allocations'
        ' (set 0 to be unlimited)')
    # Report score
    parser.add_argument('--report_score', dest='report_score',
                        action='store_true', help='report score')
    parser.add_argument('--no_report_score', dest='report_score',
                        action='store_false', help='do not report score')
    parser.set_defaults(report_score=True)
    # Report success rate
    parser.add_argument('--report_success_rate', dest='report_success_rate',
                        action='store_true', help='report success rate')
    parser.add_argument('--no_report_success_rate', dest='report_success_rate',
                        action='store_false', help='do not report success rate')
    parser.set_defaults(report_success_rate=True)
    # Report failed requirement
    parser.add_argument('--report_failed_requirement',
                        dest='report_failed_requirement', action='store_true',
                        help='report failed requirement')
    parser.add_argument('--no_report_failed_requirement',
                        dest='report_failed_requirement', action='store_false',
                        help='do not report failed requirement')
    parser.set_defaults(report_failed_requirement=True)
    # One switch to turn off all additional reports
    parser.add_argument('--no_additional', default=False, action='store_true',
                        help='do not report any additional information')
    args = parser.parse_args()
    p_args.gen_spec_paths(args)
    if args.no_additional:
        args.report_score = False
        args.report_success_rate = False
        args.report_failed_requirement = False
    return args


def load_data(args):
    with open(args.adventures_path, 'r', encoding='utf8') as stream:
        adventures = yaml.load(stream)
    with open(args.funghis_path, 'r', encoding='utf8') as stream:
        funghis = yaml.load(stream)
    with open(args.rewards_path, 'r', encoding='utf8') as stream:
        rewards = yaml.load(stream)
    return {
        'adventures': adventures,
        'funghis': funghis,
        'rewards': rewards,
    }


def limit_best_results(best_results, max_results):
    if max_results <= 0:
        return
    results = best_results['results']
    if len(results) > max_results:
        best_results['results'] = results[:max_results]
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
    best_results = calc.filter_best_results(data, funghi_combinations, results)
    limited = limit_best_results(best_results, args.max)
    calc.list_best_allocations(data, best_results, args.report_score,
                               args.report_success_rate,
                               args.report_failed_requirement)
    if limited:
        print('The limit has been reached')


if __name__ == '__main__':
    main()
