from setuptools import setup, find_packages
import sys, os

version = '0.7.1'

setup(name='crank',
      version=version,
      description="Generalization of dispatch mechanism for use across frameworks.",
      long_description="""\
""",
      classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python',
      ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Christopher Perkins',
      author_email='chris@percious.com',
      url='https://github.com/TurboGears/crank',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      extras_require={
           # Used by Travis and Coverage due to setup.py nosetests
           # causing a coredump when used with coverage
           'testing': ['webob'],
      },
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
