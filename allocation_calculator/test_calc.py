# Native modules
import copy
import unittest

# Project modules
import calc

STUB_DATA = {
    'adventures': {
        1: {
            'name': 'adventure1',
            'capacity': 1
        },
        2: {
            'name': 'adventure2',
            'capacity': 2
        }
    },
    'funghis': {
        1: {
            'name': 'funghi1',
            'capacity': 1,
            'stats': {
                'vitality': 10,
                'intelligence': 10,
                'speed': 10
            },
            'skills': {
                'skill1': 1
            }
        },
        2: {
            'name': 'funghi2',
            'capacity': 1,
            'stats': {
                'vitality': 10,
                'intelligence': 20,
                'speed': 30
            },
            'skills': {
                'skill2': 1
            }
        },
        3: {
            'name': 'funghi3',
            'capacity': 1,
            'stats': {
                'vitality': 30,
                'intelligence': 20,
                'speed': 10
            },
            'skills': {
                'skill3': 1
            }
        },
        4: {
            'name': 'funghi4',
            'capacity': 1,
            'stats': {
                'vitality': 30,
                'intelligence': 30,
                'speed': 30
            },
            'skills': {
                'skill4': 1
            }
        }
    }
}


class TestGenFunghiCombinations(unittest.TestCase):
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
        combinations = calc.gen_funghi_combinations(STUB_DATA, 3, 4)
        self.assertEqual(list(combinations), EXPECTED_COMBINATIONS)

    def test_simple_2(self):
        EXPECTED_COMBINATIONS = [
            {1: [1], 2: [2, 3]},
            {1: [2], 2: [1, 3]},
            {1: [3], 2: [1, 2]},
        ]
        data = copy.deepcopy(STUB_DATA)
        del data['funghis'][4]
        combinations = calc.gen_funghi_combinations(data, 3, 3)
        self.assertEqual(list(combinations), EXPECTED_COMBINATIONS)

    def test_simple_3(self):
        EXPECTED_COMBINATIONS = [
            {1: [1], 2: [-1, 2]},
            {1: [2], 2: [-1, 1]},
            {1: [-1], 2: [1, 2]},
        ]
        data = copy.deepcopy(STUB_DATA)
        del data['funghis'][3]
        del data['funghis'][4]
        combinations = calc.gen_funghi_combinations(data, 3, 2)
        self.assertEqual(list(combinations), EXPECTED_COMBINATIONS)

    def test_multi_secondary_1(self):
        EXPECTED_COMBINATIONS = [
            {1: [1], 2: [2, 2]},
            {1: [2], 2: [1, 2]},
        ]
        data = copy.deepcopy(STUB_DATA)
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
        data = copy.deepcopy(STUB_DATA)
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


if __name__ == '__main__':
    unittest.main(exit=False)
