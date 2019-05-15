from Benchmark import Benchmark
from Instance import Instance
from Provider import Provider


def run():
    provider = Provider(
        name='exoscale',
        access_key='EXO84e091ac6a22bf8fb7b916f2',
        secret_key='-DU8_52ivubZb0-hdrx788GKtbTjw7r32LUOlFKV_VA',
        url='https://api.exoscale.com/compute'
    )

    instance = Instance('Medium', 'Linux Ubuntu 18.04 LTS 64-bit')

    with open('/home/david/.ssh/piIot') as f:
        private_key = f.read()

    with open('/home/david/.ssh/piIot.pub') as f:
        public_key = f.read()

    benchmark = Benchmark(provider, instance, (private_key, public_key))

    benchmark.run()

    pass


if __name__ == '__main__':
    run()
