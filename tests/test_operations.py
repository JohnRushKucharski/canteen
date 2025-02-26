'''Test the operations.py module.'''

import unittest

from canteen.reservoir import BasicReservoir
from canteen.operations import Passive, load_basic_ops

class TestOperations(unittest.TestCase):
    '''Test Operations class.'''
    def test_passive_operate(self):
        '''Tests passive operate method updates storage and returns release.'''
        ops = Passive()
        res = BasicReservoir()
        release = ops.operate(res, 1.0)
        self.assertEqual(res.storage, 1.0)
        self.assertEqual(release, 0.0)

    def test_passive_output_labels(self):
        '''Tests passive output_labels method returns labels.'''
        res = Passive()
        labels = res.output_labels()
        self.assertEqual(labels, ('Spill',))

    def test_load_basic_ops(self):
        '''Tests load_basic_ops function returns operations function.'''
        ops = load_basic_ops()
        #TODO: Seems to be loading from canteen/plugins/ not canteen/canteen/plugins'/
        self.assertEqual(ops.__module__, 'canteen.plugins.operations.passive_outlets')
