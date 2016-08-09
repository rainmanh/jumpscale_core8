# How to Use Git Manually

## Generate keys

- Generate your own ssh keys

  - Look at <https://help.github.com/articles/generating-ssh-keys/> for a good explanation

- Best to use a passphrase!!! You will only have to use the passphrase when you load it in your ssh-add

## Manually load keys

ssh-agent is a very nice tool which allows you to use your keys without having to type the passphrase all the time.

Here's how to manually have your keys loaded using ssh-agent:

```
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_rsa
```

- `~/.ssh/id_rsa` is your private key you have generated, never expose this key, its only for you
- `~/.ssh/id_rsa.pub` is your public key, this one needs to be used to get access to other machine or service (like git in this case)

## How to get ssh-agent to work without having to do this manually

add this to end of $homedir/.bashrc

```
ssh-add -l &>/dev/null
if [ "$?" == 2 ]; then
  test -r ~/.ssh-agent && \
    eval "$(<~/.ssh-agent)" >/dev/null

  ssh-add -l &>/dev/null
  if [ "$?" == 2 ]; then
    (umask 066; ssh-agent > ~/.ssh-agent)
    eval "$(<~/.ssh-agent)" >/dev/null
    ssh-add
  fi
fi
```

This will make sure your ssh-agent gets loaded and keys are in memory for maximum 10 hours.

## Set your Git private details

```
git config --global user.email "your_email@example.com"
git config --global user.name "Billy Everyteen"
```

## How to manually checkout a Git repo

```
mkdir -p ~/code
cd ~/code/
git clone git@github.com:Jumpscale/jumpscale_core8.git
```

The nice thing is you will not have to use login/passwd when doing code mgmt as long as you have your keys filled in.
