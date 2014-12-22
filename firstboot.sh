# This script will run the first time the virtual machine boots
# It is ran as root.

# Expire the user account
passwd -e administrator

# Install openssh-server
apt-get update
apt-get upgrade --yes
