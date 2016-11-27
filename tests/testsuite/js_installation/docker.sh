#!/bin/bash
user=$1
if [ $user = "root" ]; then
    exit 0
else
    pass=$2
    echo $pass | sudo -S groupadd docker
    echo $pass | sudo -S gpasswd -a ${USER} docker
    echo $pass | sudo -S service docker restart
fi
