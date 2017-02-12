# How to Use Git Manually

## Generate keys

- Generate your own ssh keys

  - Look at <https://help.github.com/articles/generating-ssh-keys/> for a good explanation

- Best to use a passphrase!!! You will only have to use the passphrase when you load it in your ssh-add

## load ssh aggent

```
js 'j.do.SSHKeysLoad()'
```

## Set your Git private details

```
git config --global user.email "your_email@example.com"
git config --global user.name "Billy Everyteen"
```

## How to manually checkout a Git repo

```
mkdir -p ~/code/github/jumpscale
cd ~/code/github/jumpscale
git clone git@github.com:Jumpscale/jumpscale_core8.git
```

The nice thing is you will not have to use login/passwd when doing code mgmt as long as you have your keys filled in.
DO NOT checkout code using http, always use ssh
