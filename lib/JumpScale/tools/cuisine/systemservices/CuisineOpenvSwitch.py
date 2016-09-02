
from JumpScale import j

base = j.tools.cuisine._getBaseClass()

# TODO: *1 implement & test & document (test on packet.net)

# make sure you use the trick we used in jumpscale/jumpscale_core8/lib/JumpScale/tools/cuisine/systemservices/CuisineFW.py
#   : setRuleset...   here we use a python script to make sure we set & set back to original if it doesn't work

# can we use j.sal.openvswitch & i saw there is already an .executor in, is it usable everywhere?

# please spec properly


class CuisineOpenvSwitch(base):
    """
    usage:

    ```
    c=j.tools.cuisine.get("ovh4")
    c.systemservices.openvswitch.install()
    ```

    """

    def prepare(self):
        self.install()

        # check openvswitch properly configured

    def install(self):
        if self._cuisine.core.isUbuntu:
            # TODO: check is ubuntu 16.04
            raise NotImplemented()
        else:
            raise RuntimeError("only support ubuntu")
        # do checks if openvswitch installed & configured properly if not install

    def vnicCreate(self, name):
        """

        """
        # TODO: *1 spec
        # is a name relevant???, how do we identify a vnic
        raise NotImplemented()

    def vnicDelete(**kwargs):
        raise NotImplemented()

    def vnicQOS(self, **kwargs):
        # TODO: *1 spec what is relevant for a vnic from QOS perspective, what can we do
        # goal is we can do this at runtime

        raise NotImplemented()
