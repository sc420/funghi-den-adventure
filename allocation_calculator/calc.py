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


def filter_out_subset_funghis(data):
    adventures = data['adventures']
    funghis = data['funghis']
    adventure_capacity = calc_total_adventure_capacity(data)
    funghi_capacity = calc_total_funghi_capacity(data)
    remove = True
    # We need to have enough funghis for all adventures
    while remove and funghi_capacity > adventure_capacity:
        remove = False
        # Try each base funghi
        for funghi_id in funghis:
            signature = gen_adventure_requirement_met_signature(
                data, funghi_id, adventures)
            # For each other funghi, check whether the passing requirement list
            # is a superset of the base funghi
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
        allocated_funghis = gen_allocated_funghis(
            data, adventure_allocation)
        requirements = adventure['requirements']
        # Look through each requirement
        for requirement in requirements.values():
            augmented_funghis = gen_augmented_funghis(
                requirement, allocated_funghis)
            is_met = is_requirement_met(requirement, augmented_funghis)
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

    Empty funghis will be generated if there are not enough funghis for
    allocations.
    """
    candidates = []
    # Generate funghi candidates
    funghis = data['funghis']
    for funghi_id, funghi in funghis.items():
        for funghi_idx in range(funghi['capacity']):
            candidates.append((funghi_id, funghi_idx))
    # If there are not enough funghis, generate negative IDs as empty funghis
    if funghi_capacity < adventure_capacity:
        empty_size = adventure_capacity - funghi_capacity
        for empty_idx in range(empty_size):
            candidates.append((EMPTY_ID, empty_idx))
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
    local_comb = gen_combinations_primary_jumpy(candidates, local_capacity)
    generators.append(local_comb)
    # Add dummy candidates
    candidates_list.append([])
    # Add the original candidates in the remaining list
    remaining_list.append(set(candidates))
    # Generate combinations
    while len(generators) > 0:
        next_idx = len(generators)
        adventure = adventures_values[next_idx - 1]
        local_candidates = next(generators[-1], None)
        # Check whether the local candidates are in the allowed list
        while not check_allowed_funghis(adventure, local_candidates):
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
                    output[adventure_id] = [pair[0]
                                            for pair in candidates_item]
                yield output
                candidates_list.pop()
            else:
                # Add next generator
                next_adventure = adventures_values[next_idx]
                local_capacity = next_adventure['capacity']
                sorted_remaining_candidates = sorted(remaining_candidates)
                local_comb = gen_combinations_primary_jumpy(
                    sorted_remaining_candidates, local_capacity)
                generators.append(local_comb)
                # Add next remaining candidates
                remaining_list.append(remaining_candidates)


def gen_combinations_primary_jumpy(candidates, n):
    candidate_size = len(candidates)
    # Create pointers
    pointers = list(range(n))
    # If the index is negative, the pointer can not move anymore, so that we can
    # stop the generation
    idx = 0
    while idx >= 0:
        # Output the combination
        output = []
        for idx in range(n):
            pointer = pointers[idx]
            output.append(candidates[pointer])
        yield output
        # Go to the next pointer combination
        idx = n - 1
        while idx >= 0:
            # Find the new pointer with a different primary number
            pointer = pointers[idx]
            prev_primary_num = candidates[pointer][0]
            can_move_pointer = False
            for new_pointer in range(pointer + 1, candidate_size):
                if candidates[new_pointer][0] != prev_primary_num:
                    pointers[idx] = new_pointer
                    can_move_pointer = True
                    break
            if can_move_pointer:
                # Set the following pointers to be one position behind the
                # previous one
                for following_idx in range(idx + 1, n):
                    pointers[following_idx] = pointers[following_idx - 1] + 1
                # If the last pointer is invalid, try to move the previous
                # pointer in the next loop
                if pointers[-1] >= candidate_size:
                    idx -= 1
                else:
                    break
            else:
                # Try to move the previous pointer in the next loop
                idx -= 1


def check_allowed_funghis(adventure, candidates):
    if 'allowed_funghis' not in adventure:
        return True
    if candidates is None:
        return True
    allowed_funghis = adventure['allowed_funghis']
    for candidate in candidates:
        if candidate[0] not in allowed_funghis:
            return False
    return True


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
                if is_requirement_met(requirement, augmented_funghis):
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


def is_requirement_met(requirement, augmented_funghis):
    return is_non_reduce_requirement_met(
        requirement, augmented_funghis, 'stats') and \
        is_non_reduce_requirement_met(
        requirement, augmented_funghis, 'skills') and \
        is_reduce_requirement_met(requirement, augmented_funghis)


def is_non_reduce_requirement_met(requirement, augmented_funghis, spec):
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


def is_reduce_requirement_met(requirement, augmented_funghis):
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


def calc_weighted_score(rewards, req_rewards):
    score = 0.0
    for req_reward_name, req_reward_value in req_rewards.items():
        if req_reward_name in rewards:
            score += rewards[req_reward_name] * req_reward_value
        else:
            raise ValueError(
                'Could not find "{}" in rewards'.format(req_reward_name))
    return score


def filter_best_results(funghi_combinations, results):
    if len(results) <= 0:
        return {
            'max_score': 0.0,
            'rate_and_combinations': [],
        }
    # Calculate the max score
    scores = [result['score'] for result in results]
    max_score = max(scores)
    # Keep the combinations with the same max score
    rate_and_combinations = []
    for combination, result in zip(funghi_combinations, results):
        score = result['score']
        if score >= max_score:
            success_count = result['success_count']
            requirement_count = result['requirement_count']
            if requirement_count > 0:
                success_rate = success_count / requirement_count * 100.0
            else:
                success_rate = 0.0
            rate_and_combinations.append((success_rate, combination))
    # Sort the combinations by score
    rate_and_combinations = sorted(
        rate_and_combinations, key=lambda t: t[0], reverse=True)
    return {
        'max_score': max_score,
        'rate_and_combinations': rate_and_combinations,
    }


def list_best_allocations(data, best_results):
    max_score = best_results['max_score']
    rate_and_combinations = best_results['rate_and_combinations']
    # Print the max score
    print('Max score: {}'.format(max_score))
    # List all allocations of the max score
    print('Best allocations ({}):'.format(len(rate_and_combinations)))
    for idx, (success_rate, combination) in enumerate(rate_and_combinations):
        print('#{}'.format(idx + 1))
        print('Success rate: {:.2f}%'.format(success_rate))
        print_best_allocation(data, combination)
        print()


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
