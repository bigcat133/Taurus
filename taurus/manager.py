#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import importlib


# from libcloud.compute.providers import get_driver
# from libcloud.compute.types import Provider

# from libcloud.storage.types import Provider as storageProvider
# from libcloud.storage.providers import get_driver as storage_get_driver

# from libcloud.common.openstack_identity import OpenStackIdentity_3_0_Connection
from libcloud.common.openstack_identity import OpenStackIdentityTokenScope

from taurus.nsdrivers.drivers.openstack import NSOpenStackIdentityConnection
from taurus.exceptions import ParamError, DriverBuildError


# providerList = {'openstack': 'publice',
#                 'aliyun': 'private'}

providerList = {'openstack': 'publice'}


class TenantManager:
    @staticmethod
    def openstack(args, timeout=10):
        user_id = getattr(args, 'user_id')
        key = getattr(args, 'key')
        auth_url = getattr(args, 'auth_url')

        driver = NSOpenStackIdentityConnection(
            auth_url=auth_url,
            user_id=user_id,
            key=key,
            token_scope=OpenStackIdentityTokenScope.UNSCOPED,
            timeout=timeout
        )
        driver.authenticate()
        resp = driver.authenticated_callApi('/v3/auth/tokens', 'GET')
        tokens = json.loads(resp.body)

        if 'project' in tokens['token']:
            return tokens['token']['project']['name']
        else:
            return None


class Paramlist:
    def __init__(self, paramDict):
        if not isinstance(paramDict, dict):
            raise ParamError('The args is must dict')
        for k in paramDict:
            setattr(self, k, paramDict[k])


class DriverBuilder:

    @staticmethod
    def import_name(driverName):
        return 'taurus.drivers.%s' % driverName.lower()

    @staticmethod
    def get(driverName, args, subName=None, timeout=30, test_func=None):
        """
        Test driver config is ok
        params:
        driverName : driver name as openstack, aliyun
        args : build driver paramters
        if miss some paramter will raise AttributeError

        return : return a driver by building
        if don't find driver name return None
        """

        module_str_name = DriverBuilder.import_name(driverName)
        try:
            module = importlib.import_module(module_str_name)
        except ImportError:
            msg = 'Driver %s is not exist!!!' % driverName
            raise DriverBuildError(msg)

        if not subName:
            subName = 'base'
        subName = subName.lower()
        if not hasattr(module, subName):
            raise DriverBuildError('Driver sub model is not exist!!!')

        d_func = getattr(module, subName)
        params = Paramlist(args)
        driver = d_func(params, timeout)
        return driver

    @staticmethod
    def getName(driverName, args, timeout=4):
        params = Paramlist(args)
        d_name = driverName.lower()
        if hasattr(TenantManager, d_name):
            d_func = getattr(TenantManager, d_name)
            name = d_func(params, timeout)
            return name
        else:
            raise DriverBuildError("Driver do not support to find Tenant or Region")

    @staticmethod
    def test(driverName, args):
        """
        build driver by driver name
        params:
        driverName : driver name as openstack, aliyun
        args : build driver paramters
        if miss some paramter will raise AttributeError

        return : return a driver by building
        if don't find driver name return None
        """

        module_str_name = DriverBuilder.import_name(driverName)
        try:
            module = importlib.import_module(module_str_name)

            testInfo = {"subName": "", "func": 'test'}
            if hasattr(module, 'testInfo'):
                testInfo = getattr(module, 'testInfo')

            subName = testInfo["subName"]
            driver = DriverBuilder.get(driverName, args, subName, timeout=5)
            d_name = driverName.lower()
            if subName:
                d_name = '%s_%s' % (d_name, subName)

            test_fun_name = testInfo["func"]
            test_func = getattr(driver, test_fun_name)
            test_func()
        except Exception as ex:
            # import traceback
            # print(traceback.format_exc())
            return False, ex.message
        return True, ''
