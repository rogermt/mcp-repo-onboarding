from setuptools import setup

setup(
    name="example-package",
    version="0.1.0",
    description="Example setuptools package",
    packages=["example"],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
    ],
)
