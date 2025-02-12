'''Test the reservoir.py module.'''
import unittest

from canteen.reservoir import BasicReservoir
from canteen.outlet import load_outlet_module
from canteen.plugins import PLUGINS, Tags

class TestReservoir(unittest.TestCase):
    '''Test Reservoir class.'''
    def test_reservoir_construction(self):
        '''Tests reservoir default construction returns object with outlets attribute.'''
        res = BasicReservoir()
        self.assertEqual(res.name, '')
        self.assertEqual(res.storage, 0.0)
        self.assertEqual(res.capacity, 1.0)
        self.assertEqual(res.operations.__name__, 'passive')

    def test_add_outlets(self):
        '''Tests add_outlets method returns new reservoir with outlets attribute.'''
        res = BasicReservoir()
        load_outlet_module('basic')
        res = res.add_outlets([PLUGINS[Tags.OUTLETS]['Basic']()])
        self.assertEqual(res.outlets[0].name, 'outlet')

    def test_operate_updates_storage(self):
        '''Tests operations method calls operations function.'''
        res = BasicReservoir()
        self.assertEqual(res.storage, 0.0)
        res.operate(inflow=1.0)
        self.assertEqual(res.storage, 1.0)

    # def test_operate_plugins(self):
    #     '''Tests operations method calls operations function.'''
    #     ops = load_basic_ops()
    #     self.assertFalse(True)

        # res = BasicReservoir()
        # load_outlet_module('basic')
        # res = res.add_outlets([PLUGINS[Tags.OUTLETS]['Basic']()])
        # self.assertEqual(res.storage, 0.0)
        # res.operate(inflow=1.0)
        # self.assertEqual(res.storage, 0.5)
