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


if __name__ == '__main__':
    setup(
        name='pylastfm',
        version=read_version(),
        packages=find_packages(exclude=['tests']),
        install_requires=[
            'requests>=2.5.1',
            'six>=1.9.0',
            'python-dateutil>=2.4.0',
            'figgis>=1.6.0',
        ],
    )
