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



def generate_config(cfg_file, args):
    #
    # Generate vmbuilder config:
    #

    with open('vmbuilder.cfg.template', 'r') as f:
        vmbuilder_config = f.read()

        # Add full path
        cwd = os.getcwd()

        vmbuilder_config = vmbuilder_config.format(cwd=cwd, mac=args.mac,
						   mem=args.mem)

        with open(vmbuilder_cfgfile, 'w') as cfg_out:
            cfg_out.write(vmbuilder_config)

def which(fn):
    for path in os.environ["PATH"].split(":"):
        if os.path.exists(os.path.join(path, fn)):
                return os.path.join(path, fn)

    return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='A ubuntu-vm-builder wrapper')
    parser.add_argument('hostname', help='The VM hostname')
    parser.add_argument('--mac', help="The mac address", default=random_mac())
    parser.add_argument('--mem', help="Amount of memory (MB)", default=1024)
    parser.add_argument('--really_run', action='store_true',
        help='Really call the ubuntu-vm-builder')

    args = parser.parse_args()

    if not os.path.isdir('templated_configs'):
	os.mkdir('templated_configs')

    image_dir = "images/{}".format(args.hostname)

    if os.path.isdir(image_dir):
	print("The directory '{}' should not exist! - exiting.".format(image_dir))
	exit()

    vmbuilder_cfgfile = "templated_configs/vmbuilder_{}.cfg".format(args.hostname)
    # Generate the config
    generate_config(vmbuilder_cfgfile, args)


    #
    # Print the vmbuilder command:
    #
    cwd = os.getcwd()
    print("Provision the vm by calling:")
    execv_args = ['ubuntu-vm-builder', 'kvm', 'ubuntu', '-c',
             './{cfg}'.format(cfg=vmbuilder_cfgfile), 
	     '-d', image_dir, '--part={cwd}/vmbuilder.partition'.format(cwd=cwd),
             '--hostname={host}'.format(host=args.hostname)]

    print("> ubuntu-vm-builder {}".format(" ".join(execv_args)))
    
    if args.really_run:
        os.execv(which('ubuntu-vm-builder'), execv_args)
