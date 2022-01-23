from setuptools import setup, find_packages

setup(
    name='ytbeetdl',
    version='0.0.3',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    scripts=[],

    entry_points={
        'console_scripts': [
            'ytbdl = ytbeetdl.application:main'
        ]
    },

    install_requires=[
        "beets==1.5.0",
        "requests>=2.0.0",
        "yt-dlp>=2021.11.10.1",
    ],

    package_data={
        'ytbeetdl': ['default_config.yaml']
    },

    python_requires='>=3.5.10',

    zip_safe=False,
    description='Download music with yt-dlp and autotag it with beets',
    author='Daniel Lovegrove',
    author_email='Daniel.Lovegrove@umanitoba.ca',
    license='MIT',
)
