\# TulgaTech AI - Construction Data Intelligence Platform



\*\*Advanced AEC (Architecture/Engineering/Construction) Analysis Engine\*\*



!\[Status](https://img.shields.io/badge/status-Phase%201%20Complete-brightgreen)

!\[Tests](https://img.shields.io/badge/tests-96%2B%20passed-brightgreen)

!\[Python](https://img.shields.io/badge/python-3.9%2B-blue)

!\[License](https://img.shields.io/badge/license-MIT-blue)



---



\## 🎯 Overview



TulgaTech AI is a cutting-edge construction data intelligence platform that analyzes architectural drawings (DXF/DWG files) to extract:



\- \*\*Structural Elements\*\*: Walls, columns, beams with precise measurements

\- \*\*Spatial Analysis\*\*: Rooms, areas, zones with calculated dimensions

\- \*\*Cost Estimation\*\*: Material quantities and preliminary budgeting

\- \*\*Project Planning\*\*: Resource allocation and timeline optimization



Perfect for \*\*Turkish SME contractors, site managers, and construction firms\*\*.



---



\## ✨ Key Features



\### Core Capabilities

\- 🔍 \*\*Intelligent DXF/DWG parsing\*\* with automatic entity normalization

\- 📏 \*\*Scale detection\*\* from DIMENSION entities with confidence scoring

\- 🧱 \*\*Wall detection\*\* using geometric analysis and layer profiling

\- 📐 \*\*Area calculation\*\* from segment clusters and polygon analysis

\- 🏗️ \*\*Room detection\*\* with perimeter and area computation

\- 📊 \*\*Layer profiling\*\* to identify architectural elements by CAD convention

\- 🎯 \*\*Cluster detection\*\* using grid-based spatial analysis

\- 📋 \*\*Report generation\*\* with summary and detailed technical output



\### Quality Metrics

\- ✅ \*\*100% test coverage\*\* (96+ unit + integration tests)

\- 🔒 \*\*Type-safe\*\* with Python type hints throughout

\- 🏗️ \*\*Modular architecture\*\* for easy extension

\- 📦 \*\*Production-ready\*\* with clean separation of concerns



---



\## 📦 Installation



\### Requirements

\- Python 3.9+

\- pip or conda



\### Quick Start

```bash

\# Clone repository

git clone https://github.com/senoltas/tulgatech-ai.git

cd tulgatech-ai



\# Create virtual environment

python -m venv venv

source venv/bin/activate  # On Windows: venv\\Scripts\\activate



\# Install dependencies

pip install -r requirements.txt



\# Install in development mode

pip install -e .

```



---



\## 🚀 Usage



\### Command Line Interface

```bash

\# Analyze a DXF file

tulgatech project\_plan.dxf



\# Output includes:

\# - Scale detection results

\# - Wall detection summary

\# - Room analysis

\# - Area calculations

\# - Quality metrics

```



\### Python API

```python

from tulgatech.engine.orchestrator import TulgaTechOrchestrator



\# Initialize orchestrator

orch = TulgaTechOrchestrator()



\# Process DXF file

result = orch.process("my\_project.dxf")



\# Access results

print(f"Scale: {result\['scale']\['value']}")

print(f"Walls found: {len(result\['walls'])}")

print(f"Total wall length: {result\['stats']\['total\_wall\_length\_m']:.2f}m")

```



---



\## 📁 Project Structure

```

tulgatech-ai/

├── src/tulgatech/

│   ├── core/                 # Core modules

│   │   ├── types.py         # Data structures

│   │   ├── geometry.py      # Geometric utilities

│   │   └── scale\_manager.py # Scale detection

│   ├── io/                   # Input/Output

│   │   ├── dxf\_loader.py    # DXF file loading

│   │   ├── segment\_extractor.py  # Segment extraction

│   │   └── normalizer.py    # Entity normalization

│   ├── engine/              # Analysis engines

│   │   ├── wall\_detector.py      # Wall detection

│   │   ├── layer\_profiler.py     # Layer analysis

│   │   ├── cluster\_detector.py   # Spatial clustering

│   │   ├── area\_calculator.py    # Area computation

│   │   ├── room\_detector.py      # Room detection

│   │   ├── orchestrator.py       # Main pipeline

│   │   └── report\_generator.py   # Report generation

│   ├── cli/                 # Command-line interface

│   │   └── main.py

│   └── reporting/           # Report generation (legacy)

│       └── generator.py

├── tests/                    # Test suite (96+ tests)

│   ├── test\_\*.py           # Unit tests

│   └── test\_integration\_dxf.py  # Integration tests

├── data/                     # Test data (DXF files)

├── config/

│   └── assumptions.json     # Default parameters

├── requirements.txt         # Dependencies

├── setup.py                # Package setup

└── README.md               # This file

```



---



\## 🧪 Testing



\### Run All Tests

```bash

pytest tests/ -v

```



\### Run Specific Test Category

```bash

\# Unit tests only

pytest tests/test\_\*.py -v --ignore=tests/test\_integration\_dxf.py



\# Integration tests

pytest tests/test\_integration\_dxf.py -v

```



\### Test Coverage

```bash

pytest tests/ --cov=src/tulgatech --cov-report=html

```



\*\*Current Status\*\*: ✅ 96+ tests passing (100% pass rate)



---



\## 🏗️ Architecture



\### Module Breakdown



| Module | Purpose | Status |

|--------|---------|--------|

| \*\*core\*\* | Types, geometry, scale detection | ✅ Complete |

| \*\*io\*\* | DXF loading, normalization, segment extraction | ✅ Complete |

| \*\*engine\*\* | Wall, room, area, cluster detection | ✅ Complete |

| \*\*cli\*\* | Command-line interface | ✅ Complete |

| \*\*reporting\*\* | Report generation | ✅ Complete |



\## 🎨 System Architecture



!\[TulgaTech AI Architecture](docs/architecture.png)



The system follows a modular pipeline approach:

\- \*\*Input Layer\*\*: DXF/DWG file intake

\- \*\*Processing Layer\*\*: Parsing, normalization, analysis

\- \*\*Intelligence Layer\*\*: Detection engines (walls, rooms, areas)

\- \*\*Output Layer\*\*: Reports, cost estimation, project planning



\### Data Flow

```

DXF File

&nbsp;  ↓

\[DXF Loader] → Load \& parse

&nbsp;  ↓

\[Normalizer] → Standardize entities

&nbsp;  ↓

\[Scale Detector] → Detect scale from DIMENSION

&nbsp;  ↓

\[Segment Extractor] → Extract geometric primitives

&nbsp;  ↓

\[Layer Profiler] → Analyze by CAD layer

&nbsp;  ↓

\[Wall Detector] → Identify structural elements

&nbsp;  ↓

\[Cluster Detector] → Group spatial entities

&nbsp;  ↓

\[Area Calculator] → Compute areas

&nbsp;  ↓

\[Room Detector] → Identify spaces

&nbsp;  ↓

\[Report Generator] → Create output report

&nbsp;  ↓

Result (JSON/Summary)

```



---



\## 📊 Performance



\- \*\*DXF Loading\*\*: < 2 seconds for typical project files

\- \*\*Scale Detection\*\*: < 1 second

\- \*\*Wall Detection\*\*: < 2 seconds

\- \*\*Full Pipeline\*\*: ~8 seconds per file (with all analyses)



\*Benchmarks on standard project (10,000+ entities)\*



---



\## 🔧 Configuration



Edit `config/assumptions.json` to customize:

```json

{

&nbsp; "wall\_thickness": 0.25,

&nbsp; "wall\_height": 3.0,

&nbsp; "door\_width": 0.90,

&nbsp; "door\_height": 2.10,

&nbsp; "window\_height": 1.50,

&nbsp; "paint\_waste\_factor": 0.15,

&nbsp; "flooring\_waste": 0.10,

&nbsp; ...

}

```



---



\## 📋 Phase 1 Checklist



\- ✅ Core infrastructure (types, geometry, scale)

\- ✅ DXF I/O pipeline (loading, normalization, segment extraction)

\- ✅ Wall detection engine

\- ✅ Layer profiling and analysis

\- ✅ Cluster detection (spatial grouping)

\- ✅ Area calculation

\- ✅ Room detection

\- ✅ Report generation

\- ✅ CLI interface

\- ✅ Comprehensive test suite (96+ tests)

\- ✅ Integration tests with real DXF files



---



\## 🚧 Phase 2 Roadmap



\- \[ ] Sheet segmentation (multiple plans per file)

\- \[ ] Advanced room topology

\- \[ ] Door/window detection

\- \[ ] Material estimation

\- \[ ] 3D model generation

\- \[ ] PDF report export

\- \[ ] Web interface

\- \[ ] API server



---



\## 📞 Support



\### For Issues

1\. Check \[GitHub Issues](https://github.com/senoltas/tulgatech-ai/issues)

2\. Review test files in `tests/` for usage examples

3\. Check configuration in `config/assumptions.json`



\### For Contributions

\- Follow PEP 8 style guide

\- Add tests for new features

\- Update documentation

\- Create feature branch from `develop`



---



\## 📄 License



MIT License - See LICENSE file for details



---



\## 👨‍💼 About



\*\*TulgaTech AI\*\* is developed as part of Cumhuriyet Üniversitesi Teknokent (Teknokent Sivas) initiative to advance construction technology in Turkey.



\*\*Developer\*\*: Senol Tas  

\*\*Repository\*\*: https://github.com/senoltas/tulgatech-ai  

\*\*Status\*\*: Phase 1 Complete (March 2026)



---



\## 🎓 Technical Stack



\- \*\*Language\*\*: Python 3.13

\- \*\*DXF Processing\*\*: ezdxf 1.4.3

\- \*\*Geometry\*\*: shapely 2.1.2

\- \*\*Data Validation\*\*: pydantic 2.12.5

\- \*\*Testing\*\*: pytest 9.0.2

\- \*\*Type Checking\*\*: mypy



---



\*\*Last Updated\*\*: March 8, 2026  

\*\*Version\*\*: 0.1.0-alpha

