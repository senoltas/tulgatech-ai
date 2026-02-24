"""
TulgaTech AI - Setup Script
"""

from setuptools import setup, find_packages
from pathlib import Path


# README varsa otomatik oku
BASE_DIR = Path(__file__).parent

readme_file = BASE_DIR / "README.md"

if readme_file.exists():
    long_description = readme_file.read_text(encoding="utf-8")
else:
    long_description = "TulgaTech AI - Akıllı İnşaat Metraj ve Planlama Sistemi"


setup(

    # Paket bilgileri
    name="tulgatech-ai",
    version="1.0.0",

    author="TulgaTech",
    author_email="info@tulgatech.ai",

    description="Akıllı İnşaat Metraj ve Planlama Sistemi",
    long_description=long_description,
    long_description_content_type="text/markdown",

    keywords=[
        "construction",
        "quantity takeoff",
        "dxf",
        "estimation",
        "ai",
        "building"
    ],

    # Paketler
    packages=find_packages(),

    include_package_data=True,

    # Gerekli kütüphaneler
    install_requires=[
        "ezdxf>=1.1.0",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "reportlab>=4.0.0",
        "pillow>=10.0.0",
        "python-dotenv>=1.0.0"
    ],

    # Python versiyonu
    python_requires=">=3.8",

    # PyPI için meta
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Construction"
    ],

    # Komut satırı aracı eklemek istersek hazır
    entry_points={
        "console_scripts": [
            "tulgatech-ai=engine.orchestrator:main"
        ]
    },

)
