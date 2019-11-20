from setuptools import setup

setup(
    name = 'rhbztools',
    version = '0.1',
    packages = ['rhbztools'],
    python_requires = '>=3.7',
    install_requires = [
        'appdirs',
        'requests',
        'tatsu',
    ],
    entry_points = {
        'console_scripts': [
            'bzdevelwb = rhbztools.bzdevelwb:main',
        ]
    },
    test_suite = 'rhbztools.tests.all_tests',
    tests_require = ['testtools', 'requests-mock', 'ddt'],
)
