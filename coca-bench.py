from Provider import Provider
from Crypto.PublicKey import RSA
import argparse
import ConfigParser


def run():
    parser = argparse.ArgumentParser(description='Run benchmarks in all instances defined by the config file')
    parser.add_argument("providers", help='Configuration file describing providers')
    parser.add_argument("instances", help='Configuration file describing instances to create and benchmark')
    parser.add_argument("--nThreads", type=int, help='Number of threads to start')
    parser.add_argument("--keyLength", type=int, default=2048, help='Length of the generated SSH key')
    args = parser.parse_args()

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

    key = RSA.generate(2048)
    keypair = (key.exportKey('PEM'), key.publickey().exportKey('OpenSSH'))


if __name__ == '__main__':
    run()
