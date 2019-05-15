from libcloud.compute.base import NodeDriver
from libcloud.compute.providers import get_driver
from libcloud.compute.types import Provider as LibCloudProvider


class Provider:
    connection = None  # type: NodeDriver
    name = None  # type: str
    region = None  # type: str
    ip_type = "public_ips" # type: str

    def __init__(self, name, region, config):
        self.name = name
        self.region = region
        self.connection = self.__create_connection(config)

    def __create_connection(self, data):
        print data, type(data)
        if self.name == "switchengines":
            self.ip_type = "private_ips"
            driver = get_driver(LibCloudProvider.OPENSTACK)
            project = data['project']
            username = data['username']
            password = data['password']
            return driver(username, password,
                                  ex_tenant_name=project,
                                  ex_force_auth_url='https://keystone.cloud.switch.ch:5000',
                                  ex_force_auth_version='3.x_password',
                                  ex_force_service_region=self.region)
        elif self.name == "aws":
            driver = get_driver(LibCloudProvider.EC2)
            access = data['access']
            secret = data['secret']
            return driver(access, secret, region=self.region)
        elif self.name == "exoscale":
            driver = get_driver(LibCloudProvider.EXOSCALE)
            access = data['access']
            secret = data['secret']
            return driver(access, secret)
        elif self.name == "azure":
            pass
        elif self.name == "google":
            pass
        else:
            raise Exception('Not supported provider')
