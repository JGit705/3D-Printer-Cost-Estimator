# 3D Printer Cost Estimator

## Project Overview

A Streamlit web application that calculates accurate 3D printing costs based on STL files. This tool helps both hobbyists and professionals estimate printing costs by considering material, energy, and printer depreciation.

## Features

### Core Functionality

- STL file upload and processing
- Interactive 3D model preview
- Volume calculation
- Support cost calculation based on support type
- Detailed cost breakdown

### Cost Components

- Material cost based on volume and density
- Energy cost based on printer power consumption
- Printer depreciation calculation
- Support for multiple currencies (GBP, USD, EUR)
- UK electricity rate presets

### Printer Database

- Comprehensive database of popular 3D printers with:
  - Default power consumption
  - Purchase cost
  - Expected maintenance costs
  - Lifetime hours
- Supports major brands including:
  - Bambu Lab
  - Prusa Research
  - Creality
  - Anycubic
  - And more...

### Material Support

- Common 3D printing materials:
  - PLA
  - PETG
  - ABS
  - TPU
  - Nylon
  - PC
  - ASA
  - PVA
  - HIPS
  - Carbon Fiber (PLA-based)
- Material properties included:
  - Density
  - Cost per kg
  - Available diameters

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/3d-printer-cost-estimator.git
cd 3d-printer-cost-estimator
```

2. Create and activate virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Mac/Linux
```

3. Install required packages:

```bash
pip install streamlit pandas numpy trimesh plotly
```

4. Run the application:

```bash
streamlit run app.py
```

## How to Use

1. **Launch the Application**

   - Run the application using `streamlit run app.py`
   - The web interface will open in your default browser

2. **Configure Settings**

   - Select your currency
   - Choose electricity rate
   - Set markup percentage
   - Select printer make and model

3. **Upload STL File**

   - Drag and drop your STL file or use the file browser
   - The 3D preview will appear automatically

4. **Enter Print Details**

   - Input print duration from your slicer
   - Select support type if needed:
     - None: No additional cost
     - Regular: +10-20% material cost
     - Tree: +5-15% material cost
     - Soluble: +30-50% material cost

5. **View Results**
   - See total cost summary
   - Review detailed cost breakdown
   - Check material and energy costs
   - View printer depreciation impact

## Advanced Settings

- Custom material costs
- Printer-specific configurations:
  - Purchase cost
  - Planned upgrades
  - Expected maintenance
  - Lifetime hours
  - Power consumption

## Technical Requirements

- Python 3.7+
- Streamlit
- NumPy
- Pandas
- Trimesh
- Plotly

## Current Limitations

- Print time must be manually entered from slicer
- Support material calculations are estimates
- Electricity costs based on average consumption

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

---

_Note: This tool provides cost estimates based on input parameters. Actual costs may vary depending on specific printer settings, environmental conditions, and material properties._
