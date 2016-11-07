JumpScale 8


[![Join the chat at https://gitter.im/Jumpscale/jumpscale_core8](https://badges.gitter.im/Jumpscale/jumpscale_core8.svg)](https://gitter.im/Jumpscale/jumpscale_core8?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)


JumpScale is A cloud automation product and a branch from what used to be Pylabs. About 7 years ago Pylabs was the basis of a cloud automation product which was acquired by SUN Microsystems from a company called Q-Layer. In the mean time we are 4 versions further and we rebranded to JumpScale.

Please check our [GitBook](https://gig.gitbooks.io/jumpscale-core8/content/) for a full documentation (alwasy shows the master)

## how to install from master

```
cd /tmp
rm -f install.sh
curl -k https://raw.githubusercontent.com/Jumpscale/jumpscale_core8/master/install/install.sh > install.sh
bash install.sh
```


## how to install from a branch

```
cd /tmp
rm -f install.sh
curl -k https://raw.githubusercontent.com/Jumpscale/jumpscale_core8/fix_installer/install/install.sh > install.sh
export JSBRANCH="fix_installer"
bash install.sh
```
