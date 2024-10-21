'''
Reservoir plugin for reservoir with zone based operations.
'''
from plugins.reservoirs.pools import ReservoirWithPools

class PoolBasedOperations:
    '''
    Provides a simple example for pool based rules.
    
        Uses ReservoirWithPools plugin in plugins/reservoirs/pools.py module
    
        In deadpool not releases are made.
        In conservation pool, standard operating proceedures for given demand.
        In flood pool, empty pool given constrained maximum release.
        In surcharge space unlimited release to top of flood pool.
        In spill same as surcharge space.
    '''
    def operations(self, reservoir: ReservoirWithPools,
                   inflow: float, demand: float) -> tuple[float,...]:
        '''
        Only meant as an example for plugin development.
        '''
        # needed for surcharge and flood ops.
        max_flood_release = 0.1
        # needed for surcharge and spill ops
        flood_pool_volume = reservoir.pools.top_locations[2] - reservoir.pools.top_locations[1]

        volume = reservoir.storage + inflow
        releases = [0 for _ in reservoir.pools]
        pool_name, pool_vol = reservoir.active_pool(volume)
        match pool_name:
            case 'dead':
                return tuple(releases)
            case 'conservation':
                releases[1] = min(demand, pool_vol)
                return tuple(releases)
            case 'flood':
                releases[2] = min(pool_vol, max_flood_release)
            case 'surcharge':
                releases[2] = min(flood_pool_volume, max_flood_release)
                releases[3] = pool_vol
            case 'spill':
                releases[2] = min(flood_pool_volume, max_flood_release)
                releases[3] = reservoir.pools.top_locations[3] - reservoir.pools.top_locations[2]
                releases[4] = pool_vol
            case _:
                raise ValueError('Unexpected pool name: {pool_name}')
        return releases
    def outputs(self, reservoir: ReservoirWithPools) -> tuple[str,...]:
        '''Example outputs for pool based operations above.'''        
        return tuple(k for k, _ in reservoir.pools)
