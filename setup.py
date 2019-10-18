#! /usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


setup(
    name='djangowebpushpoc',
    version='0.1',
    description='Django Webpush Demo',
    author='Elias Showk',
    author_email='elias@showk.me',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    scripts=('manage.py',),
    url='https://github.com/elishowk/django-webpush-demo',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
    install_requires=[
        'django>=2.2.6',
        'django-push-notifications>=1.6.1',
        'djangorestframework',
        'python-dateutil',
    ],
    zip_safe=False,
    cmdclass={},
)
