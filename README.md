🐍 About This Fork🍴
--------------------
This is a fork of https://github.com/spotify/snakebite, via
https://github.com/kirklg/snakebite/tree/feature/python3. We maintain it enough
to work for our needs at the Internet Archive. We use the library with our CDH5
cluster and have not tested it with any other versions of hadoop. Please help
us improve this! Or make your own fork. No hard feelings.

![Snakebite mini logo](https://github.com/internetarchive/snakebite-py3/blob/master/doc/logo/logo-mini-typo.png)
---

Snakebite is a python library that provides a pure python HDFS client
and a wrapper around Hadoops minicluster. The client uses protobuf for
communicating with the NameNode and comes in the form of a library and a
command line interface. Currently, the snakebite client supports most
actions that involve the Namenode and reading data from DataNodes.

*Note:* all methods that read data from a data node are able to check
the CRC during transfer, but this is disabled by default because of
performance reasons. This is the opposite behaviour from the stock
Hadoop client.

~Snakebite requires python2 (python3 is not supported yet)~ and
python-protobuf 2.4.1 or higher.

Snakebite 1.3.x has been tested mainly against Cloudera CDH4.1.3 (hadoop
2.0.0) in production. Tests pass on HortonWorks HDP 2.0.3.22-alpha
(protocol versions 7 and 8)

Snakebite 2.x has been tested on Hortonworks HDP2.0 and CDH5 Beta and
ONLY supports Hadoop 2.2.0 and up (protocol version 9)!

Installing
==========

Snakebite-py3 releases will be available through pypi at
<https://pypi.python.org/pypi/snakebite-py3/>

To install snakebite run:

`pip install snakebite-py3`

Documentation
=============

More information and documentation can be found at
https://snakebite.readthedocs.io/en/latest/

Development
===========

Travis CI status: [![Travis](https://travis-ci.org/internetarchive/snakebite-py3.svg?branch=master)](https://travis-ci.org/internetarchive/snakebite-py3)
[![Join the chat at https://gitter.im/spotify/snakebite](https://badges.gitter.im/spotify/snakebite.svg)](https://gitter.im/spotify/snakebite?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

Copyright 2013-2016 Spotify AB
Copyright 2016-2019 Internet Archive and individual contributors
