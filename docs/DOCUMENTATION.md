\# TulgaTech AI - Complete Documentation



\*\*Version\*\*: 1.0.0  

\*\*Status\*\*: Production Ready  

\*\*Last Updated\*\*: March 9, 2026



---



\## 📚 Table of Contents



1\. \[Introduction](#introduction)

2\. \[Architecture](#architecture)

3\. \[Installation](#installation)

4\. \[API Reference](#api-reference)

5\. \[Web Dashboard](#web-dashboard)

6\. \[Development Guide](#development-guide)

7\. \[Troubleshooting](#troubleshooting)



---



\## Introduction



TulgaTech AI is a comprehensive construction data intelligence platform that analyzes architectural drawings (DXF/DWG) to extract structural information, spatial data, and cost estimates.



\### Key Features



\- \*\*Scale Detection\*\*: Automatic scale detection from DIMENSION entities

\- \*\*Wall Detection\*\*: Intelligent wall and structural element identification

\- \*\*Room Analysis\*\*: Spatial analysis and room connectivity detection

\- \*\*Cost Estimation\*\*: Detailed material and labor cost breakdown

\- \*\*3D Modeling\*\*: Generate 3D models from 2D analysis

\- \*\*Schedule Optimization\*\*: Project timeline planning

\- \*\*API Server\*\*: RESTful API for integration

\- \*\*Web Dashboard\*\*: Interactive visualization interface



\### Target Users



\- Turkish SME contractors

\- Site managers and project supervisors

\- Construction firms and engineering companies

\- Architecture offices



---



\## Architecture



\### System Components



\#### Core Layer

\- \*\*Scale Manager\*\*: Scale detection and management

\- \*\*Geometry\*\*: Geometric calculations and utilities

\- \*\*Types\*\*: Data structures and models



\#### I/O Layer

\- \*\*DXF Loader\*\*: DXF/DWG file loading

\- \*\*Segment Extractor\*\*: Geometric segment extraction

\- \*\*Normalizer\*\*: Entity normalization



\#### Analysis Engines

\- \*\*Wall Detector\*\*: Structural element detection

\- \*\*Layer Profiler\*\*: Layer-based analysis

\- \*\*Cluster Detector\*\*: Spatial clustering

\- \*\*Area Calculator\*\*: Area computation

\- \*\*Room Detector\*\*: Space identification

\- \*\*Topology Analyzer\*\*: Connectivity analysis

\- \*\*Frame Detector\*\*: Sheet segmentation



\#### Advanced Features

\- \*\*Material Estimator\*\*: Cost and material estimation

\- \*\*3D Model Generator\*\*: 3D model creation

\- \*\*Schedule Optimizer\*\*: Project scheduling

\- \*\*Cost Breakdown Analyzer\*\*: Detailed cost analysis

\- \*\*PDF Exporter\*\*: Report generation

\- \*\*Report Generator\*\*: Analysis reporting



\#### Integration

\- \*\*API Server\*\*: REST API interface

\- \*\*Web Dashboard\*\*: Web-based UI

\- \*\*CLI\*\*: Command-line interface



---



\## Installation



\### Requirements

\- Python 3.9+

\- Windows/Linux/macOS



\### Quick Start

```bash

\# Clone repository

git clone https://github.com/senoltas/tulgatech-ai.git

cd tulgatech-ai



\# Create virtual environment

python -m venv venv

source venv/bin/activate  # Windows: venv\\Scripts\\activate



\# Install dependencies

pip install -r requirements.txt



\# Install in development mode

pip install -e .

```



\### Verify Installation

```bash

pytest tests/ -v

```



Expected: All tests pass (186+)



---



\## API Reference



\### Health Check

```

GET /api/v1/health

```



\*\*Response (200)\*\*:

```json

{

&nbsp; "status": "healthy",

&nbsp; "api\_version": "1.0.0",

&nbsp; "is\_running": true

}

```



\### Analyze File

```

POST /api/v1/analyze

Content-Type: application/json



{

&nbsp; "file\_path": "path/to/project.dxf"

}

```



\*\*Response (201)\*\*:

```json

{

&nbsp; "analysis\_id": "ANL\_001",

&nbsp; "status": "queued",

&nbsp; "file\_path": "path/to/project.dxf",

&nbsp; "created": "2026-03-09T20:54:00"

}

```



\### Get Analysis Result

```

GET /api/v1/analysis/{id}

```



\*\*Response (200)\*\*:

```json

{

&nbsp; "analysis\_id": "ANL\_001",

&nbsp; "scale": {...},

&nbsp; "walls": \[...],

&nbsp; "rooms": \[...],

&nbsp; "stats": {...}

}

```



---



\## Web Dashboard



\### Pages



1\. \*\*Overview\*\*: Key statistics and trends

2\. \*\*Projects\*\*: Project list and management

3\. \*\*Analytics\*\*: Detailed analysis and visualizations



\### Features



\- Real-time data refresh

\- Responsive design

\- Light/Dark theme support

\- Interactive charts

\- Building footprint maps

\- Cost distribution analysis



\### Accessing Dashboard

```

http://localhost:8000/dashboard

```



---



\## Development Guide



\### Project Structure

```

tulgatech-ai/

├── src/tulgatech/

│   ├── core/          (3 modules)

│   ├── io/            (3 modules)

│   ├── engine/        (12 modules)

│   ├── cli/           (1 module)

│   └── reporting/     (1 module)

├── tests/             (186+ tests)

├── docs/              (documentation)

├── config/            (configuration)

└── data/              (test data)

```



\### Adding New Modules



1\. Create module in appropriate subdirectory

2\. Write comprehensive tests in `tests/`

3\. Update imports in `\_\_init\_\_.py`

4\. Add to documentation

5\. Run tests: `pytest tests/ -v`

6\. Commit and push



\### Coding Standards



\- Use type hints throughout

\- 100% test coverage for new code

\- Follow PEP 8 style guide

\- Document all public methods

\- Use descriptive variable names



\### Running Tests

```bash

\# All tests

pytest tests/ -v



\# Specific module

pytest tests/test\_wall\_detector.py -v



\# With coverage

pytest tests/ --cov=src/tulgatech

```



---



\## Configuration



\### Default Parameters



Edit `config/assumptions.json`:

```json

{

&nbsp; "wall\_thickness": 0.25,

&nbsp; "wall\_height": 3.0,

&nbsp; "door\_width": 0.90,

&nbsp; "window\_height": 1.50,

&nbsp; ...

}

```



\### Environment Variables

```bash

TULGATECH\_API\_HOST=0.0.0.0

TULGATECH\_API\_PORT=8000

TULGATECH\_LOG\_LEVEL=INFO

```



---



\## Troubleshooting



\### Issue: Import Error



\*\*Solution\*\*: Ensure virtual environment is activated and package installed:

```bash

pip install -e .

```



\### Issue: Test Failures



\*\*Solution\*\*: Update dependencies:

```bash

pip install --upgrade -r requirements.txt

```



\### Issue: DXF File Not Recognized



\*\*Solution\*\*: Verify file format and ensure scale is detectable:

\- Check file with DXF viewer

\- Ensure DIMENSION entities present for scale detection



\### Issue: API Connection Failed



\*\*Solution\*\*: Verify server is running:

```bash

python -c "from tulgatech.engine.api\_server import APIServer; s = APIServer(); print(s.start())"

```



---



\## Performance Metrics



| Task | Duration | Status |

|------|----------|--------|

| DXF Loading | < 2 sec | ✅ |

| Scale Detection | < 1 sec | ✅ |

| Wall Detection | < 2 sec | ✅ |

| Full Pipeline | ~8 sec | ✅ |



---



\## Support \& Contribution



\### Reporting Issues



Submit issues on GitHub with:

\- Step-by-step reproduction

\- Expected vs actual behavior

\- System information



\### Contributing



1\. Fork repository

2\. Create feature branch: `git checkout -b feature/xyz`

3\. Write tests

4\. Submit pull request



---



\## License



MIT License - See LICENSE file



---



\## Version History



\### v1.0.0 (March 9, 2026)

\- ✅ Complete Phase 1-4

\- ✅ 24 production modules

\- ✅ 186+ tests (100% pass)

\- ✅ API server

\- ✅ Web dashboard

\- ✅ Production ready



---



\## Contact \& Support



\*\*Project Owner\*\*: Senol Tas  

\*\*Email\*\*: senol@tulgatech.ai  

\*\*Repository\*\*: https://github.com/senoltas/tulgatech-ai  

\*\*Status\*\*: Active Development



---



\*\*TulgaTech AI - Building Intelligence into Construction\*\* 🏗️

