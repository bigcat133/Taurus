#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
NSOpenStack driver
"""

import json

from libcloud.utils.py3 import httplib
from libcloud.common.openstack_identity import OpenStackIdentity_3_0_Connection
from libcloud.compute.drivers.openstack import OpenStack_1_1_NodeDriver, OpenStack_1_1_Connection
from libcloud.compute.types import InvalidCredsError
from taurus.nsdrivers.types import Provider
from libcloud.compute.types import NodeState
from libcloud.utils.iso8601 import parse_date
from libcloud.compute.base import Node
from libcloud.utils.networking import is_public_subnet

__all__ = [
    'NSOpenStackDriver',
]

ATOM_NAMESPACE = "http://www.w3.org/2005/Atom"

DEFAULT_API_VERSION = '1.1'


class NSOpenStackDriver(OpenStack_1_1_NodeDriver):
    """
    OpenStack node driver.
    """
    connectionCls = OpenStack_1_1_Connection
    type = Provider.NSOPENSTACK

    features = {"create_node": ["generates_password"]}
    _networks_url_prefix = '/os-networks'

    def __init__(self, *args, **kwargs):
        self._ex_force_api_version = str(kwargs.pop('ex_force_api_version',
                                                    None))
        super(OpenStack_1_1_NodeDriver, self).__init__(*args, **kwargs)

    def showQuota(self, tenantId, user_id=None):
        uri = '/os-quota-sets/%s/detail' % tenantId
        quotaObj = self.connection.request(uri).object
        return quotaObj['quota_set']

    def callApi(self, uri, method, params=None, headers=None):
        resp = self.connection.request(uri, method=method, data=params, headers=headers).object
        return resp

    def _to_node(self, api_node):
        public_networks_labels = ['public', 'internet']
        public_ips, private_ips = [], []

        for label, values in api_node['addresses'].items():
            for value in values:
                ip = value['addr']
                is_public_ip = False

                try:
                    is_public_ip = is_public_subnet(ip)
                except:
                    # IPv6

                    # Openstack Icehouse sets 'OS-EXT-IPS:type' to 'floating'
                    # for public and 'fixed' for private
                    explicit_ip_type = value.get('OS-EXT-IPS:type', None)

                    if label in public_networks_labels:
                        is_public_ip = True
                    elif explicit_ip_type == 'floating':
                        is_public_ip = True
                    elif explicit_ip_type == 'fixed':
                        is_public_ip = False

                if is_public_ip:
                    public_ips.append(ip)
                else:
                    private_ips.append(ip)

        # Sometimes 'image' attribute is not present if the node is in an error
        # state
        image = api_node.get('image', None)
        image_id = image.get('id', None) if image else None
        config_drive = api_node.get("config_drive", False)
        volumes_attached = api_node.get('os-extended-volumes:volumes_attached')
        created = parse_date(api_node["created"])

        return Node(
            id=api_node['id'],
            name=api_node['name'],
            state=self.NODE_STATE_MAP.get(api_node['status'],
                                          NodeState.UNKNOWN),
            public_ips=public_ips,
            private_ips=private_ips,
            created_at=created,
            driver=self,
            extra=dict(
                addresses=api_node['addresses'],
                hostId=api_node['hostId'],
                access_ip=api_node.get('accessIPv4'),
                access_ipv6=api_node.get('accessIPv6', None),
                # Docs says "tenantId", but actual is "tenant_id". *sigh*
                # Best handle both.
                tenantId=api_node.get('tenant_id') or api_node['tenantId'],
                userId=api_node.get('user_id', None),
                imageId=image_id,
                flavorId=api_node['flavor']['id'],
                uri=next(link['href'] for link in api_node['links'] if link['rel'] == 'self'),
                service_name=self.connection.get_service_name(),
                metadata=api_node['metadata'],
                password=api_node.get('adminPass', None),
                created=api_node['created'],
                updated=api_node['updated'],
                key_name=api_node.get('key_name', None),
                disk_config=api_node.get('OS-DCF:diskConfig', None),
                config_drive=config_drive,
                availability_zone=api_node.get('OS-EXT-AZ:availability_zone'),
                hypervisor_hostname=api_node.get('OS-EXT-SRV-ATTR:hypervisor_hostname'),
                volumes_attached=volumes_attached,
                task_state=api_node.get("OS-EXT-STS:task_state", None),
                vm_state=api_node.get("OS-EXT-STS:vm_state", None),
                power_state=api_node.get("OS-EXT-STS:power_state", None),
                progress=api_node.get("progress", None),
                fault=api_node.get('fault')
            ),
        )


class NSOpenStackIdentityConnection(OpenStackIdentity_3_0_Connection):

    def __init__(self, *args, **kwargs):
        super(OpenStackIdentity_3_0_Connection, self).__init__(*args, **kwargs)

    def create_project(self, name):
        uri = '/v3/projects'
        project = {'name': name,
                   "enabled": True}
        resp = self.authenticated_request(
            uri,
            headers={'Content-Type': 'application/json'},
            method="POST",
            data=json.dumps({"project": project})
        )
        if resp.status == httplib.UNAUTHORIZED:
            raise InvalidCredsError()

        return resp

    def callApi(self, uri, method, params=None):
        resp = self.request(
            uri,
            headers={'Content-Type': 'application/json'},
            method=method, data=json.dumps(params)
        )
        return resp

    def authenticated_callApi(self, uri, method, params=None):
        resp = self.authenticated_request(
            uri,
            headers={
                'Content-Type': 'application/json',
                'X-Subject-Token': self.auth_token
            },
            method=method, data=json.dumps(params)
        )
        return resp
