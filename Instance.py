from Provider import Provider

user_data_template = """#!/usr/bin/env bash
echo "{}" >> /home/ubuntu/.ssh/authorized_keys
chown -R ubuntu:ubuntu /home/ubuntu
"""


class Instance:
    provider = None  # type: Provider
    flavor = None  # type: str
    image = None  # type: str
    public_ip = None  # type: str
    username = "ubuntu"  # type: str
    node = None  # type: Node
    secgrp_name = "COCA-BENCH"  # type: str

    def __init__(self, provider, name, flavor, image, username=None):
        self.provider = provider
        self.flavor = flavor
        self.image = image
        self.name = name
        if username is not None:
            self.username = username
        self.secgrp_name = self.secgrp_name + "-" + self.name

    def create(self, ssh_public_key):
        """

        :param Provider provider:
        :param str ssh_public_key:
        :return:
        """
        conn = self.provider.connection
        image_id = self.provider.get_image(self.image)
        flavor = [f for f in conn.list_sizes() if f.name == self.flavor][0]

        user_data = user_data_template.format(ssh_public_key)

        node_params = dict()
        node_params["name"] = self.name
        node_params["size"] = flavor
        node_params["image"] = image_id
        node_params["ex_userdata"] = user_data
        node_params["ex_security_groups"] = [self.provider.secgrp]
        if self.provider.name == "aws":
            node_params["ex_blockdevicemappings"] = [
                {"VirtualName": None,
                 "Ebs": {
                     "VolumeSize": 20,
                     "VolumeType": "gp2",
                     "DeleteOnTermination": "true"},
                 "DeviceName": "/dev/sda1"}
            ]
        if self.provider.name == "exoscale":
            node_params["ex_rootdisksize"] = "20"

        node = conn.create_node(**node_params)
        running_node = conn.wait_until_running([node], wait_period=3, timeout=600, ssh_interface=self.provider.ip_type)

        if self.provider.ip_type == "private_ips":
            floating_ip = self.__create_attach_floating_ip(conn, running_node[0][0])
            self.public_ip = floating_ip.ip_address
        else:
            self.public_ip = running_node[0][0].public_ips[0]
        self.node = running_node[0][0]
        return

    def delete(self):
        if self.node is not None:
            if self.provider.ip_type == "private_ips":
                self.provider.connection.ex_delete_floating_ip(
                    self.provider.connection.ex_get_floating_ip(self.public_ip))
            self.node.destroy()
        else:
            print self.name + "is None"

    @staticmethod
    def __create_attach_floating_ip(conn, instance):
        pool = conn.ex_list_floating_ip_pools()[0]
        floating_ip = pool.create_floating_ip()
        conn.ex_attach_floating_ip_to_node(instance, floating_ip)
        return floating_ip
