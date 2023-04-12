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

# Redirects error messages out to Null to subduce error usage messages being outputted by pyEZ.
class DevNull:
    def write(self, msg):
        pass
sys.stderr = DevNull()

# check interface function to see the current configuration for a specified interface.
def check_interface(AS, INT):
    while True:
        try:
            dev = Device(host=f"10.1.252.{AS}", user='hyperadmin', password='').open()

            if INT < 0 or INT > 11:
                return "Interface number has to be between 0-11"

            # Show interface terse command
            show_int = dev.cli(f"show configuration interfaces ge-0/0/{INT}").split('\n')
            if show_int == ['']:
                return f"AS:{AS} || Interface ge-0/0/{INT} has not been configured."

            # Interface description
            int_des = show_int[1]
            int_tag = int_des[:-1]

            # Interface vlan 
            int_vlan = show_int[-5]
            vlan_tag = int_vlan[:-1].strip()

            # re to match and verify vlan_tag
            re_pattern = re.compile(r'(^members EVN\d\d\d)')
            re_search = re_pattern.search(vlan_tag)

            # check class of service for interface
            check_cos = dev.cli(f"show configuration class-of-service interfaces ge-0/0/{INT}")

            # if vlan_tag does not match or missing, output no vlan configured on that port, else, output vlan and int description
            if vlan_tag == '' or re_search == None:
                return f"AS:{AS} || interface ge-0/0/{INT} || " + " Interface has no vlan configured."
            elif check_cos == None or check_cos == '':
                return f"AS:{AS} || interface ge-0/0/{INT} || " + int_tag + " || " + vlan_tag + " || " + "COS not configured on this port."
            else:
                return f"AS:{AS} || interface ge-0/0/{INT} || " + int_tag + " || " + vlan_tag + " || " + check_cos

        except (ConnectTimeoutError, ConnectUnknownHostError, ConnectRefusedError):
            return "ERROR: device unreachable, please check connectivity to device."


def main_configure(AS, INT, DES, VLAN, COS):
    while True:
        try:
            dev = Device(host=f"10.1.252.{AS}", user='hyperadmin', password='dAJr3Ear$z#G*Y').open()

            # Check switch model 
            version = dev.cli("show version").split('\n')[4]
            if version == "Model: ex2300-c-12t" or version == "Model: ex2300-24t":
                MODE = "interface-mode"
            else:
                MODE = "port-mode"

            # check to see if interface number, VLAN, COS is within range
            if INT < 0 or INT > 11:
                return "Interface number has to be between 0-11"
            if VLAN < 166 or VLAN > 320:
                return "VLAN range has to be between 166-320"
            if COS > 1000:
                return "COS has to be less than 1000"
                
            cu = Config(dev)
            # create and sanitize interface
            cu.load(f'set interfaces ge-0/0/{INT} unit 0 family ethernet-switching', format='set')
            cu.load(f'delete interfaces ge-0/0/{INT}', format='set')
            # set interface description
            cu.load(f'set interfaces ge-0/0/{INT} description "{DES}"', format='set')
            # set interface VLAN tag
            cu.load(f'set interfaces ge-0/0/{INT} unit 0 family ethernet-switching {MODE} access vlan members EVN{VLAN}', format='set')

            # set class of service
            check_trunk = dev.cli(f"show configuration class-of-service interfaces ge-0/1/0")
            if check_trunk == '':
                cu.load(f'set class-of-service interfaces ge-0/0/{INT} shaping-rate {COS}m', format='set')
                cu.load(f'set class-of-service interfaces ge-0/1/0 shaping-rate {COS}m', format='set')
            else:
                show_cos = dev.cli("show configuration class-of-service").split()[-3]
                # strip show_cos to trunk_cos
                trunk_cos = show_cos[:-2]
                add_cos = int(COS) + int(trunk_cos)
                TOTAL_COS = str(add_cos)
                cu.load(f'set class-of-service interfaces ge-0/0/{INT} shaping-rate {COS}m', format='set')
                cu.load(f'set class-of-service interfaces ge-0/1/0 shaping-rate {TOTAL_COS}m', format='set')

            cu.commit()

            show_int = dev.cli(f"show configuration interfaces ge-0/0/{INT}").split('\n')
            
            int_des = show_int[1]
            int_tag = int_des[:-1]

            int_vlan = show_int[-5]
            vlan_tag = int_vlan[:-1].strip()

            check_cos = dev.cli(f"show configuration class-of-service interfaces ge-0/0/{INT}")
            return "port configured and committed " + f"AS:{AS} || interface ge-0/0/{INT} || " + int_tag + " || " + vlan_tag + " || " + check_cos

        except (ConnectTimeoutError, ConnectUnknownHostError, ConnectRefusedError):
            return "ERROR: device unreachable, please check connectivity to device"
        except ConfigLoadError:
            cu.rollback()
            return "ERROR: invalid input"
        except CommitError as e:
            cu.rollback()
            return "ERROR: commit error, message: " + str(e)


def idf_cleanup(AS):
    while True:
        try:
            dev = Device(host=f"10.1.252.{AS}", user='hyperadmin', password='dAJr3Ear$z#G*Y').open()
            cu = Config(dev)

            # Check switch model 
            version = dev.cli("show version").split('\n')[4]
            if version == "Model: ex2300-c-12t":
                MODE = "interface-mode"
            else:
                MODE = "port-mode"
            
            try:
                cu.load(f"wildcard range set interfaces ge-0/0/[0-11] unit 0 family ethernet-switching {MODE} access", format="set", merge=True)
            except ConfigLoadError:
                pass
            try:
                cu.load("wildcard range delete interfaces ge-0/0/[0-11]", format="set", merge=True)
            except ConfigLoadError:
                pass
            try:
                cu.load(f"wildcard range set interfaces ge-0/0/[0-11] unit 0 family ethernet-switching {MODE} access", format="set", merge=True)
            except ConfigLoadError:
                pass
            try:
                cu.load("set class-of-service interfaces ge-0/0/0 shaping-rate 12m", format="set")
            except ConfigLoadError:
                pass
            try:
                cu.load("delete class-of-service interfaces", format="set")
            except ConfigLoadError:
                pass
            
            def redirect_output():
                tmp = sys.stdout
                my_result = StringIO()
                sys.stdout = my_result
                show_compare = cu.pdiff()
                sys.stdout = tmp
                results = my_result.getvalue()
                return results
            
            return "This is the result of the cleanup || \n" + redirect_output()

        except (ConnectTimeoutError, ConnectUnknownHostError, ConnectRefusedError):
            return "ERROR: device unreachable, please check connectivity to device"
        except ConfigLoadError:
            cu.rollback()
            return "ERROR: invalid input"
        except CommitError as e:
            cu.rollback()
            return "ERROR: commit error, message: " + str(e)

        