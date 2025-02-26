'''Test the reservoir.py module.'''
import unittest

from canteen.plugin import PLUGINS, Tags
from canteen.reservoir import BasicReservoir
from canteen.outlet import load_outlet_module
from canteen.operations import load_operations_module

class TestReservoir(unittest.TestCase):
    '''Test Reservoir class.'''
    def test_reservoir_construction(self):
        '''Tests reservoir default construction returns object with outlets attribute.'''
        res = BasicReservoir()
        self.assertEqual(res.name, '')
        self.assertEqual(res.storage, 0.0)
        self.assertEqual(res.capacity, 1.0)
        #self.assertEqual(res.operations.__name__, 'Passive')

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

    def test_add_outlets_add_passive_outlet_ops(self):
        '''Tests add_outlets method adds passive outlet operations.'''
        res = BasicReservoir()
        self.assertEqual(res.storage, 0.0)
        # only spilling allowed, inflow should be stored
        o1 = res.operate(inflow=1.0)
        self.assertEqual(o1, 0.0)
        self.assertEqual(res.storage, 1.0)
        # add passive outlet, without change in operations it is not used.
        load_outlet_module('basic')
        res = res.add_outlets([PLUGINS[Tags.OUTLETS]['Basic'](location=0)])
        o2 = res.operate(inflow=0.0)
        self.assertEqual(o2, 0.0)
        self.assertEqual(res.storage, 1.0)
        # change operations to passive outlet
        load_operations_module('passive_outlets')
        res.operations = PLUGINS[Tags.OPERATIONS]['PassiveOutlets']()
        o3 = res.operate(inflow=0.0)
        self.assertEqual(o3, (1.0, 0.0))
        self.assertEqual(res.storage, 0.0)
