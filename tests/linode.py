import unittest

from tests import get_test_client
from linode import Linode, Disk, Config, Backup, IPAddress, ApiError

class LinodeTest(unittest.TestCase):
    def setUp(self):
        self.client = get_test_client()

        self.distro = self.client.get_distributions().last()
        self.linode = self.client.create_linode('linode2048.5', 'newark')
        self.linode_distro = self.client.create_linode('linode2048.5', 'newark',
                source=self.distro)[0]

    def tearDown(self):
        self.linode.delete()
        self.linode_distro.delete()

    def test_linode_boot(self):
        result = self.linode_distro.boot()
        self.assertTrue(result)

    def test_linode_shutdown(self):
        result = self.linode_distro.boot()
        self.assertTrue(result)
        result = self.linode_distro.shutdown()
        self.assertTrue(result)

    def test_linode_distro_reboot(self):
        result = self.linode_distro.boot()
        self.assertTrue(result)
        result = self.linode_distro.reboot()
        self.assertTrue(result)

    def test_linode_create_disk(self):
        disk = self.linode.create_disk(500)
        self.assertIsNotNone(disk)
        self.assertIsInstance(disk, Disk)
        self.assertEqual(disk.filesystem, 'raw')
        self.assertEqual(disk.size, 500)

    def test_linode_create_disk_ext4(self):
        disk = self.linode.create_disk(500, filesystem='ext4')
        self.assertIsNotNone(disk)
        self.assertIsInstance(disk, Disk)
        self.assertEqual(disk.filesystem, 'ext4')
        self.assertEqual(disk.size, 500)

    def test_linode_disk_distro(self):
        disk, pw = self.linode.create_disk(2000, distribution=self.distro)
        self.assertIsNotNone(disk)
        self.assertIsInstance(disk, Disk)
        self.assertIsNotNone(pw)

    def test_enable_backups(self):
        result = self.linode_distro.enable_backups()
        self.assertTrue(result)
        self.assertTrue(self.linode_distro.backups.enabled)

    def test_cancel_backups(self):
        result = self.linode_distro.enable_backups()
        self.assertTrue(result)
        self.assertTrue(self.linode_distro.backups.enabled)

        result = self.linode_distro.cancel_backups()
        self.assertTrue(result)
        self.assertFalse(self.linode_distro.backups.enabled)

    def test_snapshot(self):
        result = self.linode_distro.enable_backups()
        self.assertTrue(result)

        snap = self.linode_distro.snapshot()
        self.assertIsNotNone(snap)
        self.assertIsInstance(snap, Backup)
        self.assertEqual(snap.type, 'snapshot')

    def test_allocate_private_ip(self):
        ip = self.linode.allocate_ip()
        self.assertIsNotNone(ip)
        self.assertIsInstance(ip, IPAddress)
        self.assertEqual(ip.type, 'private')

    def test_allocate_public_ip(self):
        # This should raise - the API won't give us more than one
        with self.assertRaises(ApiError):
            self.linode.allocate_ip(public=True)
