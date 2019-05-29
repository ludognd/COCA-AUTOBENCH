import ConfigParser
import argparse
import os
import threading

from Crypto.PublicKey import RSA

from Benchmark import Benchmark
from Instance import Instance
from Provider import Provider


def run():
    parser = argparse.ArgumentParser(description='Run benchmarks in all instances defined by the config file')
    parser.add_argument("providers", help='Configuration file describing providers')
    parser.add_argument("instances", help='Configuration file describing instances to create and benchmark')
    parser.add_argument("--nThreads", type=int, help='Number of threads to start')
    parser.add_argument("--keyLength", type=int, default=2048, help='Length of the generated SSH key')
    args = parser.parse_args()

    key = RSA.generate(2048)
    keypair = (key.exportKey('PEM'), key.publickey().exportKey('OpenSSH'))

    pkey_name = "coca-bench.pem"

    os.system("chmod 777 " + pkey_name)
    file1 = open(pkey_name, "w")
    file1.write(keypair[0])
    file1.close()
    os.system("chmod 400 " + pkey_name)

    providers_config = ConfigParser.ConfigParser()
    providers_config.read(args.providers)
    instances_config = ConfigParser.ConfigParser()
    instances_config.read(args.instances)

    nthreads = len(instances_config.sections())
    if args.nThreads is not None:
        nthreads = args.nThreads
    semaphore = threading.BoundedSemaphore(nthreads)

    jobs = list()
    for instance_name in instances_config.sections():
        provider_name = instances_config.get(instance_name, "provider")
        flavor = instances_config.get(instance_name, "flavor")
        image = instances_config.get(instance_name, "image")
        provider_data = dict(providers_config.items(provider_name))
        username = None
        if instances_config.has_option(instance_name, "username"):
            username = instances_config.get(instance_name, "username")
        region = instances_config.get(instance_name, "region")
        provider = Provider(provider_name, region, provider_data)
        instance = Instance(provider, instance_name, flavor, image, username)
        bench = Benchmark(instance, keypair, semaphore)
        jobs.append(bench)

    for job in jobs:
        job.start()

    for job in jobs:
        job.join()

    print("all threads are finished")


if __name__ == '__main__':
    run()
