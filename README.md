# Provisioning command
```
ubuntu-vm-builder kvm ubuntu -c ./vmbuilder.cfg 
```


# How to generate a mac address:
```
MACADDR="52:54:00:$(dd if=/dev/urandom bs=512 count=1 2>/dev/null | md5sum | sed 's/^\(..\)\(..\)\(..\).*$/\1:\2:\3/')"; echo $MACADDR
```
