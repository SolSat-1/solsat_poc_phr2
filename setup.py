from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="enhanced-solar-rooftop-analysis",
    version="1.0.0",
    author="Solar Analysis Team",
    author_email="contact@solaranalysis.com",
    description="A comprehensive solar energy prediction and visualization system for rooftop analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/enhanced-solar-rooftop-analysis",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=22.0",
            "flake8>=5.0",
            "mypy>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "solar-analysis=main_solar_analysis:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.json"],
    },
    keywords="solar energy rooftop analysis gis visualization prediction",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/enhanced-solar-rooftop-analysis/issues",
        "Source": "https://github.com/yourusername/enhanced-solar-rooftop-analysis",
        "Documentation": "https://github.com/yourusername/enhanced-solar-rooftop-analysis#readme",
    },
)
