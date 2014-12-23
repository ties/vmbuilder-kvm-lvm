# Libvirt/KVM provisioning tools
```
python provision.py [hostname] --mem [mem] --mac [mac] --really_run
lvcreate [vgroup] -n [volume] -L [size]

modprobe nbd max_part=16
qemu-nbd -c /dev/nbd0 images/[hostname]/[...].qcow2
partprobe /dev/nbd0
dd if=/dev/nbd0 of=/dev/[vgroup]/[volume] bs=1M
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
