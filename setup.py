import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lcd1602gpio",
    version="0.3.1",
    author="Wei-Li Tang",
    author_email="alextwl@gmail.com",
    description="Use HD44780-compatible 16x2 LCD module via RPi.GPIO",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alextwl/lcd1602gpio",
    py_modules=["lcd1602gpio"],
    install_requires=["RPi.GPIO >= 0.7.0"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Topic :: System :: Hardware",
    ],
)
