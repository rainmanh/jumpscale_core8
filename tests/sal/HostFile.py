from JumpScale import j
hostsfactory=j.sal.hostsfile
from nose.tools import assert_equal, assert_not_equal, assert_raises, raises, assert_in, assert_not_in
import random
import socket
import struct

class TestHostFile():
    def test_remove(self):
        #generate random ip
        ip = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
        domains = ["remove.test", "remove2.test"]
        hostsfile = hostsfactory.get()
        hostsfile.set(ip, domains)
        assert_equal(hostsfile.existsIP(ip), True)
        hostsfile.remove(ip)
        assert_equal(hostsfile.existsIP(ip), False)

    def test_existsIP(self):
        ip = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
        not_exists_ip = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
        domains = ["exists.test", "exists2.test"]
        hostsfile = hostsfactory.get()
        hostsfile.set(ip, domains)
        assert_equal(True, hostsfile.existsIP(ip))
        assert_equal(False, hostsfile.existsIP(not_exists_ip))
        hostsfile.remove(ip)

    def test_getNames(self):
        ip = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
        domains = ["test_domain", "test_domain2"]
        hostsfile=j.sal.hostsfile.get()
        hostsfile.set(ip, domains)
        names = hostsfile.getNames(ip)
        assert_equal(names, domains)
        hostsfile.remove(ip)

    def test_set(self):
        ip = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
        domains = ["test_set.com", "test_set2.com"]
        hostsfile = hostsfactory.get()
        hostsfile.set(ip, domains)
        hostsfile = hostsfactory.get()
        assert_equal(hostsfile.existsIP(ip), True)
        hostsfile.remove(ip)