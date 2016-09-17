## AYS process

- seen per ays actor (if e.g. asked for from blueprint, or manually)
- first do init
    - when
        - if specificaly asked for (ays init)
        - if local "actor" dir does not exist yet in ays repo
    - what
        - search for the template
        - create actor dir & populate actor object in db & serialize to disk
        - if change:
            - walk over each service linked to actor & mention there is a change 
