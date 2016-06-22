# python 3 support
from __future__ import absolute_import, print_function, division

from test.minicluster_testbase import MiniClusterTestBase
from snakebite.client import Client
import os

class EffectiveUserTest(MiniClusterTestBase):
    ERR_MSG_TOUCH = "org.apache.hadoop.security.AccessControlException\nPermission denied: user=__foobar"
    ERR_MSG_STAT = "`/foobar2': No such file or directory"

    VALID_FILE = '/foobar'
    INVALID_FILE = '/foobar2'

    def setUp(self):
        self.custom_client = Client(self.cluster.host, self.cluster.port)
        self.custom_foobar_client = Client(host=self.cluster.host,
                                           port=self.cluster.port,
                                           effective_user='__foobar')

    def test_touch(self):
        print(tuple(self.custom_client.touchz([self.VALID_FILE])))
        try:
            tuple(self.custom_foobar_client.touchz([self.INVALID_FILE]))
        except Exception as e:
            self.assertTrue(e.args[0].startswith(self.ERR_MSG_TOUCH))

        self.custom_client.stat([self.VALID_FILE])
        try:
            self.custom_client.stat([self.INVALID_FILE])
        except Exception as e:
            self.assertEquals(e.args[0], self.ERR_MSG_STAT)
