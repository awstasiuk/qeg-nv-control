import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="qegnv",  # Replace with your own username
    version="0.1.0",
    author="Alex Ungar & Andrew Stasiuk",
    author_email="astasiuk@mit.edu",
    description="NV Python Interace for QEG",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/awstasiuk/qeg-nv-control",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
