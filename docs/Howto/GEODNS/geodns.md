# How to use geodns

## install geodns
```python
cuisine = j.tools.cuisine.local
cuisine.apps.geodns.install()
```
## start geodns
```python
cuisine.apps.geodns.start()
```

## create a domain

```python
domain_manager = j.sal.domainmanager.get(cuisine)
domain = domain_manager.ensure_domain("gig.com", serial=3, ttl=600)
```
## adding **A** record


```python
domain.add_a_record("123.45.123.1", "www")
domain.save()
#OR
domain_manager.add_record("gig.com", "www", "a", "123.45.123.1")
```


## adding **cname** record
```python
domain.add_cname_record("www", "grid")
domain.save()
# OR
domain_manager.add_record("gig.com", "grid", "cname", "www")
```

## getting **A** record
```python
domain.get_a_record('www')
# OR
  a_records = domain_manager.get_record("gig.com", "a", 'www')
```

## getting **cname** record
```python
  cname_records = domain.get_cname_record('grid')
  # OR
  cname_records = domain_manager.get_record("gig.com", "cname", 'grid')
```
## deleting **A** record
```python
domain.del_a_record("www", full=True)
domain.save()
# OR
domain_manager.del_record("gig.com", "a", "www", full=True)
```

## deleting **cname** record
```python
domain.del_cname_record("grid")
domain.save()
# OR
domain_manager.del_record("gig.com", "cname", "grid", full=True)
```

```
!!!
title = "Geodns"
date = "2017-04-08"
tags = ["howto"]
```
