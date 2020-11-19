from setuptools import setup, find_packages

with open("README.md", "r") as f:
    readme = f.read()

setup(
    name='python-options',
    version='1.0.0-3',
    packages=find_packages(),
    url='https://github.com/TinDang97/python-options',
    license='LICENSE',
    author='tindang',
    author_email='rainstone1029x@gmail.com',
    description="Make python class with option base on property. "
                "Using build option for client like kafka, command option like ffmpeg.",
    long_description=readme,
    long_description_content_type='text/markdown',
    keywords=["option", "pyopt", "python-options"],
    python_requires=">=3.6"
)
