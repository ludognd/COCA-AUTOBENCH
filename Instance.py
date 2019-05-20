from libcloud.compute.base import NodeDriver

user_data_template = """
#!/usr/bin/env bash
echo "{}" >> /home/ubuntu/.ssh/authorized_keys
chown -R ubuntu:ubuntu /home/ubuntu
"""


class Instance:
    flavor = None  # type: str
    image = None  # type: str
    public_ip = None  # type: str
    username = None  # type: str

    def __init__(self, name, flavor, image):
        self.flavor = flavor
        self.image = image
        self.name = name

    def create(self, connection, ssh_public_key):
        """

        :param NodeDriver connection:
        :param str ssh_public_key:
        :return:
        """

        if 'exoscale' == connection.name.lower():
            image_id = [i for i in connection.list_images() if i.name == self.image][0]
            flavor = [f for f in connection.list_sizes() if str(f.name) == self.flavor][0]
        else:
            image_id = connection.get_image(self.image)
            flavor = self.flavor

        key = " ".join(ssh_public_key.split(" ")[:-1])
        user_data = user_data_template.format(key)

        node = connection.create_node(size=flavor, image=image_id, ex_userdata=user_data, ex_keyname='labo-cloud')
        # node = connection.create_node(size=flavor, image=image_id, ex_userdata=user_data)

        self.public_ip = node.public_ips[0]
        return
