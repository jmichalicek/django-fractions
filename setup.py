#!/usr/bin/env python

from setuptools import setup

import djfractions

version = djfractions.__version__

readme = open("README.rst").read()
history = open("HISTORY.rst").read().replace(".. :changelog:", "")

setup(
    name="django-fractions",
    version=version,
    description="""Fraction display and form fields for Django""",
    long_description=readme,
    author="Justin Michalicek",
    author_email="jmichalicek@gmail.com",
    url="https://github.com/jmichalicek/django-fractions",
    packages=[
        "djfractions",
    ],
    include_package_data=True,
    install_requires=[],
    test_suite="runtests.run_tests",
    license="BSD",
    zip_safe=False,
    keywords="django-fractions",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
