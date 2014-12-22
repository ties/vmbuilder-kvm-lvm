import os
import hashlib
import binascii

hostname = "pm-vm"


#
# Random data for mac:
#
def random_mac():
    mac_seed = os.urandom(512)
    m = hashlib.sha256()
    m.update(mac_seed)

    # 6 digets in pairs of 2
    mac_digest = bytearray(m.digest())

    return '00:50:56:{:02x}:{:02x}:{:02x}'.format(
            *list(mac_digest[:4]))



mac = random_mac()
#
# Generate vmbuilder config:
#
vmbuilder_cfgfile = 'vmbuilder_{}.cfg'.format(hostname)

with open('vmbuilder.cfg.template', 'r') as f:
    vmbuilder_config = f.read()

    # Add full path
    cwd = os.getcwd()

    vmbuilder_config = vmbuilder_config.format(cwd=cwd, mac=mac)

    with open(vmbuilder_cfgfile, 'w') as cfg_out:
        cfg_out.write(vmbuilder_config)

#
# Print the vmbuilder command:
#
print("Provision the vm with:")
print("> ubuntu-vm-builder kvm ubuntu -c ./{cfg} --hostname={host}".format(
    cfg=vmbuilder_cfgfile, host=hostname))

