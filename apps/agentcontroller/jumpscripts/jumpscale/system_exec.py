from JumpScale import j

descr = """
Execute command
"""

organization = "jumpscale"
author = "deboeckj@codscalers.com"
license = "bsd"
version = "1.0"
category = "tools"
async=True
roles = []
log=True

def action(cmd="hostname -a"):
    return j.sal.process.execute(cmd, dieOnNonZeroExitCode=False)


if __name__ == "__main__":
    print (action())