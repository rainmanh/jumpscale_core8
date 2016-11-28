

## Branching Strategy:
Branches are only created by product owner (because product owner should have full overview of everything happening in the product)
### Branches on repo:
    * Currently 8.1.0 and master (8.1.1).
    * Should not be deleted.

### Branches overview
    
```
MASTER
|              8.1.0
|-------------->|
|               | 
|               | 
|               | 
|               |
|               |
|<------------- | (update master with changes from release branch)
|               v
|
|
8.1.1           
|
|
* blocking fix
| 
|
|
|
v
```
