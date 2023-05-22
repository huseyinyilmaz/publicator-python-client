from setuptools import setup, find_packages
import os

setup(
    name='publicatorclient',
    version='0.1.1',
    author='Huseyin Yilmaz',
    author_email='yilmazhuseyin@gmail.com',
    url='https://github.com/huseyinyilmaz/publicator-python-client',
    description='Client for connecting publicator server.',
    long_description=os.path.join(os.path.dirname(__file__), 'README.rst'),
    packages=find_packages(exclude=[]),
    install_requires=[
        'requests==2.31.0'
    ],
    include_package_data=True,
)
