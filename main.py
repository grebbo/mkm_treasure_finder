import mkm_api_manager
from util import pretty
import sys


user = sys.argv[1]

mkm_api_manager.get_deals(user, "EX", 3, 15)