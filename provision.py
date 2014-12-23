import os
import hashlib
import argparse
import math
import glob
import subprocess

import lvm
import parted.device
import logging

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

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

# Create LVM volume of size (in bytes):
def lvm_vg_create(vg_name, lv_name, size):
    vg = lvm.vgOpen(vg_name, 'w')

    lv = vg.createLvLinear(lv_name, size)
    vg.close()
    return '/dev/{vg}/{lv}'.format(vg=vg_name, lv=lv_name)

"""
Get disk size (in bytes)
"""
def disk_size(device_name):
    dev = parted.device.Device(device_name)
    return int(dev.getSize(unit="B"))
    

def qcow_to_lvm(qcow, vg_name, lv_name):
    assert os.path.isfile(qcow)

    # build full path for qcow:
    qcow = os.path.abspath(qcow)

    qemu_nbd_bin = which('qemu-nbd')
    log.info('qemu-nbd: {}'.format(qemu_nbd_bin))

    # find free nbd device:
    nbd_mountpoint = None
    for idx in range(16):
        nbd = "/dev/nbd{}".format(idx)
        if not os.path.ismount(nbd):
            nbd_mountpoint = os.path.join("/dev", nbd)
            break
    
    assert nbd_mountpoint
    log.info("nbd mountpoint: {}".format(nbd_mountpoint))

    # Mount:
    subprocess.check_call([qemu_nbd_bin, '-c', nbd_mountpoint, qcow])
    log.info("mounted {} on {}".format(qcow, nbd_mountpoint))
    
    # Get size:
    nbd_size = disk_size(nbd_mountpoint)
    log.info("qcow: {} bytes".format(nbd_size))

    lv_device = lvm_vg_create(vg_name, lv_name, nbd_size)
    log.info("created lv: {}".format(lv_device)) 

    # Unmount nbd
    subprocess.check_call([qemu_nbd_bin, '-d', nbd_mountpoint])
    assert not os.path.ismount(nbd_mountpoint)

    # Copy qcow -> LVM
    assert os.path.exists(lv_device)
    
    log.info("copying {} -> {}".format(qcow, lv_device))
    subprocess.check_call([which('qemu-img'), 'convert', qcow, '-O', 'raw', lv_device])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='A ubuntu-vm-builder wrapper')
    parser.add_argument('hostname', help='The VM hostname')
    parser.add_argument('--lvm_vg', help='The LVM volume group to copy to')
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
    execv_args = [which('ubuntu-vm-builder'), 'kvm', 'ubuntu', '-c',
                  './{cfg}'.format(cfg=vmbuilder_cfgfile),
		  '--templates={}'.format(os.path.abspath('vmbuilder_templates')),
                  '-d', image_dir, '--part={cwd}/vmbuilder.partition'.format(cwd=cwd),
                  '--hostname={host}'.format(host=args.hostname)]

    print("> ubuntu-vm-builder {}".format(" ".join(execv_args)))
    
    if args.really_run:
        subprocess.check_call(execv_args)
    
    if args.lvm_vg:
        # find the qcow images:
        for path, _, filenames in os.walk(image_dir):
            for idx, qcow in enumerate([os.path.join(path, filename) for filename in filenames]):
                target_lv = "{}-disk{}".format(args.hostname, idx)
                
                log.info("{} -> {}/{}".format(qcow, args.lvm_vg, target_lv))
                if args.really_run:
                    qcow_to_lvm(qcow, args.lvm_vg, target_lv)
