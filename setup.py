#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""Setup package
"""
from glob import glob
from os.path import basename, splitext

from setuptools import find_packages
from setuptools import setup


def readme():
    """Read README contents
    """
    with open('README.md', encoding="utf8") as f:
        return f.read()


setup(
    name='glassfibre',
    use_scm_version=True,
    license='MIT License',
    description='A global assessment of fixed broadband infrastructure (glassfibre) - A fiber-to-the-neighborhood approach',
    long_description=readme(),
    long_description_content_type="text/markdown",
    author='Bonface Osoro, Edward Oughton & Fabion Kauker',
    author_email='bosoro@gmu.edu',
    url='https://github.com/Bonface-Osoro/glassfibre',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Utilities',
    ],
    keywords=[
        'fibre','optimization', 'broadband', 'neighbourhood'
    ],
    setup_requires=[
        'setuptools_scm'
    ],
    install_requires=[
        'attrs==23.2.0',
        'certifi==2024.2.2',
        'click==8.1.7',
        'click-plugins==1.1.1',
        'cligj==0.7.2',
        'fiona==1.9.6',
        'geopandas==0.14.3',
        'h3==3.7.7',
        'networkx==3.2.1',
        'numpy==1.26.4',
        'packaging==24.0',
        'pandas==2.2.1',
        'pcst-fast==1.0.10',
        'pybind11==2.12.0',
        'pyproj==3.6.1',
        'python-dateutil==2.9.0.post0',
        'pytz==2024.1',
        'scipy==1.13.0',
        'shapely==2.0.3',
        'six==1.16.0',
        'tzdata==2024.1'
    ],
    entry_points={
        'console_scripts': [
            # eg: 'snkit = snkit.cli:main',
        ]
    },
)