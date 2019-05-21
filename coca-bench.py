from Provider import Provider
from Instance import Instance
from Benchmark import Benchmark
from Crypto.PublicKey import RSA
import argparse
import ConfigParser
import threading

def run():
    parser = argparse.ArgumentParser(description='Run benchmarks in all instances defined by the config file')
    parser.add_argument("providers", help='Configuration file describing providers')
    parser.add_argument("instances", help='Configuration file describing instances to create and benchmark')
    parser.add_argument("--nThreads", type=int, help='Number of threads to start')
    parser.add_argument("--keyLength", type=int, default=2048, help='Length of the generated SSH key')
    args = parser.parse_args()

    key = RSA.generate(2048)
    keypair = (key.exportKey('PEM'), key.publickey().exportKey('OpenSSH'))

    providers_config = ConfigParser.ConfigParser()
    providers_config.read(args.providers)
    providers = dict()
    for provider_name in providers_config.sections():
        regions = providers_config.get(provider_name, "regions").split(',')
        providers[provider_name] = dict()
        for region in regions:
            region = region.strip()
            data = dict(providers_config.items(provider_name))
            data.pop("regions")
            providers[provider_name][region] = Provider(provider_name, region, data)

    instances_config = ConfigParser.ConfigParser()
    instances_config.read(args.instances)
    jobs = list()
    for instance_name in instances_config.sections():
        provider = instances_config.get(instance_name, "provider")
        region = instances_config.get(instance_name, "region")
        flavor = instances_config.get(instance_name, "flavor")
        image = instances_config.get(instance_name, "image")
        instance = Instance(providers[provider][region], instance_name, flavor, image)
        bench = Benchmark(instance, keypair)
        jobs.append(bench)

    nthreads = len(jobs)
    if args.nThreads is not None:
        nthreads = args.nThreads

    while jobs:
        if threading.active_count() <= nthreads:
            job = jobs.pop()
            job.start()


if __name__ == '__main__':
    run()
