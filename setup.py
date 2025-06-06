from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dnarecon",
    version="0.1.0",
    author="DNARecon Team",
    author_email="contact@dnarecon.com",
    description="Outil CLI pour l'analyse comportementale des applications web",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/votre-username/dnarecon",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Security",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
        "pyyaml>=6.0.1",
        "python-dotenv>=1.0.0",
        "colorama>=0.4.6",
        "tqdm>=4.66.1",
        "beautifulsoup4>=4.12.2",
        "aiohttp>=3.9.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "pytest-asyncio>=0.21.1",
            "black>=23.11.0",
            "flake8>=6.1.0",
            "mypy>=1.7.1",
            "isort>=5.12.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "dnarecon=dnarecon:main",
        ],
    },
) 