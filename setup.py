from setuptools import setup, find_packages
import os.path


def read_version():
    """Read the library version"""
    path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        'pylastfm',
        '_version.py'
    )
    with open(path) as f:
        exec(f.read())
        return locals()['__version__']


def download_url():
    return 'https://github.com/thesquelched/pylastfm/tarball/{0}'.format(
        read_version())


CHANGELOG = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'CHANGELOG.md')

DESCRIPTION = """\
pylastfm
========

Lasty Last.FM API bindings

.. image:: https://travis-ci.org/thesquelched/pylastfm.svg?branch=master
    :target: https://travis-ci.org/thesquelched/pylastfm

`GitHub Project <https://github.com/thesquelched/pylastfm>`_"""


if __name__ == '__main__':
    try:
        with open(CHANGELOG) as f:
            changelog = f.read().strip()
            suffix = """

Changelog
---------
{0}""".format(changelog)
    except IOError:
        suffix = ''

    setup(
        name='pylastfm',
        version=read_version(),

        description='Lazy Last.FM API bindings',
        long_description=DESCRIPTION + suffix,

        author='Scott Kruger',
        author_email='scott@chojin.org',
        url='https://github.com/thesquelched/pylastfm',
        download_url=download_url(),

        packages=find_packages(exclude=['tests']),
        install_requires=[
            'requests>=2.5.1',
            'six>=1.9.0',
            'python-dateutil>=2.4.0',
            'figgis>=1.6.0',
            'iso3166>=0.7',
        ],

        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: Apache Software License',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Topic :: Software Development :: Libraries',
        ]
    )
