#!/usr/bin/env python
# -*- coding: utf-8 -*-

testInfo = {"subName": "", "func": 'get_cluster_stats'}

def base(args, timeout=10):
    """
    http://docs.ceph.com/docs/giant/rados/api/python/#installation
    """
    import rados

    auth_url = getattr(args, 'auth_url')
    if isinstance(auth_url, unicode):
        auth_url = str(auth_url)

    # cluster = rados.Rados(conffile='ceph.conf',
    #                       conf=dict(keyring='ceph.client.admin.keyring'))
    cluster = rados.Rados()
    cluster.conf_set('mon_host', auth_url)
    cluster.connect(timeout)

    return cluster
