""" Install atomcsvreformatter """
from setuptools import setup, find_packages

setup(
    name='dlalbum',
    version='0.0.1',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    scripts=[],

    entry_points={
        'console_scripts': [
            'dlalbum = dlalbum.application:main'
        ]
    },

    install_requires=[
        "beets>=1.4.9",
        "confuse>=1.3.0",
        "youtube-dl>=2020.11.17",
    ],

    package_data={
        'dlalbum': ['default_config.yaml']
    },

    zip_safe=False,
    description='Download music from youtube-dl and autotag with beets',
    author='Daniel Lovegrove',
    author_email='Daniel.Lovegrove@umanitoba.ca',
    license='MIT',
)
