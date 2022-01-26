from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name='ytbdl',
    version='0.0.5',
    author='Daniel Lovegrove',
    author_email='d.lovegrove11@gmail.com',
    description='Download music with yt-dlp and autotag it with beets',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/danloveg/ytbdl',
    license='MIT',

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
)
