# Libvirt/KVM provisioning tools

## Dependencies:
  * python-parted (apt)
  * python-lvm (compile, needs liblvm2-dev)

## Post-provisioning:
There exists a VM with a XML config file that is broken;
The source for the filesystems should point to the correct
LVM device (so fix the `source dev='...` line).

```
vim /etc/libvirt/qemu/[hostname.xml]
```

Example XML:
```
<disk type='block' device='disk'>
	<driver name='qemu' type='raw' cache='none' io='native'/>
	<source dev='/dev/[vg]/[hostname]-root'/>
	<target dev='vda' bus='virtio'/>
</disk>
```
