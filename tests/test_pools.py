'''Tests the pool.py Reservoir Plugin'''

import unittest

from plugins.reservoirs.pools import Pools, ReservoirWithPools

class TestPools(unittest.TestCase):
    '''
    Test Pools class.
    '''
    def test_pools_construction(self):
        '''Tests pools default construction returns object with names attribute.'''
        pools = Pools()
        self.assertEqual(pools.names, ['dead', 'conservation', 'flood', 'surcharge', 'spill'])

class TestReservoirWithPools(unittest.TestCase):
    '''
    Test ReservoirWithPools class.
    '''
    def test_reservoirwithpools_construction(self):
        '''Tests reservoirwithpools default construction 
        returns object with pool names attribute.'''
        res = ReservoirWithPools(pools=Pools())
        self.assertEqual(res.pools.names, ['dead', 'conservation', 'flood', 'surcharge', 'spill'])

    def test_pool_above_capacity_raises_value_error(self):
        '''Assert value error raised for pool above capacity.'''
        with self.assertRaises(ValueError):
            pools = Pools(names=['1', '2', '3'], top_locations=[0.5, 1.1, 2])
            ReservoirWithPools(pools=pools)

class TestActivePool(unittest.TestCase):
    '''
    Tests ReservoirWithPools.active_pool()
    '''
    def test_below_first_top_returns_min(self):
        '''
        Below first pool top returns first pool name.
        '''
        res = ReservoirWithPools(pools=Pools())
        self.assertEqual(res.active_pool(0), 'dead')

    def test_above_last_pool_top_returns_empty_string(self):
        '''
        Above top pool returns empty string.
        '''
        res = ReservoirWithPools(pools=Pools())
        self.assertEqual(res.active_pool(2), '')

    def test_in_middle_returns_expected_pool(self):
        '''
        Middle pool returns expected string.
        '''
        res = ReservoirWithPools(pools=Pools())
        self.assertEqual(res.active_pool(0.25), 'conservation')
