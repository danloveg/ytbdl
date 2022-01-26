from setuptools import setup, find_packages

setup(
    name='ytbdl',
    version='0.0.4',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    scripts=[],

    entry_points={
        'console_scripts': [
            'ytbdl = ytbdl.application:main'
        ]
    },

    install_requires=[
        "beets==1.5.0",
        "requests>=2.0.0",
        "yt-dlp>=2021.11.10.1",
    ],

    package_data={
        'ytbdl': ['default_config.yaml']
    },

    python_requires='>=3.6.0',

    zip_safe=False,
    description='Download music with yt-dlp and autotag it with beets',
    author='Daniel Lovegrove',
    author_email='d.lovegrove11@gmail.com',
    license='MIT',
)
