JumpScale 8
===========

#[![Build Status](http://ci.codescalers.com/buildStatus/icon?job=jumpscale8-build)](http://ci.codescalers.com/job/jumpscale8-build/)

JumpScale is A cloud automation product and a branch from what used to be Pylabs. About 7 years ago Pylabs was the basis of a cloud automation product which was acquired by SUN Microsystems from a company called Q-Layer. In the mean time we are 4 versions further and we rebranded to JumpScale.

Please check our [GitBook](https://gig.gitbooks.io/jumpscale8/content/) for a full documentation

the oneliner for an install 
```
cd /tmp;rm -f install.sh;curl -k https://raw.githubusercontent.com/Jumpscale/jumpscale_core8/master/install/install.sh > install.sh;bash install.sh
```

MAC USERS
=========
make sure you have a writable /opt dir & homebrew is installed
```
sudo mkdir -p /opt
sudo chown -R despiegk:root /opt
ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

```
replace despiegk with your local username
