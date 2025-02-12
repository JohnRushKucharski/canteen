'''
Initializes plugins
'''
from canteen.plugins import Tags, load_modules

def initialize():
    '''Initialize plugins.'''
    for tag in Tags:
        load_modules(tag)

initialize()
