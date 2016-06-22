## Destroy

The `destroy` command is quite dangerous since it destroys AYS service instances.

``` shell
ays destroy --help
Usage: ays destroy [OPTIONS]

  reset in current ays repo all services & recipe's in current repo
  (DANGEROUS) all instances will be lost !!!

  make sure to do a commit before you do a distroy, this will give you a
  chance to roll back.

Options:
  --help  Show this message and exit.
```