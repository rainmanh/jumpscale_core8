# How to Use Git Automated

We have a handy tool `jscode` to make working with source code easier.

The `jscode` shell command is a way for developers to develop on JumpScale, easily across all repositories.

```bash
jscode --help
usage: jscode [-h] [-n NAME] [--url URL] [-m MESSAGE] [-b BRANCH]
              [-a ACCOUNTS] [-u] [-f] [-d] [-o]
              {get,commit,push,update,status,list,init}

positional arguments:
  {get,commit,push,update,status,list,init}
                        Command to perform

optional arguments:
  -h, --help            show this help message and exit
  -n NAME, --name NAME  name or partial name of repo, can also be comma
                        separated, if not specified then will ask, if '*' then
                        all.
  --url URL             url
  -m MESSAGE, --message MESSAGE
                        commit message
  -b BRANCH, --branch BRANCH
                        branch
  -a ACCOUNTS, --accounts ACCOUNTS
                        comma separated list of accounts, if not specified
                        then will ask, if '*' then all.
  -u, --update          update merge before doing push or commit
  -f, --force           auto answer yes on every question
  -d, --deletechanges   will delete all changes when doing update
  -o, --onlychanges     will only do an action where modified files are found
```

## jscode init

```bash
jscode init
```

- This will check if there is ~/.ssh/id_rsa
- If not keys will be generated
- Your Git configuration will be done (email, username)
- Your bashrc will be adjusted to make sure your ssh-agent gets loaded properly

> If you entered a passphrase for your key, you will get asked for it when you do a relogin

## jscode status and jscode list

- `jscode status` shows all the code repos status (if it has local modifications)
- `jscode list` shows the remote `URLs`

## jscode commit

Commits changes in a repo (or all repos).

Optionally commits to a branch using the `-b` option.

```shell
jscode commit -a jumpscale -r default_doc_jumpscale -m "example message"
```

If any of the arguments are not supplied by the user, they will be interactively asked.

- a: github account name
- r: repo name
- m: message

## jscode update

Pulls all new remote changes to local clone.

```shell
jscode update
```

## jscode push

Pushes all local commitsto remote.

```shell
jscode push -m "message"
```

## status

```shell
jscode status

#EXAMPLE
STATUS: account reponame                  branch added:modified:deleted   insyncwithremote?   localrev       remoterev
============================================================================================================================
jumpscale       jumpscale_portal          unstable   a1  :m0  :d0         reposync:N          lrev:401       rrev:406
```

```
!!!
title = "How To Use Git Automated"
date = "2017-04-08"
tags = ["howto"]
```
