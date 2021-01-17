import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent

VERSION = '0.1.0'
PACKAGE_NAME = 'ksalib'
AUTHOR = 'andyyeyeye'
AUTHOR_EMAIL = 'andyye.jongcye@gmail.com'
URL = 'https://github.com/andyyeyeye/ksalib'

LICENSE = 'The MIT License'
DESCRIPTION = 'A library for KSA'
LONG_DESCRIPTION = open('README.md', 'r', encoding='UTF8').read()
LONG_DESC_TYPE = "text/markdown"

INSTALL_REQUIRES = [
      'requests',
      'bs4',
      'html2text',
]

setup(name=PACKAGE_NAME,
      version=VERSION,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      long_description_content_type=LONG_DESC_TYPE,
      author=AUTHOR,
      license=LICENSE,
      author_email=AUTHOR_EMAIL,
      url=URL,
      install_requires=INSTALL_REQUIRES,
      packages=find_packages()
      )