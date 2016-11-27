
## Versions:
  * 8.1.0:
     * Branch: 8.1.0
     * Used for cockpit v8.1 with OpenVCloud 8.1.x
        
  * 8.1.1:
     * Branch: master (new development)
     * New developement of Core0/CoreX
     * Stories involving this version:
       * [g8os.alpha](https://github.com/gig-projects/org_development/issues/1218)
     
  
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
