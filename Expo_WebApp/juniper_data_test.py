from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import ConnectTimeoutError
from jnpr.junos.exception import ConnectUnknownHostError
from jnpr.junos.exception import ConfigLoadError
from jnpr.junos.exception import CommitError
from jnpr.junos.exception import ConnectRefusedError
import sys
from io import StringIO
import re
import json
import pprint

dev = Device(host=f"10.1.252.99", user='hyperadmin', password='dAJr3Ear$z#G*Y').open()
cu = Config(dev)


def redirect_output():
    tmp = sys.stdout
    my_result = StringIO()
    sys.stdout = my_result
    show_compare = cu.pdiff()
    sys.stdout = tmp
    results = my_result.getvalue()
    return results

data = redirect_output()
print(type(data))
print(data)

#for i in data:
    #print(i)
