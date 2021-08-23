from setuptools import setup, find_packages
from pkg_resources import parse_version, get_distribution
import os.path

NAME = "mo_installer"

# Base version (removes any pre, post, a, b or rc element)
try:
    BASE = get_distribution(NAME).base_version
except:
    BASE = "0.0.0"

# In long description, replace "master" in the build status badges
#  with the current version we are building
with open("README.rst") as fd:
    long_description = next(fd).replace("master", BASE)
    long_description += "".join(fd)

setup(
    name=NAME,
    description = "Smoothly integrates mo files in setuptools packaging",
    long_description = long_description,
    packages = find_packages(exclude=["tests"]),
    setup_requires = ["setuptools_scm"],
    use_scm_version = { "write_to": os.path.join(NAME, 'version.py') },
    author="s-ball",
    author_email = "s-ball@laposte.net",
    url = "https://github.com/s-ball/" + NAME,
    license = "MIT License",
    project_urls = {
        "Changelog":
            "https://github.com/s-ball/{}/blob/master/CHANGES.txt".format(
                NAME)
        },
    classifiers = [
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Internationalization",
        ],
    python_requires=">=2.7",
    tests_require = ["pyfakefs"],
    entry_points = {
        "distutils.commands": [
            "build = mo_installer.builder:build",
            "build_mo = mo_installer.builder:build_mo",
            ],
        "distutils.setup_keywords": [
            "locale_src = mo_installer.builder:validate_src",
            "locale_dir = mo_installer.builder:validate_dir",
            ]
        },
    test_suite = "tests",
    )
