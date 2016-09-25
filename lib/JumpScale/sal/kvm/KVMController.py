from jinja2 import Environment, FileSystemLoader
import libvirt
import atexit
from JumpScale import j


class KVMController:

    def __init__(self, host='localhost', executor=None, base_path=None):
        self.executor = executor
        self._host = host
        self.user = host.split('@')[0] if '@' in host else 'root'
        self.open()
        atexit.register(self.close)
        if executor is None:
            self.executor = j.tools.executor.getLocal()
        self.template_path = j.sal.fs.joinPaths(
            j.sal.fs.getParent(__file__), 'templates')
        self.base_path = base_path or "/tmp/base"
        self.executor._cuisine.core.dir_ensure(self.base_path)
        self._env = Environment(loader=FileSystemLoader(self.template_path))

    def open(self):
        uri = None
        self.authorized = False
        j.tools.cuisine.local.ssh.keygen(name='libvirt')
        self.pubkey = j.tools.cuisine.local.core.file_read('/root/.ssh/libvirt.pub')
        if self._host != 'localhost':
            self.authorized = not self.executor.cuisine.ssh.authorize(self.user, self.pubkey)
            uri = 'qemu+ssh://%s/system?no_tty=1&keyfile=/root/.ssh/libvirt&no_verify=1' % self._host
        self.connection = libvirt.open(uri)
        self.readonly = libvirt.openReadOnly(uri)

    def close(self):
        def close(con):
            if con:
                try:
                    con.close()
                except:
                    pass
        close(self.connection)
        close(self.readonly)
        if self.authorized:
            self.executor._cuisine.ssh.unauthorize(self.user, self.pubkey)

    def get_template(self, template):
        return self._env.get_template(template)

    def list_machines(self):
        machines = list()
        domains = self.connection.listAllDomains()
        for domain in domains:
            machine = j.sal.kvm.Machine.from_xml(self, domain.XMLDesc())
            machines.append(machine)
        return machines
