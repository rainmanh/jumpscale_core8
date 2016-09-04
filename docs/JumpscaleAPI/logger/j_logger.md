<!-- toc -->
## j.logger

- /opt/jumpscale8/lib/JumpScale/core/logging/LoggerFactory.py
- Properties
    - handlers
    - root_logger_name
    - PRODUCTION
    - DEV

### Methods

#### get(*name, enable_only_me*) 

```
Return a logger with the given name. Name will be prepend with 'j.' so
every logger return by this function is a child of the jumpscale root logger 'j'

Usage:
    self.logger = j.logger.get(__name__)
in library module always pass __name__ as argument.

```

#### init(*mode, level, filter*) 

#### log(*msg, level=20, category='j'*) 

#### set_level(*level*) 

#### set_mode(*mode*) 

#### set_quiet(*quiet*) 

