import requests
from typing import Tuple
import threading
import time
from Instance import Instance
from Provider import Provider

API_URL = 'http://86.119.37.171:15000'


class Benchmark(threading.Thread):
    __instance = None  # type: Instance
    __provider = None  # type: Provider
    __ssh_key = None  # type: Tuple[str, str]

    def __init__(self, provider, instance, ssh_key):
        """
        Construct benchmark object

        :param Provider provider: Cloud provider object
        :param Instance instance: Instance object
        :param (private_key, public_key) ssh_key: ssh key for instance (public and private)
        """
        threading.Thread.__init__(self)
        self.__provider = provider
        self.__instance = instance
        self.__ssh_key = ssh_key

    def run(self):
        """
        Run benchmark

        :return:
        """
        self.__instance.create(self.__provider.connection, self.__ssh_key[1])
        self.__run_benchmark()

    def __run_benchmark(self):
        r = requests.post(API_URL + '/benchmark/',
                          json={
                              'serverIP': self.__instance.public_ip,
                              'serviceprovider': self.__provider.name,
                              'flavor': self.__instance.flavor,
                              'userName': self.__instance.username,
                              'privateKey': self.__ssh_key[0]
                          })

        if r.status_code != 200:
            print r.content
