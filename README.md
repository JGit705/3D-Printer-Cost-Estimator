# 3D Printer Cost Estimator

## Project Overview

A comprehensive Streamlit web application that calculates the cost of 3D printing based on STL files. The tool provides both hobbyist and business-oriented cost estimations.

## Features

### 📊 Core Functionality

- STL file upload and parsing
- 3D model preview with interactive visualization
- Volume calculation and bounding box display
- Print time estimation based on model geometry
- Detailed cost breakdown

### 💰 Cost Calculation Features

- Material cost based on volume and density
- Energy cost calculation using printer power consumption
- Support for multiple currencies (GBP, USD, EUR)
- UK electricity rate presets including Economy 7 and Octopus Agile

### 🖨️ Printer Support

- Extensive database of popular 3D printer models
- Power consumption data for major brands:
  - Bambu Lab
  - Prusa Research
  - Creality
  - Anycubic
  - And many more...

### 🏢 Business Mode

- Depreciation calculation
- Labor cost estimation
- Fail rate adjustment
- Shipping cost inclusion
- Custom markup settings
- Comprehensive business pricing model

### ⚙️ Advanced Settings

- Adjustable printer power settings
- Custom electricity rates
- Print parameters configuration
- Markup percentage adjustment

## Technical Details

### Dependencies

```
streamlit
numpy
pandas
trimesh
plotly
```

### Project Structure

```
3d-printer-cost-estimator/
├── app.py              # Main application file
├── utils/
│   ├── stl_parser.py   # STL file processing
│   ├── cost_calculator.py # Cost calculation logic
│   ├── visualisation.py  # Data visualization
│   └── business_logic.py # Business calculations
```

## Installation

1. Clone the repo:

```bash
git clone <repo-url>
cd 3d-printer-cost-estimator
```

2. Create virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the application:

```bash
streamlit run app.py
```

## Usage

1. Select printer make and model
2. Choose material type
3. Upload STL file
4. View cost estimation and breakdown
5. (Optional) Enable business mode for commercial pricing

## Example Usage

- **Input:**
  - STL file: `cube.stl`
  - Material: PLA
  - Print time: 4 hours
  - Power: 120W
  - Electricity rate: $0.15/kWh
- **Output:**
  - Volume: 10 cm³
  - Material cost: $0.25
  - Energy cost: $0.07
  - Total cost (with markup): $0.40
  - Pie chart: Material vs Energy vs Markup

## Future Improvements

### 🎨 UI/UX Enhancements

- Create a more intuitive layout for business settings
- Add progress indicators for calculations
- Improve error message styling and clarity

### ⏱️ Print Time Estimation

- Integrate with slicer engines (PrusaSlicer/Cura) for accurate time estimates
- Account for different infill patterns and densities
- Add support structure calculation

### 💰 Cost Calculation Improvements

- Include failed print statistics
- Factor in support material costs
- Implement material waste calculations

### 🖼️ STL Visualization

- Implement native STL viewer
- Add support for multiple file formats (OBJ, 3MF)
- Add measurements and dimensioning tools

---

_Note: These improvements are planned for future releases and will be implemented based on user feedback and priorities._

_This project provides cost estimation tools for both hobby and business 3D printing applications. All calculations are estimates and should be validated against actual data and costs._
