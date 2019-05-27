import requests
from typing import Tuple
import threading
import time
from Instance import Instance
import traceback

API_URL = 'http://86.119.37.171:15000'


class Benchmark(threading.Thread):
    __instance = None  # type: Instance
    __ssh_key = None  # type: Tuple[str, str]

    def __init__(self, instance, ssh_key, semaphore):
        """
        Construct benchmark object

        :param Instance instance: Instance object
        :param (private_key, public_key) ssh_key: ssh key for instance (public and private)
        :param BoundedSemaphore semaphore: semaphore to limit the number of working threads
        """
        threading.Thread.__init__(self)
        self.__instance = instance
        self.__ssh_key = ssh_key
        self.semaphore = semaphore

    def run(self):
        """
        Run benchmark

        """
        print "{0}\n".format(threading.current_thread().getName() + " will benchmark " + self.__instance.name),
        self.semaphore.acquire()
        self.__instance.provider.create_environment()
        print "{0}\n".format("Spawning " + self.__instance.name),
        self.__instance.create(self.__ssh_key[1])
        print "{0}\n".format("Done spawning " + self.__instance.name + " start benchmarking"),
        bench_result = self.__run_benchmark()
        print "{0}\n".format(
            "Done benchmarking instance " + self.__instance.name + " with code " + str(bench_result[0]) + "\nmessage: "
            + str(bench_result[1]) + " \ndeleting instance"),
        self.__instance.delete()
        time.sleep(180)  # Waiting for instance state to reach terminated
        print "{0}\n".format("Deleted " + self.__instance.name),
        self.__instance.provider.clean()
        self.semaphore.release()
        print "{0}\n".format(threading.current_thread().getName() + " finished"),

    def __run_benchmark(self):
        r = requests.post(API_URL + '/benchmark/',
                          json={
                              'serverIP': self.__instance.public_ip,
                              'ServiceProvider': self.__instance.provider.name+"-reg-"+self.__instance.provider.region,
                              'Flavor': self.__instance.flavor,
                              'userName': self.__instance.username,
                              'privateKey': self.__ssh_key[0]
                          })

        return r.status_code, r.content
