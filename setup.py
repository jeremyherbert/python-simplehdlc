import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="simplehdlc",
    version="0.1.0",
    author="Jeremy Herbert",
    author_email="jeremy.006@gmail.com",
    description="A python implementation of the simplehdlc packet encoder/parser",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jeremyherbert/python-simplehdlc",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)