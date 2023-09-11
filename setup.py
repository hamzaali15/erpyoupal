from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in erpyoupal/__init__.py
from erpyoupal import __version__ as version

setup(
	name="erpyoupal",
	version=version,
	description="ERPYoupal",
	author="Youpal",
	author_email="hamza.a@youpalgroup.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
