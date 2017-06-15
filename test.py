#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pprint import pprint

from taurus.manager import DriverBuilder

user_id = "admin"
key = "nsf0cusredhat"
auth_url = "http://controller:5000"

# driver = cls('<username>', '<password>',
#              ex_force_auth_version='3.x_password',
#              ex_force_auth_url='http://192.168.1.100:5000',
#              ex_force_service_type='compute',
#              ex_force_service_region='regionOne',
#              ex_tenant_name='<my tenant>')


def test_getdriver():
    from libcloud.compute.types import Provider
    from libcloud.compute.providers import get_driver

    openstack = get_driver(Provider.OPENSTACK)
    driver = openstack(user_id, key,
                       ex_force_auth_version='3.x_password',
                       ex_force_auth_url=auth_url,
                       ex_tenant_name='admin')

    pprint(driver.list_nodes())
    pprint(driver.list_images())


def test_driverBuild():
    op_driver = DriverBuilder.get("OpenStack",
                                  args={'user_id': user_id, 'key': key, 'auth_url': auth_url, 'tenant_name':'admin'})
    print(op_driver.list_nodes())
    print(op_driver.ex_limits())  # fail
    print(op_driver.list_images())


def build_os_3_driver():
    from libcloud.common.openstack_identity import OpenStackIdentity_3_0_Connection
    from libcloud.common.openstack_identity import OpenStackIdentityTokenScope

    # auth_url = "http://172.168.1.55:5000"
    driver = OpenStackIdentity_3_0_Connection(auth_url=auth_url,
                                              user_id=user_id,
                                              key=key,
                                              token_scope=OpenStackIdentityTokenScope.PROJECT,
                                              tenant_name=user_id,
                                              timeout=10)
    return driver


def test_openstack_3_0():
    driver = build_os_3_driver()
    pprint(driver.list_supported_versions())
    driver.authenticate()
    pprint(driver.list_users())
    pprint(driver.list_roles())
    pprint(driver.list_projects())


def test_ns_driver():
    driver = build_os_3_driver()
    driver.authenticate()
    tenants = driver.list_projects()

    from taurus.nsdrivers.providers import Provider
    from taurus.nsdrivers.providers import get_driver

    ns_openstack = get_driver(Provider.OPENSTACK)

    driver = ns_openstack(user_id, key,
                          ex_force_auth_version='3.x_password',
                          ex_force_auth_url=auth_url,
                          ex_tenant_name='admin')
    for tenant in tenants:
        pprint(tenant)
        pprint(driver.showQuota(tenant.id))
    print("undefine tenant:")
    pprint(driver.showQuota('test000988'))


def test_create_project():
    from taurus.nsdrivers.drivers.openstack import NSOpenStackIdentityConnection
    from libcloud.common.openstack_identity import OpenStackIdentityTokenScope
    driver = NSOpenStackIdentityConnection(auth_url=auth_url,
                                           user_id=user_id,
                                           key=key,
                                           token_scope=OpenStackIdentityTokenScope.PROJECT,
                                           tenant_name=user_id,
                                           timeout=10)
    driver.authenticate()
    pprint(driver.create_project('test_tenant'))


def test_get_host():

    from taurus.nsdrivers.providers import Provider
    from taurus.nsdrivers.providers import get_driver

    ns_openstack = get_driver(Provider.OPENSTACK)

    driver = ns_openstack(user_id, key,
                          ex_force_auth_version='3.x_password',
                          ex_force_auth_url=auth_url,
                          ex_tenant_name='admin')

    resp = driver.callApi("/os-hosts", "GET", {})
    print(resp)

    resp = driver.callApi("/os-hosts/controller", "GET", {})
    print(resp)


def test_cephDriver():
    from taurus.manager import DriverBuilder

    args = {'user_id': "",
            'key': "",
            'auth_url': "http://10.5.248.1:6789"}
    provider = 'ceph'
    driver = DriverBuilder.get(provider, args)

    # pprint(driver.get_container())
    # pprint(driver.get_capabilities())
    pprint(driver.get_account())


def test_ceph():
    import rados

    # cluster = rados.Rados(conffile='ceph.conf')
    cluster = rados.Rados(conffile='ceph.conf', conf=dict(keyring='ceph.client.admin.keyring'))
    pprint(cluster.conf_get('client'))
    cluster = rados.Rados()
    cluster.conf_set("mon_host", "10.5.248.1")
    # cluster.conf_set("mon_initial_members", "controller")
    print "\nlibrados version: " + str(cluster.version())
    print "Will attempt to connect to: " + str(cluster.conf_get('mon initial members'))

    cluster.connect()
    print "\nCluster ID: " + cluster.get_fsid()

    print "\n\nCluster Statistics"
    print "=================="
    cluster_stats = cluster.get_cluster_stats()
    print(cluster_stats)

    for key, value in cluster_stats.iteritems():
        print key, value

    pools = cluster.list_pools()
    for pool in pools:
        pprint(pool)
        ctx = cluster.open_ioctx(pool)
        pprint(ctx.get_stats())
        ctx.close()
    cluster.shutdown()

if __name__ == "__main__":
    # test_get_host()
    # test_ceph()
    test_driverBuild()
