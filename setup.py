"""
Setup configuration for Knauf DARC Data Connector package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="knauf-darc-connector",
    version="0.1.0",
    author="Knauf DARC Team",
    author_email="darc@knauf.com",
    description="A Python package for connecting to Microsoft Fabric Lakehouse with flexible authentication methods",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/singhknauf/Knauf-DARC-DataConnector",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    entry_points={
        "console_scripts": [
            "knauf-connector=knauf_darc_connector.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)