from test.minicluster_testbase import MiniClusterTestBase
from snakebite.errors import SnapshotException

SNAPSHOT_NAME = 'mySnapshot'


class SnapshotsTest(MiniClusterTestBase):
    def test_create_not_allowed(self):
        self.assertRaises(
            SnapshotException, self.client.createSnapshot('/dir1', SNAPSHOT_NAME).__next__)

    def test_create_allowed(self):
        new_dir = '/dir_create_allowed'
        list(self.client.mkdir([new_dir]))
        list(self.client.allowSnapshot([new_dir]))
        list(self.client.createSnapshot(new_dir, SNAPSHOT_NAME))
        self.assertTrue(self.client.test(new_dir + '/.snapshot/' + SNAPSHOT_NAME, exists=True))

    def test_allow(self):
        new_dir = '/dir_allow'
        list(self.client.mkdir([new_dir]))
        list(self.client.allowSnapshot([new_dir]))
        self.assertTrue(self.client.test(new_dir + '/.snapshot', exists=True))

    def test_allow_disallow(self):
        new_dir = '/dir_allow_disallow'
        list(self.client.mkdir([new_dir]))
        list(self.client.allowSnapshot([new_dir]))
        list(self.client.disallowSnapshot([new_dir]))
        self.assertFalse(self.client.test(new_dir + '/.snapshot', exists=True))
        self.assertRaises(
            SnapshotException, self.client.createSnapshot(new_dir, SNAPSHOT_NAME).__next__)

    def test_delete_snapshot(self):
        new_dir = '/dir_remove_snapshot'
        list(self.client.mkdir([new_dir]))
        list(self.client.allowSnapshot([new_dir]))
        list(self.client.createSnapshot(new_dir, SNAPSHOT_NAME))
        self.assertTrue(self.client.test(new_dir + '/.snapshot/' + SNAPSHOT_NAME, exists=True))
        list(self.client.deleteSnapshot(new_dir, SNAPSHOT_NAME))
        self.assertFalse(self.client.test(new_dir + '/.snapshot/' + SNAPSHOT_NAME, exists=True))
