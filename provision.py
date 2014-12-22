import os
import hashlib
import argparse

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



def generate_config(hostname, cfg_file):
    mac = random_mac()
    #
    # Generate vmbuilder config:
    #

    with open('vmbuilder.cfg.template', 'r') as f:
        vmbuilder_config = f.read()

        # Add full path
        cwd = os.getcwd()

        vmbuilder_config = vmbuilder_config.format(cwd=cwd, mac=mac)

        with open(vmbuilder_cfgfile, 'w') as cfg_out:
            cfg_out.write(vmbuilder_config)

def which(fn):
    for path in os.environ["PATH"].split(":"):
        if os.path.exists(os.path.join(path, fn)):
                return os.path.join(path, fn)

    return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='A ubuntu-vm-builder wrapper')
    parser.add_argument('hostname', nargs=1, help='The VM hostname')
    parser.add_argument('--really_run', action='store_true',
        help='Really call the ubuntu-vm-builder')

    args = parser.parse_args()

    vmbuilder_cfgfile = "vmbuilder_{}.cfg".format(args.hostname)
    # Generate the config
    generate_config(args.hostname, vmbuilder_cfgfile)


    #
    # Print the vmbuilder command:
    #
    print("Provision the vm by calling:")
    execv_args = ['kvm', 'ubuntu', '-c',
             './{cfg}'.format(vmbuilder_cfgfile), 
             '--hostname={host}'.format(hostname)]

    printf("> ubuntu-vm-builder {}".format(" ".join(execv)))
    
    if args.really_run:
        os.execv(which('ubuntu-vm-builder'), execv_args)
