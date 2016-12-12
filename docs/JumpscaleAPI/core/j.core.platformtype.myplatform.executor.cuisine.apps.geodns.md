<!-- toc -->
## j.core.platformtype.myplatform.executor.cuisine.apps.geodns

- /opt/jumpscale8/lib/JumpScale/tools/cuisine/apps/CuisineGeoDns.py

### Methods

#### add_record(*domain_name, subdomain, record_type, value, weight=100*) 

```
@domain_name = domin object name : string
@subdomain = subdomain assigned to record : string
@record_type = cname or a :string
@value = ip or cname : string
@weight = recurrence on request : int

```

#### del_domain(*domain_name*) 

```
delete domain object

```

#### del_record(*domain_name, record_type, subdomain, value, full=True*) 

```
delete record and/or entire subdomain

```

#### ensure_domain(*domain_name, serial=1, ttl=600, content, max_hosts=2, a_records, cname_records, ns*) 

```
used to create a domain_name in dns server also updates if already exists
@name = full domain name to be created or to edit
@content = string with json of entire zone file to replace or create zonefile
@a_records = dict of a_records and their subdomains
@cname_records = list of c_records and thier subdomains
@ttl = time to live specified if predefined in content will be replaced
@serial = int, used as a uniques key, need to be incretented after every change of the
    domain.
@ns = list of name servers

```

#### get_domain(*domain_name*) 

```
get domain object with dict of relevant records

```

#### get_record(*domain_name, record_type, subdomain*) 

```
returns a dict of record/s and related subdomains within domain

```

#### install(*reset*) 

```
installs and builds geodns from github.com/abh/geodns

```

#### isInstalled() 

```
Checks if a package is installed or not
You can ovveride it to use another way for checking

```

#### start(*ip='0.0.0.0', port='5053', config_dir='$JSCFGDIR/geodns/dns/', identifier='geodns_main', cpus='1', tmux*) 

```
starts geodns server with given params

```

#### stop(*name='geodns_main'*) 

```
stop geodns server with @name

```

