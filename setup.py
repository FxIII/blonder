"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
"""
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='blonder',
    version='0.0.dev1',
    description='a useless python toolset for blender',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/FxIII/blonder',
    author='FxIII',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Topic :: System :: Distributed Computing',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='blender async asyncio aiomas',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=[
        "aiomas",
    ],
)
