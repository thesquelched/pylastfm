from setuptools import setup, find_packages

if __name__ == '__main__':
    setup(
        name='pylastfm',
        version='0.1',
        packages=find_packages(exclude=['tests']),
        install_requires=[
            'requests>=2.5.1',
            'six>=1.9.0',
            'python-dateutil>=2.4.0',
            'figgis>=1.6.0',
        ],
    )
