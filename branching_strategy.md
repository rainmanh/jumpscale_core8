
## Versions:
  * 8.1:
     * Branch: 8.1
     * Used for cockpit v8.1 with OpenVCloud 8.1.x
     * Stories involving this version:
        * [js81](https://github.com/gig-projects/org_development/issues/1212): branch 8.1_story_js81
        * [cockpit_installation](https://github.com/gig-projects/org_development/issues/1301): branch 8.1_story_cockpit_installation
        * [autotest_216](https://github.com/gig-projects/org_development/issues/1223): branch 8.1_story_autotest_216
        * [cockpit-doc](https://github.com/gig-projects/org_development/issues/862): branch 8.1_story_cockpit-doc
        * [mvp-cockpit](https://github.com/gig-projects/org_development/issues/1318): branch 8.1_story_mvp-cockpit
        * [cockpit_chatbot](https://github.com/gig-projects/org_development/issues/1304): branch 8.1_story_cockpit_chatbot
        * [cockpit_portal](https://github.com/gig-projects/org_development/issues/1303): branch 8.1_story_cockpit_portal
        
  * 8.1.1:
     * Branch: master (new development)
     * New developement of Core0/CoreX
     * Stories involving this version:
       * [g8os.alpha](https://github.com/gig-projects/org_development/issues/1218)
     
  
## Branching Strategy:
Branches are only created by product owner (because product owner should have full overview of everything happening in the product)
### Branches on repo:
  * Version branches:
    * Currently 8.1 and master (8.1.1).
    * Should not be deleted.
    * Will be base for StoryCard braches
  * StoryCard:
    * Will usually branch off of version branches.
    * Will be deleted after their conclusion. (should be always tested before merging back into version branch)
    
    
```
MASTER
|              8.1
|-------------->|
|               |    8.1_story_<storycard_name>
|               | ----->|
|               |       |
|               | <-----x (SC done, merged back into release branch. Tested.)
|               |
|<------------- | (update master with changes from release branch)
|               v
|
|
|           8.1.1_story_storycard_name
| ------------->| 
|               |
* blocking fix  |
|               |
|-------------->| (merge upstream into SC branch)
|               |
|               |
|               |
| <-------------x (SC done, merged back into release branch. Tested.)
|
|
|
|
v
```
