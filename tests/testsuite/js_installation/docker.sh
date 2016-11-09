#!/bin/bash
user=$1
if [ $user = "root" ]; then
    exit 0
else
    echo $pass | sudo -S groupadd docker
    sudo gpasswd -a ${USER} docker
    sudo service docker restart
fi
