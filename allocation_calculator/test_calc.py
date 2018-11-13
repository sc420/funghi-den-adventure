# Native modules
import copy
import unittest

# Third-party modules
import yaml

# Project modules
import calc


class TestMain(unittest.TestCase):
    STUB_ADVENTURES = '''
1:
  name: Adventure 1
  capacity: 1
  requirements:
    1:
      name: Path 1
      stats:
      - vitality: 10
      rewards:
        item1: 1
    2:
      name: Path 2
      stats:
      - intelligence: 10
        speed: 10
      rewards:
        item2: 1
    3:
      name: Path 3
      stats:
      - vitality: 30
        intelligence: 30
        speed: 30
      boosts:
      - skill3:
          intelligence: 10
          speed: 20
      rewards:
        item3: 1
  perfect_rewards:
    item4: 1
2:
  name: Adventure 2
  capacity: 2
  requirements:
    1:
      name: Path 1
      stats:
      - vitality: 10
        intelligence: 10
        speed: 10
      skills:
      - skill1: 1
      rewards:
        item5: 1
    2:
      name: Path 2
      reduce_stats:
        vitality: 120
      reduce_boosts:
      - skill1:
          vitality: 50
      rewards:
        item6: 1
    3:
      name: Path 3
      stats:
      - vitality: 100
      - vitality: 100
      rewards:
        item7: 2
    4:
      name: Path 4
      skills:
      - skill100: 1
      rewards:
        item8: 3
    5:
      name: Path 5
      reduce_stats:
        vitality: 100
      rewards:
        item9: 4
    6:
      name: Path 5
      skills:
      - skill3: 1
      - skill3: 1
      rewards:
        item10: 5
  perfect_rewards:
    item11: 6
'''
    STUB_FUNGHIS = '''
1:
  name: Funghi 1
  capacity: 1
  stats:
    vitality: 10
    intelligence: 10
    speed: 10
  skills:
    skill1: 1
2:
  name: Funghi 2
  capacity: 1
  stats:
    vitality: 10
    intelligence: 20
    speed: 30
  skills:
    skill1: 1
    skill2: 1
3:
  name: Funghi 3
  capacity: 1
  stats:
    vitality: 30
    intelligence: 20
    speed: 10
  skills:
    skill1: 1
    skill2: 1
    skill3: 1
'''
    STUB_REWARDS = '''
item1: 1.0
item2: 2.0
item3: 3.0
item4: 4.0
item5: 5.0
item6: 6.0
item7: 100.0
item8: 100.0
item9: 100.0
item10: 100.0
item11: 100.0
'''

    def test_1(self):
        EXPECTED_SCORES = [14.0, 14.0, 21.0]
        EXPECTED_SUCCESS_COUNTS = [4, 4, 5]
        EXPECTED_REQUIREMENT_COUNTS = [9, 9, 9]
        data = self.load_data(self.STUB_ADVENTURES,
                              self.STUB_FUNGHIS, self.STUB_REWARDS)
        calc.normalize_data(data)
        total_adventure_capacity = calc.calc_total_adventure_capacity(data)
        total_funghi_capacity = calc.calc_total_funghi_capacity(data)
        funghi_combinations = calc.gen_funghi_combinations(
            data, total_adventure_capacity, total_funghi_capacity)
        results = calc.calc_allocations_results(data, funghi_combinations)
        scores = [result['score'] for result in results]
        success_counts = [result['success_count'] for result in results]
        requirement_counts = [result['requirement_count']
                              for result in results]
        self.assertAlmostEqual(scores, EXPECTED_SCORES)
        self.assertEqual(success_counts, EXPECTED_SUCCESS_COUNTS)
        self.assertEqual(requirement_counts, EXPECTED_REQUIREMENT_COUNTS)

    def load_data(self, adventures, funghis, rewards):
        adventures_data = yaml.load(adventures)
        funghis_data = yaml.load(funghis)
        rewards_data = yaml.load(rewards)
        return {
            'adventures': adventures_data,
            'funghis': funghis_data,
            'rewards': rewards_data,
        }


class TestGenFunghiCombinations(unittest.TestCase):
    STUB_DATA = {
        'adventures': {
            1: {
                'name': 'adventure1',
                'capacity': 1,
            },
            2: {
                'name': 'adventure2',
                'capacity': 2,
            },
        },
        'funghis': {
            1: {
                'name': 'funghi1',
                'capacity': 1,
                'stats': {
                    'vitality': 10,
                    'intelligence': 10,
                    'speed': 10,
                },
                'skills': {
                    'skill1': 1,
                },
            },
            2: {
                'name': 'funghi2',
                'capacity': 1,
                'stats': {
                    'vitality': 10,
                    'intelligence': 20,
                    'speed': 30,
                },
                'skills': {
                    'skill2': 1,
                },
            },
            3: {
                'name': 'funghi3',
                'capacity': 1,
                'stats': {
                    'vitality': 30,
                    'intelligence': 20,
                    'speed': 10,
                },
                'skills': {
                    'skill3': 1,
                },
            },
            4: {
                'name': 'funghi4',
                'capacity': 1,
                'stats': {
                    'vitality': 30,
                    'intelligence': 30,
                    'speed': 30,
                },
                'skills': {
                    'skill4': 1,
                },
            },
        },
    }

    def test_simple_1(self):
        EXPECTED_COMBINATIONS = [
            {1: [1], 2: [2, 3]},
            {1: [1], 2: [2, 4]},
            {1: [1], 2: [3, 4]},
            {1: [2], 2: [1, 3]},
            {1: [2], 2: [1, 4]},
            {1: [2], 2: [3, 4]},
            {1: [3], 2: [1, 2]},
            {1: [3], 2: [1, 4]},
            {1: [3], 2: [2, 4]},
            {1: [4], 2: [1, 2]},
            {1: [4], 2: [1, 3]},
            {1: [4], 2: [2, 3]},
        ]
        combinations = calc.gen_funghi_combinations(self.STUB_DATA, 3, 4)
        self.assertEqual(list(combinations), EXPECTED_COMBINATIONS)

    def test_simple_2(self):
        EXPECTED_COMBINATIONS = [
            {1: [1], 2: [2, 3]},
            {1: [2], 2: [1, 3]},
            {1: [3], 2: [1, 2]},
        ]
        data = copy.deepcopy(self.STUB_DATA)
        del data['funghis'][4]
        combinations = calc.gen_funghi_combinations(data, 3, 3)
        self.assertEqual(list(combinations), EXPECTED_COMBINATIONS)

    def test_simple_3(self):
        EXPECTED_COMBINATIONS = [
            {1: [1], 2: [-1, 2]},
            {1: [2], 2: [-1, 1]},
            {1: [-1], 2: [1, 2]},
        ]
        data = copy.deepcopy(self.STUB_DATA)
        del data['funghis'][3]
        del data['funghis'][4]
        combinations = calc.gen_funghi_combinations(data, 3, 2)
        self.assertEqual(list(combinations), EXPECTED_COMBINATIONS)

    def test_multi_secondary_1(self):
        EXPECTED_COMBINATIONS = [
            {1: [1], 2: [2, 2]},
            {1: [2], 2: [1, 2]},
        ]
        data = copy.deepcopy(self.STUB_DATA)
        del data['funghis'][3]
        del data['funghis'][4]
        data['funghis'][2]['capacity'] = 2
        combinations = calc.gen_funghi_combinations(data, 3, 3)
        self.assertEqual(list(combinations), EXPECTED_COMBINATIONS)

    def test_multi_secondary_2(self):
        EXPECTED_COMBINATIONS = [
            {1: [1], 2: [2, 2]},
            {1: [1], 2: [2, 3]},
            {1: [2], 2: [1, 2]},
            {1: [2], 2: [1, 3]},
            {1: [2], 2: [2, 3]},
            {1: [3], 2: [1, 2]},
            {1: [3], 2: [2, 2]},
        ]
        data = copy.deepcopy(self.STUB_DATA)
        del data['funghis'][4]
        data['funghis'][2]['capacity'] = 2
        combinations = calc.gen_funghi_combinations(data, 3, 4)
        self.assertEqual(list(combinations), EXPECTED_COMBINATIONS)


class TestGenCombinationsPrimaryJumpy(unittest.TestCase):
    def test_simple_1(self):
        CANDIDATES = [(1, 1), (2, 1), (3, 1)]
        EXPECTED_COMBINATIONS = [
            [(1, 1)],
            [(2, 1)],
            [(3, 1)],
        ]
        combinations = calc.gen_combinations_primary_jumpy(CANDIDATES, 1)
        self.assertEqual(list(combinations), EXPECTED_COMBINATIONS)

    def test_simple_2(self):
        CANDIDATES = [(1, 1), (2, 1), (3, 1)]
        EXPECTED_COMBINATIONS = [
            [(1, 1), (2, 1)],
            [(1, 1), (3, 1)],
            [(2, 1), (3, 1)],
        ]
        combinations = calc.gen_combinations_primary_jumpy(CANDIDATES, 2)
        self.assertEqual(list(combinations), EXPECTED_COMBINATIONS)

    def test_simple_3(self):
        CANDIDATES = [(1, 1), (2, 1), (3, 1)]
        EXPECTED_COMBINATIONS = [
            [(1, 1), (2, 1), (3, 1)],
        ]
        combinations = calc.gen_combinations_primary_jumpy(CANDIDATES, 3)
        self.assertEqual(list(combinations), EXPECTED_COMBINATIONS)

    def test_multi_secondary_1(self):
        CANDIDATES = [(1, 1), (2, 1), (2, 2)]
        EXPECTED_COMBINATIONS = [
            [(1, 1), (2, 1)],
            [(2, 1), (2, 2)],
        ]
        combinations = calc.gen_combinations_primary_jumpy(CANDIDATES, 2)
        self.assertEqual(list(combinations), EXPECTED_COMBINATIONS)

    def test_multi_secondary_2(self):
        CANDIDATES = [(1, 1), (2, 1), (2, 2), (3, 1)]
        EXPECTED_COMBINATIONS = [
            [(1, 1), (2, 1), (2, 2)],
            [(1, 1), (2, 1), (3, 1)],
            [(2, 1), (2, 2), (3, 1)],
        ]
        combinations = calc.gen_combinations_primary_jumpy(CANDIDATES, 3)
        self.assertEqual(list(combinations), EXPECTED_COMBINATIONS)


class TestIsNonReduceRequirementMet(unittest.TestCase):
    STUB_FUNGHIS = [{
        'stats': {
            'vitality': 10,
            'intelligence': 10,
            'speed': 10,
        },
        'skills': {},
    }, {
        'stats': {
            'vitality': 10,
            'intelligence': 20,
            'speed': 30,
        },
        'skills': {
            'skill1': 1,
        },
    }, {
        'stats': {
            'vitality': 30,
            'intelligence': 20,
            'speed': 10,
        },
        'skills': {
            'skill1': 1,
            'skill2': 1,
        },
    }]

    def test_single_stat_1(self):
        REQUIREMENT = {
            'stats': [{
                'vitality': 10,
            }],
        }
        self.assertTrue(calc.is_non_reduce_requirement_met(
            REQUIREMENT, self.STUB_FUNGHIS, 'stats'))

    def test_single_stat_2(self):
        REQUIREMENT = {
            'stats': [{
                'intelligence': 20,
                'speed': 20,
            }],
        }
        self.assertTrue(calc.is_non_reduce_requirement_met(
            REQUIREMENT, self.STUB_FUNGHIS, 'stats'))

    def test_single_stat_3(self):
        REQUIREMENT = {
            'stats': [{
                'speed': 100,
            }],
        }
        self.assertFalse(calc.is_non_reduce_requirement_met(
            REQUIREMENT, self.STUB_FUNGHIS, 'stats'))

    def test_multi_stats_1(self):
        REQUIREMENT = {
            'stats': [{
                'vitality': 10,
                'intelligence': 10,
            }, {
                'speed': 10,
            }],
        }
        self.assertTrue(calc.is_non_reduce_requirement_met(
            REQUIREMENT, self.STUB_FUNGHIS, 'stats'))

    def test_multi_stats_2(self):
        REQUIREMENT = {
            'stats': [{
                'intelligence': 20,
                'speed': 20,
            }, {
                'vitality': 100,
            }],
        }
        self.assertFalse(calc.is_non_reduce_requirement_met(
            REQUIREMENT, self.STUB_FUNGHIS, 'stats'))

    def test_single_skill_1(self):
        REQUIREMENT = {
            'skills': [{
                'skill1': 1,
            }],
        }
        self.assertTrue(calc.is_non_reduce_requirement_met(
            REQUIREMENT, self.STUB_FUNGHIS, 'skills'))

    def test_single_skill_2(self):
        REQUIREMENT = {
            'skills': [{
                'skill100': 1,
            }],
        }
        self.assertFalse(calc.is_non_reduce_requirement_met(
            REQUIREMENT, self.STUB_FUNGHIS, 'skills'))

    def test_multi_skills_1(self):
        REQUIREMENT = {
            'skills': [{
                'skill1': 1,
                'skill2': 1,
            }]
        }
        self.assertTrue(calc.is_non_reduce_requirement_met(
            REQUIREMENT, self.STUB_FUNGHIS, 'skills'))

    def test_multi_skills_2(self):
        REQUIREMENT = {
            'skills': [{
                'skill1': 1,
                'skill100': 1,
            }]
        }
        self.assertFalse(calc.is_non_reduce_requirement_met(
            REQUIREMENT, self.STUB_FUNGHIS, 'skills'))

    def test_multi_skills_3(self):
        REQUIREMENT = {
            'skills': [{
                'skill1': 1,
            }, {
                'skill1': 1,
            }]
        }
        self.assertTrue(calc.is_non_reduce_requirement_met(
            REQUIREMENT, self.STUB_FUNGHIS, 'skills'))

    def test_multi_skills_4(self):
        REQUIREMENT = {
            'skills': [{
                'skill2': 1,
            }, {
                'skill2': 1,
            }]
        }
        self.assertFalse(calc.is_non_reduce_requirement_met(
            REQUIREMENT, self.STUB_FUNGHIS, 'skills'))


class TestIsReduceRequirementMet(unittest.TestCase):
    STUB_FUNGHIS = [{
        'stats': {
            'vitality': 10,
            'intelligence': 10,
            'speed': 10,
        },
    }, {
        'stats': {
            'vitality': 10,
            'intelligence': 20,
            'speed': 30,
        },
    }, {
        'stats': {
            'vitality': 30,
            'intelligence': 20,
            'speed': 10,
        },
    }]

    def test_empty_1(self):
        REQUIREMENT = {}
        self.assertTrue(calc.is_reduce_requirement_met(
            REQUIREMENT, self.STUB_FUNGHIS))

    def test_single_1(self):
        REQUIREMENT = {
            'reduce_stats': {
                'vitality': 10,
            }
        }
        self.assertTrue(calc.is_reduce_requirement_met(
            REQUIREMENT, self.STUB_FUNGHIS))

    def test_single_2(self):
        REQUIREMENT = {
            'reduce_stats': {
                'vitality': 100,
            }
        }
        self.assertFalse(calc.is_reduce_requirement_met(
            REQUIREMENT, self.STUB_FUNGHIS))

    def test_multi_1(self):
        REQUIREMENT = {
            'reduce_stats': {
                'vitality': 50,
                'intelligence': 50,
                'speed': 50,
            }
        }
        self.assertTrue(calc.is_reduce_requirement_met(
            REQUIREMENT, self.STUB_FUNGHIS))

    def test_multi_2(self):
        REQUIREMENT = {
            'reduce_stats': {
                'vitality': 100,
                'intelligence': 50,
                'speed': 50,
            }
        }
        self.assertFalse(calc.is_reduce_requirement_met(
            REQUIREMENT, self.STUB_FUNGHIS))


class TestGenAugmentedFunghis(unittest.TestCase):
    STUB_FUNGHIS = [{
        'stats': {
            'vitality': 10,
            'intelligence': 10,
            'speed': 10,
        },
        'skills': {
            'skill1': 1,
        },
    }, {
        'stats': {
            'vitality': 10,
            'intelligence': 20,
            'speed': 30,
        },
        'skills': {
            'skill1': 1,
            'skill2': 1,
        },
    }, {
        'stats': {
            'vitality': 30,
            'intelligence': 20,
            'speed': 10,
        },
        'skills': {
            'skill1': 1,
            'skill2': 1,
            'skill3': 1,
        },
    }]

    def test_empty_1(self):
        REQUIREMENT = {}
        augmented_funghis = calc.gen_augmented_funghis(
            REQUIREMENT, self.STUB_FUNGHIS)
        self.assertEqual(augmented_funghis, self.STUB_FUNGHIS)

    def test_single_boost_1(self):
        REQUIREMENT = {
            'boosts': [{
                'skill1': {
                    'vitality': 100,
                },
            }],
        }
        augmented_funghis = calc.gen_augmented_funghis(
            REQUIREMENT, self.STUB_FUNGHIS)
        expected_funghis = copy.deepcopy(self.STUB_FUNGHIS)
        expected_funghis[0]['stats']['vitality'] += 100
        expected_funghis[1]['stats']['vitality'] += 100
        expected_funghis[2]['stats']['vitality'] += 100
        self.assertEqual(augmented_funghis, expected_funghis)

    def test_single_boost_2(self):
        REQUIREMENT = {
            'boosts': [{
                'skill100': {
                    'vitality': 100,
                },
            }],
        }
        augmented_funghis = calc.gen_augmented_funghis(
            REQUIREMENT, self.STUB_FUNGHIS)
        self.assertEqual(augmented_funghis, self.STUB_FUNGHIS)

    def test_multi_boosts_1(self):
        REQUIREMENT = {
            'boosts': [{
                'skill1': {
                    'vitality': 100,
                },
            }, {
                'skill2': {
                    'intelligence': 101,
                    'speed': 101,
                },
            }, {
                'skill3': {
                    'speed': 102,
                },
            }],
        }
        augmented_funghis = calc.gen_augmented_funghis(
            REQUIREMENT, self.STUB_FUNGHIS)
        expected_funghis = copy.deepcopy(self.STUB_FUNGHIS)
        # Skill 1
        expected_funghis[0]['stats']['vitality'] += 100
        expected_funghis[1]['stats']['vitality'] += 100
        expected_funghis[2]['stats']['vitality'] += 100
        # Skill 2
        expected_funghis[1]['stats']['intelligence'] += 101
        expected_funghis[1]['stats']['speed'] += 101
        expected_funghis[2]['stats']['intelligence'] += 101
        expected_funghis[2]['stats']['speed'] += 101
        # Skill 3
        expected_funghis[2]['stats']['speed'] += 102
        self.assertEqual(augmented_funghis, expected_funghis)

    def test_single_reduce_boost_1(self):
        REQUIREMENT = {
            'reduce_boosts': [{
                'skill1': {
                    'vitality': 100,
                },
            }],
        }
        augmented_funghis = calc.gen_augmented_funghis(
            REQUIREMENT, self.STUB_FUNGHIS)
        expected_funghis = copy.deepcopy(self.STUB_FUNGHIS)
        expected_funghis[0]['stats']['vitality'] += 100
        expected_funghis[1]['stats']['vitality'] += 100
        expected_funghis[2]['stats']['vitality'] += 100
        self.assertEqual(augmented_funghis, expected_funghis)

    def test_multi_reduce_boost_1(self):
        REQUIREMENT = {
            'reduce_boosts': [{
                'skill1': {
                    'vitality': 100,
                },
                'skill2': {
                    'intelligence': 101,
                },
            }],
        }
        augmented_funghis = calc.gen_augmented_funghis(
            REQUIREMENT, self.STUB_FUNGHIS)
        self.assertEqual(augmented_funghis, self.STUB_FUNGHIS)

    def test_mixed_1(self):
        REQUIREMENT = {
            'boosts': [{
                'skill1': {
                    'vitality': 100,
                }
            }],
            'reduce_boosts': [{
                'skill1': {
                    'vitality': 101,
                },
            }],
        }
        augmented_funghis = calc.gen_augmented_funghis(
            REQUIREMENT, self.STUB_FUNGHIS)
        expected_funghis = copy.deepcopy(self.STUB_FUNGHIS)
        expected_funghis[0]['stats']['vitality'] += 100 + 101
        expected_funghis[1]['stats']['vitality'] += 100 + 101
        expected_funghis[2]['stats']['vitality'] += 100 + 101
        self.assertEqual(augmented_funghis, expected_funghis)


if __name__ == '__main__':
    unittest.main(exit=False)
