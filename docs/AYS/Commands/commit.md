## Commit

It is a best practice to commit your changes back to the Git repository.

This will allow changes to be recorded and use Git workflow management, such as first accepting the changes before using `ays install` to make the change reality.

```shell
ays commit --help

Usage: ays commit [OPTIONS]

Options:
  -b, --branch TEXT   Name of branch, can be used in pull request to do change
                      mgmt.
  -m, --message TEXT  Message as used in e.g. pull/push.
  -p, --push          if True then will push changes to git repo.
  --help              Show this message and exit.
```