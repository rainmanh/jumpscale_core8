from JumpScale import j

descr = """
This jumpscript returns network info
"""

category = "monitoring"
organization = "jumpscale"
author = "kristof@incubaid.com"
license = "bsd"
version = "1.0"
roles = []


def action():
    return j.sal.nettools.getNetworkInfo()

if __name__ == "__main__":
    print(action())
