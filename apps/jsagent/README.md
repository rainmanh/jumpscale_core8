# JSAgent
This is a port of jsagent from jumpscale7 to jumpscale8. The core jsagent works fine
but we faced the following problem:

When the agent first start, it doesn't have any `management` code. In other words it doesn't know how to pull jobs,
schedule jumpscripts or report stats, etc..
It fetches all the `cmds` from the controller which introduces the problem.
All the cmds modules are jumpscale7 modules which are `python2.7` code, plus it uses jumpscale7 API. To over come this problem we had 2 options

- Modify the ported agent to not sync the commands module and instead we port the commmands and update them to js8. 
- Modify the controller in jumpscale7 to be able to serve 2 versions of the commands based on the agent version.

We decided to go with the first option.