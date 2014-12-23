# Libvirt/KVM provisioning tools

## Dependencies:
  * python-parted (apt)
  * python-lvm (compile, needs liblvm2-dev)

```
python provision.py [hostname] --mem [mem] --mac [mac] --really_run
qemu-img convert [qcow2] -O raw /dev/[vg]/[lv]
modprobe nbd max_part=16
qemu-nbd -c /dev/nbd[number] [image]
parted /dev/[nbdname] unit MB print

lvcreate [vgroup] -n [volume] -L [size]

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
