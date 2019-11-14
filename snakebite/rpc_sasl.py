# -*- coding: utf-8 -*-
# Copyright (c) 2015 Bolke de Bruin
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
'''
rpc_sasl.py - Implementation of SASL on top of Hadoop RPC.

This package contains a class providing a SASL authentication implementation
using Hadoop RPC as a transport. It was inspired the Hadoop Java classes.

May 2015

Bolke de Bruin (bolke@xs4all.nl)

'''

# python 3 support
from __future__ import absolute_import, print_function, division

import struct
import re

from snakebite.protobuf.RpcHeader_pb2 import RpcRequestHeaderProto, RpcResponseHeaderProto, RpcSaslProto
from snakebite.config import HDFSConfig
from snakebite import logger

import google.protobuf.internal.encoder as encoder
from puresasl.client import SASLClient

# Configure package logging
log = logger.getLogger(__name__)

def log_protobuf_message(header, message):
    log.debug("%s:\n\n\033[92m%s\033[0m" % (header, message))

class SaslRpcClient:
    def __init__(self, trans, hdfs_namenode_principal=None):
        self.sasl = None
        self._trans = trans
        self.hdfs_namenode_principal = hdfs_namenode_principal

    def _send_sasl_message(self, message):
        rpcheader = RpcRequestHeaderProto()
        rpcheader.rpcKind = 2 # RPC_PROTOCOL_BUFFER
        rpcheader.rpcOp = 0
        rpcheader.callId = -33 # SASL
        rpcheader.retryCount = -1
        rpcheader.clientId = b""

        s_rpcheader = rpcheader.SerializeToString()
        s_message = message.SerializeToString()

        header_length = len(s_rpcheader) + encoder._VarintSize(len(s_rpcheader)) + len(s_message) + encoder._VarintSize(len(s_message))

        self._trans.write(struct.pack('!I', header_length))
        self._trans.write_delimited(s_rpcheader)
        self._trans.write_delimited(s_message)

        log_protobuf_message("Send out", message)

    def _recv_sasl_message(self):
        bytestream = self._trans.recv_rpc_message()
        sasl_response = self._trans.parse_response(bytestream, RpcSaslProto)

        return sasl_response

    def connect(self):
        # use service name component from principal
        service = re.split('[\/@]', str(self.hdfs_namenode_principal))[0]

        if not self.sasl:
            self.sasl = SASLClient(self._trans.host, service)

        negotiate = RpcSaslProto()
        negotiate.state = 1
        self._send_sasl_message(negotiate)

        # do while true
        while True:
          res = self._recv_sasl_message()
          # TODO: check mechanisms
          if res.state == 1:
            mechs = []
            for auth in res.auths:
                mechs.append(auth.mechanism)

            log.debug("Available mechs: %s" % (",".join(mechs)))
            self.sasl.choose_mechanism(mechs, allow_anonymous=False)
            log.debug("Chosen mech: %s" % self.sasl.mechanism)

            initiate = RpcSaslProto()
            initiate.state = 2
            initiate.token = self.sasl.process()

            for auth in res.auths:
                if auth.mechanism == self.sasl.mechanism:
                    auth_method = initiate.auths.add()
                    auth_method.mechanism = self.sasl.mechanism
                    auth_method.method = auth.method
                    auth_method.protocol = auth.protocol
                    auth_method.serverId = self._trans.host

            self._send_sasl_message(initiate)
            continue
           
          if res.state == 3:
            res_token = self._evaluate_token(res)
            response = RpcSaslProto()
            response.token = res_token
            response.state = 4
            self._send_sasl_message(response)
            continue

          if res.state == 0:
            return True

    def _evaluate_token(self, sasl_response):
        return self.sasl.process(challenge=sasl_response.token)

    def wrap(self, message):
        encoded = self.sasl.wrap(message)

        sasl_message = RpcSaslProto()
        sasl_message.state = 5 #  WRAP
        sasl_message.token = encoded

        self._send_sasl_message(sasl_message)

    def unwrap(self):
        response = self._recv_sasl_message()
        if response.state != 5:
            raise Exception("Server send non-wrapped response")

        return self.sasl.unwrap(response.token)

    def use_wrap(self):
        # SASL wrapping is only used if the connection has a QOP, and
        # the value is not auth.  ex. auth-int & auth-priv
        if self.sasl.qop.decode() == 'auth-int' or self.sasl.qop.decode() == 'auth-conf':
            return True
        return False

