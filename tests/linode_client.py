import unittest
from . import get_test_client
from linode import LinodeClient, Linode, StackScript, DnsZone
from linode.util import PaginatedList

class LinodeClientGetTests(unittest.TestCase):
    def setUp(self):
        self.client = get_test_client()

    def test_get_distributions(self):
        distros = self.client.get_distributions()
        self.assertIsNotNone(distros)
        self.assertIsInstance(distros, PaginatedList)
        self.assertGreater(len(distros), 0)

    def test_get_services(self):
        services = self.client.get_services()
        self.assertIsNotNone(services)
        self.assertIsInstance(services, PaginatedList)
        self.assertGreater(len(services), 0)

    def test_get_datacenters(self):
        dcs = self.client.get_datacenters()
        self.assertIsNotNone(dcs)
        self.assertIsInstance(dcs, PaginatedList)
        self.assertGreater(len(dcs), 0)

    def test_get_linodes(self):
        linodes = self.client.get_linodes()
        self.assertIsNotNone(linodes)
        self.assertIsInstance(linodes, PaginatedList)
        self.assertEqual(len(linodes), 0)

    def test_get_stackscripts(self):
        ss = self.client.get_stackscripts()
        self.assertIsNotNone(ss)
        self.assertIsInstance(ss, PaginatedList)
        # no idea if this will return a public stackscript or not

    def test_get_kernels(self):
        kerns = self.client.get_kernels()
        self.assertIsNotNone(kerns)
        self.assertIsInstance(kerns, PaginatedList)
        self.assertGreater(len(kerns), 0)

    def test_get_dnszones(self):
        zones = self.client.get_dnszones()
        self.assertIsNotNone(zones)
        self.assertIsInstance(zones, PaginatedList)
        self.assertEqual(len(zones), 0)

class LinodeClientCreateLinodeTests(unittest.TestCase):
    def setUp(self):
        self.client = get_test_client()

    def tearDown(self):
        for l in self.client.get_linodes():
            l.delete()

    def test_create_linode(self):
        l = self.client.create_linode('linode2048.5', 'newark')
        self.assertIsNotNone(l)
        self.assertIsInstance(l, Linode)
        self.assertIsNone(l.distribution)
        self.assertEqual(len(l.disks), 0)
        self.assertEqual(len(l.configs), 0)

    def test_create_linode_with_distro(self):
        distro = self.client.get_distributions().last()
        l, pw = self.client.create_linode('linode2048.5', 'newark', source=distro)
        self.assertIsNotNone(l)
        self.assertIsInstance(l, Linode)
        self.assertIsNotNone(pw)
        self.assertEqual(distro.id, l.distribution.id)
        self.assertGreater(len(l.disks), 0)
        self.assertGreater(len(l.configs), 0)

class LinodeClientCreateStackScriptTest(unittest.TestCase):
    def setUp(self):
        self.client = get_test_client()

    def tearDown(self):
        for s in self.client.get_stackscripts(StackScript.is_public==False):
            s.delete()

    def test_create_stackscript(self):
        distros = self.client.get_distributions()
        s = self.client.create_stackscript('test', '#!/bin/bash', distros)
        self.assertIsNotNone(s)
        self.assertIsInstance(s, StackScript)
