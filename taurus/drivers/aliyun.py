#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

from libcloud.compute.providers import get_driver
from libcloud.compute.types import Provider
from aliyunsdkcore import client
from aliyunsdkcore.request import RpcRequest


testInfo = {"subName": "ecs", "func": 'access_check'}

def base(args, timeout=20):
    """
    The function base in libcloud compute mode
    reference:
    http://libcloud.readthedocs.io/en/latest/compute/drivers/aliyun_ecs.html
    """
    ECSDriver = get_driver(Provider.ALIYUN_ECS)
    access_key_id = getattr(args, 'user_id')
    access_key_secret = getattr(args, 'key')
    region = getattr(args, 'region')

    driver = ECSDriver(access_key_id,
                       access_key_secret,
                       region=region,
                       timeout=timeout)
    return driver

def ecs(args, timeout=20):
    """
    reference:
    https://github.com/aliyun/aliyun-openapi-python-sdk/tree/master/aliyun-python-sdk-ecs
    """
    client = rpc(args, timeout)
    client.set_product('Ecs')
    client.set_version('2014-05-26')

    return client

def rpc(args, timeout=20):
    """
    Base aliyun sdk
    reference:
    https://develop.aliyun.com/sdk/python
    """
    access_key_id = getattr(args, 'user_id')
    access_key_secret = getattr(args, 'key')
    region = getattr(args, 'region')
    product = getattr(args, 'product', None)
    version = getattr(args, 'version', None)

    client = Aliyun_Rpc(access_key_id,
                        access_key_secret,
                        region,
                        product,
                        version)
    return client


class Aliyun_Rpc(client.AcsClient, object):
    """
    access aliyun api by aliyun sdk
    reference:
    https://github.com/aliyun/aliyun-openapi-python-sdk/tree/master/aliyun-python-sdk-core
    """
    def __init__(self, key_id, key_secret, region, product=None, version=None):
        super(Aliyun_Rpc, self).__init__(key_id,
                                         key_secret,
                                         region)
        self.product = product
        self.version = version

    def set_product(self, product):
        self.product = product

    def set_version(self, version):
        self.version = version

    def callApi(self, action_name, params, product=None, version=None):
        """
        paramters:
        action_name: call action name
        params: k-v query_params as dict
        product: product name , as Ecs, Rds
        version: aliyun api version, must match with product, as 2014-05-26 for Ecs

        return:
        dict about result
        """

        if product is not None:
            self.product = product
        if version is not None:
            self.version = version

        request = RpcRequest(self.product, self.version, action_name)
        request.set_accept_format('json')
        request.set_query_params(params)

        return json.loads(self.do_action_with_exception(request))

    def callByRequest(self, request):
        """
        request as RpcRequest
        example:
        request = RpcRequest('Ecs', '2014-05-26')  # set product and version
        request.set_query_params(params)  # params as dict
        """
        request.set_accept_format('json')
        return self.do_action_with_exception(request)

    def access_check(self):
        request = RpcRequest(self.product, self.version, "DescribeRegions")
        request.set_accept_format('json')

        result = self.do_action_with_exception(request)
        return json.loads(result)
