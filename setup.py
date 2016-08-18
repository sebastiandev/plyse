from setuptools import setup


# Dynamically calculate the version based on plyse.VERSION.
setup(
    name='plyse',
    version=__import__('plyse').__version__,
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
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications',
        'Environment :: OSX Applications',
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
    setup_requires = [
    'pyparsing',
    ],
    install_requires = [
    'pyparsing',
    ],
)
