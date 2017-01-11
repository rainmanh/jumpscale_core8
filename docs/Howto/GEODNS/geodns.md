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
domain_manager.ensure_domain("gig.com", serial=3, ttl=600)
```
## adding **A** record


```python
domain_manager.add_record("gig.com", "www", "a", "123.45.123.1")
```

## adding **cname** record
```python
domain_manager.add_record("gig.com", "grid", "cname", "www")
```

## getting **A** record
```python
  a_records = domain_manager.get_record("gig.com", "a")
```

## getting **cname** record
```python
  cname_records = domain_manager.get_record("gig.com", "cname")
```
## deleting **A** record
```python
domain_manager.del_record("gig.com", "a", "www", full=True)
```

## deleting **cname** record
```python
domain_manager.del_record("gig.com", "cname", "grid", full=True)
```
