try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

pharos_src_home = 'src/python/pharos'

with open('requirements.txt', 'r') as f:
    requirements = [line.strip() for line in f.readlines()]

setup(
    name='pharos',
    version='0.1',
    packages=[
        'pharos', 'pharos.cli', 'pharos.common', 
        'pharos.display', 'pharos.lightkeeper', 'pharos.lighttower', 
        'pharos.storage'
    ],
    package_dir={
        'pharos': pharos_src_home,
        'pharos.cli': pharos_src_home + '/cli',
        'pharos.common': pharos_src_home + '/common',
        'pharos.display': pharos_src_home + '/display',
        'pharos.lightkeeper': pharos_src_home + '/lightkeeper',
        'pharos.lighttower': pharos_src_home + '/lighttower',
        'pharos.storage': pharos_src_home + '/storage'
    },
    install_requires=requirements,
    entry_points={'console_scripts': [
        'pharos = pharos.cli.main:main',
        'lighttower = pharos.lighttower.main:main',
        'lightkeeper = pharos.lightkeeper.lightkeeper:main']
    },
    zip_safe=False,
    author='DockerKorea',
    author_email='gopass2002@gmail.com',
    url='https://github.com/DockerKorea/pharos',
    description='distributed docker container monitoring tool',
    long_description='distributed docker container monitoring tool'
)
