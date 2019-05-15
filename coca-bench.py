from Benchmark import Benchmark
from Instance import Instance
from Provider import Provider
from Crypto.PublicKey import RSA
import argparse


def run():
    parser = argparse.ArgumentParser(description='Run benchmarks in all instances defined by the config file')
    parser.add_argument("providers", help='Configuration file describing providers')
    parser.add_argument("instances", help='Configuration file describing instances to create and benchmark')
    parser.add_argument("--nThreads", type=int, help='Number of threads to start')
    parser.add_argument("--keyLength", type=int, default=2048, help='Length of the generated SSH key')
    args = parser.parse_args()

    print args
    print args.keyLength
    key = RSA.generate(2048)
    keypair = (key.exportKey('PEM'), key.publickey().exportKey('OpenSSH'))


if __name__ == '__main__':
    run()
