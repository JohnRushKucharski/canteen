'''
This primarily supports the Canteen mapping module.

MetaData stores information about mappings, to make their 
use more transparent and to support validation.
'''
from dataclasses import dataclass

@dataclass
class MetaData:
    '''
    Holds metadata about a Mapping.
    '''
    name: str = ""
    description: str = ""

@dataclass
class MetaDataPlusRange(MetaData):
    '''
    Implements MetaData protocol for Pool components.
    '''
    range_: tuple[float, float] = (float('-inf'), float('inf'))

@dataclass
class XYMetaData(MetaData):
    '''
    Implements MetaData protocol for XYMap.
    '''
    xname: str = ""
    yname: str = ""
    domain: tuple[float, float] = (float('-inf'), float('inf'))
    range_: tuple[float, float] = (float('-inf'), float('inf'))
