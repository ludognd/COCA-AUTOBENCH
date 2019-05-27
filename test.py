import threading

from Crypto.PublicKey import RSA

from Benchmark import Benchmark
from Instance import Instance
from Provider import Provider


def run():
    config_exo = {
        'access': 'EXO84e091ac6a22bf8fb7b916f2',
        'secret': '-DU8_52ivubZb0-hdrx788GKtbTjw7r32LUOlFKV_VA'
    }

    config_aws = {
        'access': '',
        'secret': ''
    }

    provider_exo = Provider(name='exoscale', config=config_exo, region='')
    provider_aws = Provider(name='aws', config=config_aws, region='us-east-1')
    semaphore = threading.BoundedSemaphore(2)

    instance_exo = Instance(provider_exo, 'test', 'Medium', 'Linux Ubuntu 18.04 LTS 64-bit')
    instance_aws = Instance(provider_aws, 'COCA-BENCH', 't2.micro', 'ami-0a313d6098716f372')

    key = RSA.generate(2048)
    keypair = (key.exportKey('PEM'), key.publickey().exportKey('OpenSSH'))

    benchmark_exo = Benchmark(instance_exo, keypair, semaphore)
    # benchmark_aws = Benchmark(instance_aws, keypair, semaphore)

    print "start tests"
    benchmark_exo.start()
    # benchmark_aws.start()
    print "wait threads"
    benchmark_exo.join()
    # benchmark_aws.join()
    print "end"


if __name__ == '__main__':
    run()
