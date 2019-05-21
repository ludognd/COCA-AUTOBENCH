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
    instances_config = ConfigParser.ConfigParser()
    instances_config.read(args.instances)

    nthreads = len(instances_config.sections())
    if args.nThreads is not None:
        nthreads = args.nThreads
    semaphore = threading.BoundedSemaphore(nthreads)

    providers = dict()
    for provider_name in providers_config.sections():
        if providers_config.has_option(provider_name, "regions"):
            regions = providers_config.get(provider_name, "regions").split(',')
            providers[provider_name] = dict()
            for region in regions:
                region = region.strip()
                data = dict(providers_config.items(provider_name))
                data.pop("regions")
                providers[provider_name][region] = Provider(provider_name, region, data)
        else:
            data = dict(providers_config.items(provider_name))
            providers[provider_name] = Provider(provider_name, "", data)

    jobs = list()
    for instance_name in instances_config.sections():
        provider = instances_config.get(instance_name, "provider")
        region = instances_config.get(instance_name, "region")
        flavor = instances_config.get(instance_name, "flavor")
        image = instances_config.get(instance_name, "image")
        instance = Instance(providers[provider][region], instance_name, flavor, image)
        bench = Benchmark(instance, keypair, semaphore)
        jobs.append(bench)

    for job in jobs:
            job.start()

    for job in jobs:
        job.join()

    for provider_name in providers:
        if providers_config.has_option(provider_name, "regions"):
            regions = providers_config.get(provider_name, "regions").split(',')
            for region in regions:
                region = region.strip()
                providers[provider_name][region].clean()
        else:
            providers[provider_name].clean()

    print("all threads are finished", threading.active_count())


if __name__ == '__main__':
    run()
