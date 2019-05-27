from libcloud.compute.base import NodeDriver
from libcloud.compute.providers import get_driver
from libcloud.compute.types import Provider as LibCloudProvider
import uuid


class Provider:
    connection = None  # type: NodeDriver
    name = None  # type: str
    region = None  # type: str
    ip_type = "public_ips"  # type: str

    def __init__(self, name, region, config):
        self.name = name
        self.region = region
        self.connection = self.__create_connection(config)
        self.secgrp_name = str(uuid.uuid4())

    def __create_connection(self, data):
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

    def create_environment(self):
        if self.name == "switchengines":
            self.secgrp = self.connection.ex_create_security_group(self.secgrp_name, self.secgrp_name)
            self.connection.ex_create_security_group_rule(self.secgrp, "tcp", 22, 22, "0.0.0.0/0")
        elif self.name == "aws":
            # Create a security group on aws
            self.secgrp = self.connection.ex_create_security_group(self.secgrp_name, self.secgrp_name)
            self.connection.ex_authorize_security_group_permissive(self.secgrp_name)
            self.secgrp = self.secgrp_name
        elif self.name == "exoscale":
            self.secgrp = self.connection.ex_create_security_group(self.secgrp_name)
            self.connection.ex_authorize_security_group_ingress(self.secgrp_name, "tcp", "0.0.0.0/0", 22, 22)
            self.secgrp = self.secgrp_name
        elif self.name == "azure":
            pass
        elif self.name == "google":
            pass
        else:
            raise Exception('Provider not supported')

    def clean(self):
        if self.name == "switchengines":
            self.connection.ex_delete_security_group(self.secgrp)
        elif self.name == "aws":
            self.connection.ex_delete_security_group(self.secgrp)
        elif self.name == "exoscale":
            self.connection.ex_delete_security_group(self.secgrp)
        elif self.name == "azure":
            pass
        elif self.name == "google":
            pass
        else:
            raise Exception('Provider not supported')
