import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="automapping",  # Replace with your own username
    version="0.0.1",
    author="Gabriel",
    author_email="gabcpp17@gmail.com",
    description="A utility library to map between dataclass",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GabrielCpp/automapping",
    download_url="https://github.com/GabrielCpp/automapping/archive/v0.0.1.tar.gz",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
