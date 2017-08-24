from setuptools import setup
import re

# Parse version
__version__ = re.search(r'__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
    open('AndorSifReader/__init__.py').read()).group(1)

setup(name = "AndorSifReader",
      version = __version__,
      author = "Ardi Loot",
      url = "https://github.com/ardiloot/AndorSifReader",
      author_email = "ardi.loot@outlook.com",
      packages = ["AndorSifReader"],
      install_requires = ["numpy"])
