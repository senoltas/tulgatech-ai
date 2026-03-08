from setuptools import setup, find_packages

setup(
    name="tulgatech-ai",
    version="0.1.0-alpha",
    author="Senol Tas",
    description="Construction Data Intelligence Platform",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.9",
    install_requires=[
        "ezdxf>=1.3.0",
        "shapely>=2.0.0",
        "numpy>=1.24.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
    ],
)