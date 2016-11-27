
## Versions:
  * 8.1
     *  Used for cockpit v8.1 with OpenVCloud 8.1.x
  * 8.1.1
     * Core0/CoreX (@zaibon please add more)
  
## Branching Strategy:
### Branches on this repo:
  * BLOCKING:
    * Will contain blocking fixes that apply to all branches.
    * Will be periodically merged back into master and other branches
  * Version branches:
    * Currently 8.1 and 8.1.1.
    * Should not be deleted.
    * Will be base for StoryCard braches
  * StoryCard:
    * Will usually branch off of version branches.
    * Will be deleted after their conclusion. (should be always tested before merging back into version branch)
    
    
```
MASTER
|
|----|
|    | 8.1
|    | ------| 8.1_storycard_name
|    |       |
|    | <-----v
|    |
|    v
|
|----|
|    | 8.1.1
|    | ------| 8.1.1_storycard_name
|    |       |
|    | <-----v
|    |
|    v
|
|
|
v
```
