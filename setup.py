from setuptools import setup, find_packages

with open("README.md", "r") as f:
    readme = f.readlines()

setup(
    name='python-options',
    version='1.0.0',
    packages=find_packages(),
    url='https://github.com/TinDang97/python-options',
    license='MIT license',
    author='tindang',
    author_email='rainstone1029x@gmail.com',
    description=readme
)
