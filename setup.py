from setuptools import setup, find_packages


def read_requirements():
    """
    Read requirements from file.
    """
    requirements = tuple()
    try:
        with open('requirements.txt') as req:
            requirements = req.readlines()
    except IOError:
        print('Could not read requirements.txt')

    return requirements

setup(
    name='oh-my-mock',
    version='0.0.1',
    description='HTTP server mock for integration testing',
    license='MIT',
    author='Ilya Khaustov',
    url='https://github.com/ilya-khaustov/oh-my-mock',
    long_description=open('README.md').read(),
    packages=find_packages(),
    install_requires=read_requirements(),
    entry_points={
        'console_scripts': [
            'omm-server = omm.server:main',
        ]
    }
)