
## Active branches for our new development which is 8.2.0 & below

- 8.2.0
- 8.2.0_cuisine: all changes to cuisine
- 8.2.0_dev_flist: development of new flist approach based on key value stor
- 8.2.0_ays: all development on ays (fixes, ...)

## branching rules

- always start from a release branch now 8.2.0 (use as start of name)
- always merge the release branch e.g. 8.2.0 into your branch so only your (team) changes are visible
- work with a team on a branch, this allows cooperation & still code review on larger scale
- do NOT have sub of sub branches e.g. 8.2.0_ays_fix4me and 8.2.0_ays_newfeature... , this is wrong should be both 8.2.0_ays
- never more than 5 branches underneath a release branch
- cleanup the past (only 1 8.1.0 branch (including subs))
- if you need a new branch ask the product owner (Reem & Kristof for this repo)
