import sys
import requests
from pharos._common import get_preference
from pharos._common import (REMOTE_API_HOST,
                            REMOTE_API_PORT)
base_url = None

def get_remote_server_addr():
    global base_url
    if not base_url:
       base_url = 'http://%s:%i' % (get_preference(REMOTE_API_HOST), get_preference(REMOTE_API_PORT))
    return base_url

