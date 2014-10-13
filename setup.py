from setuptools import setup

setup(
    name='pharos',
    version='0.1',
    packages=['pharos'],
    package_dir={'pharos': 'src/python/pharos'},
    install_requires=['docker-py', 'pymongo', 'flask'],

    author='DockerKorea',
    author_email='gopass2002@gmail.com',
    url='https://github.com/DockerKorea/pharos',
    description='distributed docker container monitoring tool',
    long_description='distributed docker container monitoring tool'
)
