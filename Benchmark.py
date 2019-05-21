import requests
from typing import Tuple
import threading
import time
from Instance import Instance

API_URL = 'http://86.119.37.171:15000'


class Benchmark(threading.Thread):
    __instance = None  # type: Instance
    __ssh_key = None  # type: Tuple[str, str]

    def __init__(self, instance, ssh_key, semaphore):
        """
        Construct benchmark object

        :param Instance instance: Instance object
        :param (private_key, public_key) ssh_key: ssh key for instance (public and private)
        :param BoundedSemaphore semaphore: semaphore to limit the number of threads working
        """
        threading.Thread.__init__(self)
        self.__instance = instance
        self.__ssh_key = ssh_key
        self.semaphore = semaphore

    def run(self):
        """
        Run benchmark

        :return:
        """
        self.semaphore.acquire()
        print "{0}\n".format("Benchmarking instance " + self.__instance.name),
        # self.__instance.create(self.__ssh_key[1])
        # self.__run_benchmark()
        time.sleep(10)
        print "{0}\n".format("Done benchmarking instance " + self.__instance.name),
        self.semaphore.release()

    def __run_benchmark(self):
        r = requests.post(API_URL + '/benchmark/',
                          json={
                              'serverIP': self.__instance.public_ip,
                              'serviceprovider': self.__instance.provider.name,
                              'flavor': self.__instance.flavor,
                              'userName': self.__instance.username,
                              'privateKey': self.__ssh_key[0]
                          })

        if r.status_code != 200:
            print r.content
