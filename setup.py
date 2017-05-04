import os
import re
from setuptools import setup


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("^__version__ = ['\"]([^'\"]+)['\"]", init_py, re.MULTILINE).group(1)


setup(
    name='plyse',
    setup_requires=[
        'pyparsing',
    ],
    install_requires=[
        'pyparsing',
    ],
    version=get_version('plyse'),
    url='https://github.com/sebastiandev/plyse',
    author='Sebastian Packmann',
    author_email='devsebas@gmail.com',
    description=('A fully extensible query parser inspired on the lucene and gmail sintax'),
    license='MIT',
    package_dir={
        'plyse': 'plyse',
        'plyse.expressions': 'plyse/expressions',
        'plyse.tests': 'plyse/tests',
    },
    packages=['plyse', 'plyse.expressions', 'plyse.tests'],
    test_suite='tests',
    keywords="search query parser lucene gmail syntax grammar",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
