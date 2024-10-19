'''
Combines assets and outlets or reservoirs to model condition.
'''
from enum import Enum

class FailureState(Enum):
    '''Failure states for outlet.'''
    #TODO: Combine asset with structure, to compute condition.
    NORMAL = 0
    FAILED_OPEN = 1
    FAILED_CLOSED = 2
