
from JumpScale import j

app = j.tools.cuisine._getBaseAppClass()

# TODO: *1 implement & test & document (test on packet.net)

# make sure you use the trick we used in jumpscale/jumpscale_core8/lib/JumpScale/tools/cuisine/systemservices/CuisineFW.py
#   : setRuleset...   here we use a python script to make sure we set & set back to original if it doesn't work

# can we use j.sal.openvswitch & i saw there is already an .executor in,
# is it usable everywhere?

# please spec properly


class CuisineOpenvSwitch(app):
    """
    usage:

    ```
    c=j.tools.cuisine.get("ovh4")
    c.systemservices.openvswitch.install()
    ```

    """

    def __init__(self, executor, cuisine):
        self._cuisine = cuisine
        self._executor = executor
        self.__controller = None


    @property
    def _controller(self):
        if not self.__controller:
            if self._cuisine.id == 'localhost':
                host = 'localhost'
            else:
                host = '%s@%s'%(getattr(self._executor, '_login', 'root'), self._cuisine.id)
            self.__controller = j.sal.kvm.KVMController(
                host=host, executor=self._cuisine._executor)
        return self.__controller

    # def prepare(self):

    #     self.install()

    #     # check openvswitch properly configured

    def isInstalled(self):
        try:
            self._cuisine.core.run("ovs-vsctl show")
            return True
        except Exception as e:
            return False

    def install(self):
        if self._cuisine.core.isUbuntu:
            self._cuisine.package.install('openssl')
            self._cuisine.package.install('openvswitch-switch')
            self._cuisine.package.install('openvswitch-common')
            # TODO: check is ubuntu 16.04
        else:
            raise RuntimeError("only support ubuntu")
        # do checks if openvswitch installed & configured properly if not
        # install

    def networkCreate(self, network_name, bridge_name, interfaces=None):
        """
        Create a network interface using libvirt and open v switch.

        @network_name str: name of the network
        @bridge_name str: name of the main bridge created to connect to th host
        @interfaces [str]: names of the interfaces to be added to the bridge
        """
        network = j.sal.kvm.Network(
            self._controller, network_name, bridge_name, interfaces)
        return network.create()

    def networkDelete(self, bridge_name):
        """
        Delete network and bridge related to it. 

        @bridge_name
        """
        network = j.sal.kvm.Network(self._controller, bridge_name)
        return network.destroy()

    def networkList(self):
        """
        List bridges available on machaine created by openvswitch.
        """
        _, out, _ = self._cuisine.core.run("ovs-vsctl list-br")
        return out.splitlines()

    def networkListInterfaces(self, name):
        """
        List ports available on bridge specified.
        """
        _, out, _ = self._cuisine.core.run("ovs-vsctl list-ports %s" % name)
        return out.splitlines()

    def vnicCreate(self, name, bridge):
        """
        Create and interface and relevant ports connected to certain bridge or network.

        @name  str: name of the interface and port that will be creates
        @bridge str: name of bridge to add the interface to
        @qos int: limit the allowed rate to be used by interface
        """
        # TODO: *1 spec
        # is a name relevant???, how do we identify a vnic
        interface = j.sal.kvm.Interface(self._controller, name, bridge)
        self.interfaces[name] = interface
        interface.create()

    def vnicDelete(self, name, bridge):
        """
        Delete interface and port related to certain machine.

        @bridge str: name of bridge
        @name str: name of port and interface to be deleted
        """
        interface = j.sal.kvm.Interface(self._controller, name, bridge)
        return interface.destroy()

    def vnicQOS(self, name, bridge, qos, burst=None):
        """
        Limit the throughtput into an interface as a for of qos.

        @interface str: name of interface to limit rate on 
        @qos int: rate to be limited to in Kb 
        @burst int: maximum allowed burst that can be reached in Kb/s
        """
        # TODO: *1 spec what is relevant for a vnic from QOS perspective, what can we do
        # goal is we can do this at runtime
        interface = j.sal.kvm.Interface(self._controller, name, bridge)
        interface.qos(qos, burst)

    def vnicBond(self, parameter_list):
        raise NotImplemented("in development")
