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
    packages=['pharos', 'pharos._cli', 'pharos.rest', 'pharos.daemons'],
    package_dir={
        'pharos': pharos_src_home,
        'pharos._cli': pharos_src_home + '/_cli',
        'pharos.rest': pharos_src_home + '/rest',
        'pharos.daemons': pharos_src_home + '/daemons'},
    install_requires=requirements,
    entry_points={'console_scripts': [
        'pharos = pharos.cli:main',
        'lighttower = pharos.daemons.lighttower:main',
        'lightkeeper = pharos.daemons.lightkeeper:main']
    },
    zip_safe=False,
    author='DockerKorea',
    author_email='gopass2002@gmail.com',
    url='https://github.com/DockerKorea/pharos',
    description='distributed docker container monitoring tool',
    long_description='distributed docker container monitoring tool'
)
