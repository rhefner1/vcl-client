from setuptools import find_packages, setup

setup(
    name='vcl-client',
    version='0.1',
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'click',
        'keyring',
        'mock',
        'paramiko',
        'pkginfo',
        'pylint',
        'tabulate',
    ],
    entry_points={
        'console_scripts': [
            'vcl = vcl_client.cli:vcl'
        ]
    },
)

