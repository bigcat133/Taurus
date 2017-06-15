# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Provider related utilities
"""

# from libcloud.compute.types import Provider
from taurus.nsdrivers.types import Provider
from libcloud.common.providers import get_driver as _get_provider_driver
from libcloud.common.providers import set_driver as _set_provider_driver
from libcloud.compute.types import OLD_CONSTANT_TO_NEW_MAPPING
from libcloud.compute.deprecated import DEPRECATED_DRIVERS

__all__ = [
    "Provider",
    "DRIVERS",
    "get_driver"
]

DRIVERS = {
    Provider.NSOPENSTACK:
    ('taurus.nsdrivers.drivers.openstack', 'NSOpenStackDriver'),
}


def get_driver(provider):
    deprecated_constants = OLD_CONSTANT_TO_NEW_MAPPING
    return _get_provider_driver(
        drivers=DRIVERS, provider=provider,
        deprecated_providers=DEPRECATED_DRIVERS,
        deprecated_constants=deprecated_constants
    )


def set_driver(provider, module, klass):
    return _set_provider_driver(
        drivers=DRIVERS, provider=provider,
        module=module, klass=klass
    )
