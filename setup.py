#!/usr/bin/env python

import os
import sys

import djfractions

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = djfractions.__version__

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    sys.exit()

if sys.argv[-1] == 'tag':
    print("Tagging the version on github:")
    os.system(f"git tag -a {version} -m 'version {version}'")
    os.system("git push --tags")
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='django-fractions',
    version=version,
    description="""Fraction display and form fields for Django""",
    long_description=readme,
    author='Justin Michalicek',
    author_email='jmichalicek@gmail.com',
    url='https://github.com/jmichalicek/django-fractions',
    packages=['djfractions',],
    include_package_data=True,
    install_requires=[],
    test_suite='runtests.run_tests',
    license="BSD",
    zip_safe=False,
    keywords='django-fractions',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.0',
        'Framework :: Django :: 4.1',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
