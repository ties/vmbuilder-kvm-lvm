import os

hostname = "pm-vm"
mac = '52:54:00:1C:D7:5E'
#
# Generate vmbuilder config:
#
vmbuilder_cfgfile = 'vmbuilder_{}.cfg'.format(hostname)

with open('vmbuilder.cfg.template', 'r') as f:
    vmbuilder_config = f.read()

    # Add full path
    cwd = os.getcwd()

    vmbuilder_config.format(cwd=cwd)

    with open(vmbuilder_cfgfile, 'w') as cfg_out:
        cfg_out.write(vmbuilder_config)

#
# Print the vmbuilder command:
#
print("Provision the vm with:")
print("> ubuntu-vm-builder kvm ubuntu -c ./{cfg} --hostname={host}".format(
    vmbuilder_cfgfile, hostname))

