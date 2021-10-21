#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name="sharepoint-document-library",
    version="1.0.0",
    description="Sharepoint library for downloading and uploading files to sharepoint document library",
    author="RFA",
    classifiers=["Programming Language :: Python :: 3 :: Only"],
    py_modules=["sharepoint_document_library"],
    install_requires=[
        "requests"
    ],
    entry_points='''
    [console_scripts]
    sharepoint-document-library=sharepoint_document_library:main
    ''',
    packages=find_packages(),
    package_data={
        'sharepoint_document_library': [
            ''
        ]
    })
