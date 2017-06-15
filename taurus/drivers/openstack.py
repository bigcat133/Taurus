#!/usr/bin/env python
# -*- coding: utf-8 -*-


from libcloud.compute.providers import get_driver
from libcloud.compute.types import Provider
from libcloud.common.openstack_identity import OpenStackIdentityTokenScope

from taurus.nsdrivers.drivers.openstack import NSOpenStackIdentityConnection


testInfo = {"subName": 'identity', 'func': 'authenticate'}

def base(args, timeout=10):
    user_id = getattr(args, 'user_id')
    key = getattr(args, 'key')
    auth_url = getattr(args, 'auth_url')
    tenant_name = getattr(args, 'tenant_name')

    cls = get_driver(Provider.OPENSTACK)
    driver = cls(
        user_id, key,
        ex_force_auth_version='3.x_password',
        ex_force_auth_url=auth_url,
        ex_tenant_name=tenant_name,
        timeout=timeout
    )

    return driver

def identity(args, timeout=10):
    user_id = getattr(args, 'user_id')
    key = getattr(args, 'key')
    auth_url = getattr(args, 'auth_url')
    tenant_name = getattr(args, 'tenant_name')
    # tenant_name = DriverList.getTenantName(args)

    driver = NSOpenStackIdentityConnection(
        auth_url=auth_url,
        user_id=user_id,
        key=key,
        token_scope=OpenStackIdentityTokenScope.PROJECT,
        # token_scope=OpenStackIdentityTokenScope.UNSCOPED,
        tenant_name=tenant_name,
        timeout=timeout
    )

    return driver

def customer(args, timeout=10):
    from taurus.nsdrivers.providers import Provider
    from taurus.nsdrivers.providers import get_driver

    user_id = getattr(args, 'user_id')
    key = getattr(args, 'key')
    auth_url = getattr(args, 'auth_url')
    tenant_name = getattr(args, 'tenant_name')

    cls = get_driver(Provider.OPENSTACK)
    driver = cls(user_id, key,
                 ex_force_auth_version='3.x_password',
                 ex_force_auth_url=auth_url,
                 ex_tenant_name=tenant_name,
                 timeout=timeout)

    return driver

def nova(args, timeout=10):
    from keystoneauth1.identity import v3
    from keystoneauth1 import session
    from novaclient import client

    user_id = getattr(args, 'user_id')
    key = getattr(args, 'key')
    auth_url = getattr(args, 'auth_url')
    tenant_name = getattr(args, 'tenant_name')

    auth_url += "/v3"
    auth = v3.Password(auth_url=auth_url,
                       username=user_id,
                       password=key,
                       project_name=tenant_name,
                       user_domain_name='default',
                       project_domain_name='default')

    sess = session.Session(auth=auth)
    nova = client.Client("2.1", session=sess)
    return nova

def cinder(args, timeout=10):
    """
    The function is create python-cinderclient
    user_id = getattr(args, 'user_id')
    key = getattr(args, 'key')
    auth_url = getattr(args, 'auth_url')
    tenant_name = getattr(args, 'tenant_name')
    """
    # from keystoneauth1 import loading, session
    # from cinderclient.v2 import client
    from cinderclient import client

    user_id = getattr(args, 'user_id')
    key = getattr(args, 'key')
    auth_url = getattr(args, 'auth_url')
    tenant_name = getattr(args, 'tenant_name')

    # loader = loading.get_plugin_loader('password')
    # auth = loader.load_from_options(auth_url=auth_url+'/v3',
    #                                 username=user_id,
    #                                 password=key,
    #                                 project_name=tenant_name,
    #                                 project_domain_name='default',
    #                                 user_domain_name='default')

    # sess = session.Session(auth=auth)
    # driver = client.Client('2.0', sess)
    auth_url += '/v3'
    driver = client.Client('2', user_id, key, tenant_name, auth_url)

    return driver

def glance(args, timeout=10):
    """
    glance = builderDriver('openstack', args, 'glance')
    image = glance.images.update("99f53b27-1da8-43d6-a659-51b33f60105a",
                                 None,
                                 **{'name': 'test2-11',
                                    'description': 'modify-lll'})
    """

    from keystoneauth1.identity import v3
    from keystoneauth1 import session
    from glanceclient import Client

    user_id = getattr(args, 'user_id')
    key = getattr(args, 'key')
    auth_url = getattr(args, 'auth_url')
    tenant_name = getattr(args, 'tenant_name')

    auth_url += "/v3"
    auth = v3.Password(auth_url=auth_url,
                       username=user_id,
                       password=key,
                       project_name=tenant_name,
                       user_domain_name='default',
                       project_domain_name='default')

    sess = session.Session(auth=auth)
    glance = Client(session=sess, version='2')
    return glance
