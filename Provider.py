from libcloud.compute.base import NodeDriver
from libcloud.compute.providers import get_driver
from libcloud.compute.types import Provider as LibCloudProvider


class Provider:
    __access_key = None  # type: str
    __region = None  # type: str
    __secret_key = None  # type: str
    __url = None  # type: str
    connection = None  # type: NodeDriver
    name = None  # type: str

    def __init__(self, name, access_key=None, secret_key=None, region=None, url=None, host=None, path=None):
        self.name = name
        self.__access_key = access_key
        self.__region = region
        self.__secret_key = secret_key
        if url is None:
            self.__url = host + path
        else:
            self.__url = url

        self.__create_connection()

    def __create_connection(self):
        if self.name == 'switch':
            open_stack = get_driver(LibCloudProvider.OPENSTACK)
            tenant, user = self.__access_key.split(':')
            self.connection = open_stack(user, self.__secret_key,
                                         ex_tenant_name=tenant,
                                         ex_force_auth_url='https://keystone.cloud.switch.ch:5000',
                                         ex_force_auth_version='3.x_password',
                                         ex_force_service_region=self.__region)
        elif self.name == 'aws':
            aws = get_driver(LibCloudProvider.EC2)
            self.connection = aws(self.__access_key, self.__secret_key, region=self.__region)
        elif self.name == 'exoscale':
            exs = get_driver(LibCloudProvider.EXOSCALE)
            self.connection = exs(key=self.__access_key, secret=self.__secret_key, url=self.__url)
        else:
            raise Exception('Not supported provider')
