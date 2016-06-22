## jscode

The `jscode` shell command is a way for developers to develop on JumpScale, easily across all repositories.

This page is no longer up to date, since there were quite some changes in jumpscale 7.

Check `jscode --help` for more info.


### commit

Commits local changes to repo.

```shell
jscode commit -a jumpscale -r default_doc_jumpscale -m "example message"
```

If any of the arguments are not supplied by the user, they will be
interactively asked

-   a: github account name
-   r: repo name
-   m: message

### push

Pushes commited changes to repo.

```shell
jscode push -m "message"
```

### update

Update code.

```shell
jscode update
```

### status

```shell
jscode status

#EXAMPLE
STATUS: account reponame                  branch added:modified:deleted   insyncwithremote?   localrev       remoterev
============================================================================================================================
jumpscale       jumpscale_portal          unstable   a1  :m0  :d0         reposync:N          lrev:401       rrev:406
```