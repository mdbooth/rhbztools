from setuptools import setup

setup(
    name = 'bztools',
    version = '0.1',
    packages = ['bztools'],
    python_requires = '>=3.7',
    install_requires = [
        'appdirs',
        'requests',
    ],
    entry_points = {
        'console_scripts': [
            'bzdevelwb = bztools.bzdevelwb:main',
        ]
    },
    test_suite = 'bztools.tests.all_tests',
    tests_require = ['testtools', 'requests-mock', 'ddt'],
)
