from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="bis512",
    version="1.0.0",
    author="Biswajit Saha",
    author_email="biswajit@example.com",
    description="BIS512 - Custom 512-bit cryptographic hash function for blockchain",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/biswajitsaha/bis512",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Security :: Cryptography",
        "Intended Audience :: Developers",
    ],
    python_requires=">=3.6",
    license="MIT",
    keywords="hash, cryptography, blockchain, 512-bit, security, bis512",
    project_urls={
        "Bug Reports": "https://github.com/biswajitsaha/bis512/issues",
        "Source": "https://github.com/biswajitsaha/bis512",
    },
)
