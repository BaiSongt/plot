from setuptools import setup, find_packages

setup(
    name="scientific-analysis-tool",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "PySide6>=6.4.0",
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "matplotlib>=3.4.0",
        "scipy>=1.7.0",
        "scikit-learn>=1.0.0",
        "statsmodels>=0.13.0",
        "h5py>=3.6.0",
        "openpyxl>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "scientific-analysis=scientific_analysis.main:main",
        ],
    },
    python_requires=">=3.8",
)
