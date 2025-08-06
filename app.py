import streamlit as st
import numpy as np
import pandas as pd
from utils.stl_parser import parse_3d_file
from utils.cost_calculator import (
    calc_material_cost, calc_energy_cost, calc_total_cost, get_materials
)

# Add near the top of your app
if 'advanced_settings' not in st.session_state:
    st.session_state.advanced_settings = False

st.set_page_config(page_title="3D Printer Cost Estimator", layout="centered")
st.title("3D Printer Cost Estimator")

# --- Currency Selector ---
currency_options = {
    'GBP (£)': {'symbol': '£', 'rate': 1.0},
    'USD ($)': {'symbol': '$', 'rate': 1.27},
    'EUR (€)': {'symbol': '€', 'rate': 1.17}
}
# --- UK Electricity Rates ---
uk_rates = {
    "Standard Rate (0.34£/kWh)": 0.34,
    "Economy 7 Day (0.39£/kWh)": 0.39,
    "Economy 7 Night (0.20£/kWh)": 0.20,
    "Smart Meter Peak (0.40£/kWh)": 0.40,
    "Smart Meter Off-Peak (0.25£/kWh)": 0.25,
    "Custom": None
}
# --- 3D Printer Power Mapping ---
printer_power_dict = {
    "Bambu Lab": {
        "A1": 100, "A1 Mini": 100, "P1P": 85, "P1S": 85, "X1 Carbon": 95, "X1E": 95
    },
    "Prusa Research": {
        "Prusa MK4": 90, "Prusa MK3S+": 90, "Prusa Mini+": 90, "Prusa XL": 130
    },
    "Creality": {
        "Ender-3 V3 SE": 110, "Ender-3 V3 NEO": 110, "Ender-3 V3 S1": 110, "Ender-5 Plus": 130, "K1": 150, "K1 Max": 150, "CR-10 Smart Pro": 150, "CR-M4": 150
    },
    "Anycubic": {
        "Kobra 2": 100, "Kobra 2 Pro": 100, "Kobra 2 Max": 100, "Vyper": 90, "Chiron": 130
    },
    "Elegoo": {
        "Neptune 4": 100, "Neptune 4 Pro": 100, "Neptune 4 Max":
          100, "Neptune 3 Plus": 100
    },
    "Artillery": {
        "Sidewinder X2": 130, "Sidewinder X3": 130, "Genius Pro": 110
    },
    "Raise3D": {
        "E2": 200, "Pro2": 200, "Pro3": 200
    },
    "Flashforge": {
        "Adventurer 5M": 130, "Creator Pro 2": 130, "Guider IIs": 200
    },
    "Snapmaker": {
        "Snapmaker 2.0 A150": 150, "Snapmaker 2.0 A250": 150, "Snapmaker 2.0 A350": 150, "Snapmaker Artisan": 200
    },
    "Qidi Tech": {
        "X-Smart 3": 110, "X-Plus 3": 200, "X-Max 3": 200
    },
    "Ultimaker": {
        "Ultimaker S3": 250, "Ultimaker S5": 250
    },
    "Voxelab": {
        "Aquila": 110, "Aquila X2": 110, "Aquila D1": 110
    },
    "MakerBot": {
        "Sketch": 100, "Method X": 250
    },
    "LulzBot": {
        "Mini 2": 130, "Taz Workhorse": 200, "Taz Pro": 200
    }
}
# --- 3D Printer Selection (Make → Model) ---
printer_dict = {
    "Bambu Lab": ["A1", "A1 Mini", "P1P", "P1S", "X1 Carbon", "X1E"],
    "Prusa Research": ["Prusa MK4", "Prusa MK3S+", "Prusa Mini+", "Prusa XL"],
    "Creality": ["Ender-3 V3 SE / NEO / S1", "Ender-5 Plus", "K1", "K1 Max", "CR-10 Smart Pro", "CR-M4"],
    "Anycubic": ["Kobra 2 / 2 Pro / 2 Max", "Vyper", "Chiron"],
    "Elegoo": ["Neptune 4", "Neptune 4 Pro", "Neptune 4 Max", "Neptune 3 Plus"],
    "Artillery": ["Sidewinder X2", "Sidewinder X3", "Genius Pro"],
    "Raise3D": ["E2", "Pro2", "Pro3"],
    "Flashforge": ["Adventurer 5M", "Creator Pro 2", "Guider IIs"],
    "Snapmaker": ["Snapmaker 2.0 A150 / A250 / A350", "Snapmaker Artisan"],
    "Qidi Tech": ["X-Smart 3", "X-Plus 3", "X-Max 3"],
    "Ultimaker": ["Ultimaker S3", "Ultimaker S5"],
    "Voxelab": ["Aquila", "Aquila X2", "Aquila D1"],
    "MakerBot": ["Sketch", "Method X"],
    "LulzBot": ["Mini 2", "Taz Workhorse", "Taz Pro"]
}
# Build a display list for models with power values
printer_display_dict = {}
for make, models in printer_dict.items():
    display_models = []
    for m in models:
        # For grouped models, pick the first matching model in the power dict
        if "/" in m:
            # Split by / and strip whitespace
            submodels = [s.strip() for s in m.split("/")]
            # Find the first submodel with a power value
            power = None
            for sub in submodels:
                if sub in printer_power_dict.get(make, {}):
                    power = printer_power_dict[make][sub]
                    break
            # If not found, fallback to None
        else:
            power = printer_power_dict.get(make, {}).get(m)
        if power:
            display_models.append(f"{m} ({power}W)")
        else:
            display_models.append(m)
    printer_display_dict[make] = display_models

# --- Material Properties ---
MATERIALS = {
    "PLA": {
        "density": 1.24,       # g/cm³
        "cost_per_kg": 25.00,  # £/kg
        "diameters": [1.75, 2.85]
    },
    "PETG": {
        "density": 1.27,
        "cost_per_kg": 30.00,
        "diameters": [1.75, 2.85]
    },
    "ABS": {
        "density": 1.01,
        "cost_per_kg": 20.00,
        "diameters": [1.75, 2.85]
    },
    "TPU": {
        "density": 1.21,
        "cost_per_kg": 35.00,
        "diameters": [1.75, 2.85]
    },
    "Nylon": {
        "density": 1.02,
        "cost_per_kg": 100.00,
        "diameters": [1.75, 2.85]
    },
    "PC": {
        "density": 1.19,
        "cost_per_kg": 40.00,
        "diameters": [1.75, 2.85]
    },
    "ASA": {
        "density": 1.08,
        "cost_per_kg": 30.00,
        "diameters": [1.75, 2.85]
    },
    "PVA": {
        "density": 1.23,
        "cost_per_kg": 40.00,
        "diameters": [1.75]  # Usually only in 1.75 mm for support material
    },
    "HIPS": {
        "density": 1.04,
        "cost_per_kg": 35.00,
        "diameters": [1.75, 2.85]  # Some brands do both, often used for supports
    },
    "Carbon Fiber (PLA‑based)": {
        "density": 1.19,
        "cost_per_kg": 65.00,
        "diameters": [1.75, 2.85]
    }
}

# --- Printer Details Dictionary ---
printer_details_dict = {
    "Bambu Lab": {
        "A1": {"cost": 499, "upgrades": 50, "maintenance": 50, "lifetime_hours": 5000, "avg_power_watts": 100, "cost_per_kwh": 0.15},
        "A1 Mini": {"cost": 399, "upgrades": 50, "maintenance": 50, "lifetime_hours": 5000, "avg_power_watts": 100, "cost_per_kwh": 0.15},
        "P1P": {"cost": 599, "upgrades": 75, "maintenance": 50, "lifetime_hours": 5000, "avg_power_watts": 85, "cost_per_kwh": 0.15},
        "P1S": {"cost": 699, "upgrades": 75, "maintenance": 50, "lifetime_hours": 5000, "avg_power_watts": 85, "cost_per_kwh": 0.15},
        "X1 Carbon": {"cost": 1199, "upgrades": 100, "maintenance": 100, "lifetime_hours": 5000, "avg_power_watts": 95, "cost_per_kwh": 0.15},
        "X1E": {"cost": 1399, "upgrades": 100, "maintenance": 100, "lifetime_hours": 5000, "avg_power_watts": 95, "cost_per_kwh": 0.15}
    },
    "Prusa Research": {
        "Prusa MK4": {"cost": 799, "upgrades": 100, "maintenance": 75, "lifetime_hours": 5000, "avg_power_watts": 90, "cost_per_kwh": 0.15},
        "Prusa MK3S+": {"cost": 749, "upgrades": 100, "maintenance": 75, "lifetime_hours": 5000, "avg_power_watts": 90, "cost_per_kwh": 0.15},
        "Prusa Mini+": {"cost": 399, "upgrades": 50, "maintenance": 50, "lifetime_hours": 5000, "avg_power_watts": 90, "cost_per_kwh": 0.15},
        "Prusa XL": {"cost": 1999, "upgrades": 200, "maintenance": 150, "lifetime_hours": 5000, "avg_power_watts": 130, "cost_per_kwh": 0.15}
    },
    "Creality": {
        "Ender-3 V3 SE": {"cost": 229, "upgrades": 100, "maintenance": 50, "lifetime_hours": 4000, "avg_power_watts": 110, "cost_per_kwh": 0.15},
        "Ender-3 V3 NEO": {"cost": 279, "upgrades": 100, "maintenance": 50, "lifetime_hours": 4000, "avg_power_watts": 110, "cost_per_kwh": 0.15},
        "Ender-3 V3 S1": {"cost": 329, "upgrades": 100, "maintenance": 50, "lifetime_hours": 4000, "avg_power_watts": 110, "cost_per_kwh": 0.15},
        "Ender-5 Plus": {"cost": 579, "upgrades": 150, "maintenance": 75, "lifetime_hours": 4000, "avg_power_watts": 130, "cost_per_kwh": 0.15},
        "K1": {"cost": 399, "upgrades": 100, "maintenance": 75, "lifetime_hours": 4000, "avg_power_watts": 150, "cost_per_kwh": 0.15},
        "K1 Max": {"cost": 599, "upgrades": 150, "maintenance": 75, "lifetime_hours": 4000, "avg_power_watts": 150, "cost_per_kwh": 0.15},
        "CR-10 Smart Pro": {"cost": 499, "upgrades": 150, "maintenance": 75, "lifetime_hours": 4000, "avg_power_watts": 150, "cost_per_kwh": 0.15},
        "CR-M4": {"cost": 999, "upgrades": 200, "maintenance": 100, "lifetime_hours": 4000, "avg_power_watts": 150, "cost_per_kwh": 0.15}
    },
    "Anycubic": {
        "Kobra 2": {"cost": 299, "upgrades": 50, "maintenance": 50, "lifetime_hours": 4000, "avg_power_watts": 100, "cost_per_kwh": 0.15},
        "Kobra 2 Pro": {"cost": 349, "upgrades": 50, "maintenance": 50, "lifetime_hours": 4000, "avg_power_watts": 100, "cost_per_kwh": 0.15},
        "Kobra 2 Max": {"cost": 399, "upgrades": 50, "maintenance": 50, "lifetime_hours": 4000, "avg_power_watts": 100, "cost_per_kwh": 0.15},
        "Vyper": {"cost": 349, "upgrades": 50, "maintenance": 50, "lifetime_hours": 4000, "avg_power_watts": 90, "cost_per_kwh": 0.15},
        "Chiron": {"cost": 499, "upgrades": 75, "maintenance": 75, "lifetime_hours": 4000, "avg_power_watts": 130, "cost_per_kwh": 0.15}
    },
    "Elegoo": {
        "Neptune 4": {"cost": 249, "upgrades": 50, "maintenance": 50, "lifetime_hours": 4000, "avg_power_watts": 100, "cost_per_kwh": 0.15},
        "Neptune 4 Pro": {"cost": 299, "upgrades": 50, "maintenance": 50, "lifetime_hours": 4000, "avg_power_watts": 100, "cost_per_kwh": 0.15},
        "Neptune 4 Max": {"cost": 349, "upgrades": 50, "maintenance": 50, "lifetime_hours": 4000, "avg_power_watts": 100, "cost_per_kwh": 0.15},
        "Neptune 3 Plus": {"cost": 199, "upgrades": 50, "maintenance": 50, "lifetime_hours": 4000, "avg_power_watts": 100, "cost_per_kwh": 0.15}
    },
    "Artillery": {
        "Sidewinder X2": {"cost": 399, "upgrades": 75, "maintenance": 75, "lifetime_hours": 4000, "avg_power_watts": 130, "cost_per_kwh": 0.15},
        "Sidewinder X3": {"cost": 499, "upgrades": 100, "maintenance": 100, "lifetime_hours": 4000, "avg_power_watts": 130, "cost_per_kwh": 0.15},
        "Genius Pro": {"cost": 349, "upgrades": 75, "maintenance": 75, "lifetime_hours": 4000, "avg_power_watts": 110, "cost_per_kwh": 0.15}
    },
    "Raise3D": {
        "E2": {"cost": 1999, "upgrades": 200, "maintenance": 150, "lifetime_hours": 5000, "avg_power_watts": 200, "cost_per_kwh": 0.15},
        "Pro2": {"cost": 2499, "upgrades": 250, "maintenance": 200, "lifetime_hours": 5000, "avg_power_watts": 200, "cost_per_kwh": 0.15},
        "Pro3": {"cost": 2999, "upgrades": 300, "maintenance": 250, "lifetime_hours": 5000, "avg_power_watts": 200, "cost_per_kwh": 0.15}
    },
    "Flashforge": {
        "Adventurer 5M": {"cost": 499, "upgrades": 75, "maintenance": 75, "lifetime_hours": 4000, "avg_power_watts": 130, "cost_per_kwh": 0.15},
        "Creator Pro 2": {"cost": 599, "upgrades": 100, "maintenance": 100, "lifetime_hours": 4000, "avg_power_watts": 130, "cost_per_kwh": 0.15},
        "Guider IIs": {"cost": 699, "upgrades": 150, "maintenance": 150, "lifetime_hours": 4000, "avg_power_watts": 200, "cost_per_kwh": 0.15}
    },
    "Snapmaker": {
        "Snapmaker 2.0 A150": {"cost": 699, "upgrades": 100, "maintenance": 100, "lifetime_hours": 5000, "avg_power_watts": 150, "cost_per_kwh": 0.15},
        "Snapmaker 2.0 A250": {"cost": 799, "upgrades": 100, "maintenance": 100, "lifetime_hours": 5000, "avg_power_watts": 150, "cost_per_kwh": 0.15},
        "Snapmaker 2.0 A350": {"cost": 899, "upgrades": 100, "maintenance": 100, "lifetime_hours": 5000, "avg_power_watts": 150, "cost_per_kwh": 0.15},
        "Snapmaker Artisan": {"cost": 1299, "upgrades": 150, "maintenance": 150, "lifetime_hours": 5000, "avg_power_watts": 200, "cost_per_kwh": 0.15}
    },
    "Qidi Tech": {
        "X-Smart 3": {"cost": 249, "upgrades": 50, "maintenance": 50, "lifetime_hours": 4000, "avg_power_watts": 110, "cost_per_kwh": 0.15},
        "X-Plus 3": {"cost": 599, "upgrades": 100, "maintenance": 75, "lifetime_hours": 4000, "avg_power_watts": 200, "cost_per_kwh": 0.15},
        "X-Max 3": {"cost": 699, "upgrades": 150, "maintenance": 100, "lifetime_hours": 4000, "avg_power_watts": 200, "cost_per_kwh": 0.15}
    },
    "Ultimaker": {
        "Ultimaker S3": {"cost": 2495, "upgrades": 300, "maintenance": 200, "lifetime_hours": 5000, "avg_power_watts": 250, "cost_per_kwh": 0.15},
        "Ultimaker S5": {"cost": 3995, "upgrades": 500, "maintenance": 300, "lifetime_hours": 5000, "avg_power_watts": 250, "cost_per_kwh": 0.15}
    },
    "Voxelab": {
        "Aquila": {"cost": 199, "upgrades": 50, "maintenance": 50, "lifetime_hours": 4000, "avg_power_watts": 110, "cost_per_kwh": 0.15},
        "Aquila X2": {"cost": 249, "upgrades": 50, "maintenance": 50, "lifetime_hours": 4000, "avg_power_watts": 110, "cost_per_kwh": 0.15},
        "Aquila D1": {"cost": 299, "upgrades": 50, "maintenance": 50, "lifetime_hours": 4000, "avg_power_watts": 110, "cost_per_kwh": 0.15}
    },
    "MakerBot": {
        "Sketch": {"cost": 349, "upgrades": 50, "maintenance": 50, "lifetime_hours": 4000, "avg_power_watts": 100, "cost_per_kwh": 0.15},
        "Method X": {"cost": 599, "upgrades": 100, "maintenance": 75, "lifetime_hours": 5000, "avg_power_watts": 250, "cost_per_kwh": 0.15}
    },
    "LulzBot": {
        "Mini 2": {"cost": 1499, "upgrades": 200, "maintenance": 150, "lifetime_hours": 5000, "avg_power_watts": 130, "cost_per_kwh": 0.15},
        "Taz Workhorse": {"cost": 1999, "upgrades": 250, "maintenance": 200, "lifetime_hours": 5000, "avg_power_watts": 200, "cost_per_kwh": 0.15},
        "Taz Pro": {"cost": 2499, "upgrades": 300, "maintenance": 250, "lifetime_hours": 5000, "avg_power_watts": 200, "cost_per_kwh": 0.15}
    }
}

# Add after your imports and before the main code
def calc_depreciation_cost(printer_details, print_time_hr):
    """Calculate depreciation cost for a print job."""
    if not printer_details:
        return 0.0
    
    total_cost = (
        printer_details["cost"] + 
        printer_details["upgrades"] + 
        printer_details["maintenance"]
    )
    
    print_time_min = print_time_hr * 60
    depreciation_per_minute = total_cost / (printer_details["lifetime_hours"] * 60)
    
    return depreciation_per_minute * print_time_min

with st.sidebar:
    # --- General Settings ---
    st.markdown("## General Settings")
    
    # Currency and Markup in same row
    col1, col2 = st.columns(2)
    with col1:
        currency_label = st.selectbox(
            'Currency',
            options=list(currency_options.keys()),
            help='Select the currency for all costs.'
        )
        currency = currency_options[currency_label]
        symbol = currency['symbol']
        rate = currency['rate']
    
    with col2:
        markup_percent = st.slider(
            "Markup", 
            min_value=0, 
            max_value=100, 
            value=20,
            help="Percentage markup on final cost"
        )

    # Electricity rate with improved styling
    st.markdown("### Electricity Rate")
    electricity_rate_label = st.selectbox(
        "Rate Type",
        options=list(uk_rates.keys()),
        help="Select a typical UK electricity rate or choose Custom"
    )
    
    if uk_rates[electricity_rate_label] is None:
        electricity_rate = st.number_input(
            f"Custom Rate ({symbol}/kWh)", 
            min_value=0.01, 
            value=0.30, 
            step=0.01,
            help="Enter your custom electricity rate"
        ) * rate
    else:
        electricity_rate = uk_rates[electricity_rate_label] * rate

    # --- Printer Selection ---
    st.markdown("## Printer Details")
    make = st.selectbox(
        "Manufacturer",
        options=list(printer_display_dict.keys()),
        help="Select the printer manufacturer"
    )
    
    model_display = st.selectbox(
        "Model",
        options=printer_display_dict[make],
        help="Select the specific printer model"
    )

    # Extract model name (remove power info)
    model = model_display.split(" (")[0] if " (" in model_display else model_display

    # --- Material Selection ---
    st.markdown("## Material")
    material = st.selectbox(
        "Type",
        options=list(MATERIALS.keys()),
        help="Choose filament material type"
    )
    
    diameter = st.selectbox(
        "Diameter (mm)",
        options=MATERIALS[material]['diameters'],
        help="Select filament diameter"
    )

    # Material cost settings
    density = MATERIALS[material]['density']
    base_cost = MATERIALS[material]['cost_per_kg'] * rate
    
    custom_material_cost = st.checkbox(
        "Use custom material cost",
        help="Override default material cost"
    )
    
    if custom_material_cost:
        cost_per_kg = st.number_input(
            f"Material Cost ({symbol}/kg)",
            min_value=0.0,
            value=base_cost,
            step=1.0,
            help="Enter your custom material cost per kg"
        )
    else:
        cost_per_kg = base_cost

    # --- Advanced Settings ---
    with st.expander("Advanced Settings"):
        default_details = printer_details_dict.get(make, {}).get(model, {})
        
        st.markdown("### Printer Configuration")
        custom_printer_cost = st.number_input(
            f"Printer Cost ({symbol})",
            min_value=0.0,
            value=float(default_details.get("cost", 0)) * rate,
            step=10.0
        )
        
        col3, col4 = st.columns(2)
        with col3:
            custom_upgrades = st.number_input(
                f"Upgrades ({symbol})",
                min_value=0.0,
                value=float(default_details.get("upgrades", 0)) * rate,
                step=10.0
            )
        with col4:
            custom_maintenance = st.number_input(
                f"Maintenance ({symbol})",
                min_value=0.0,
                value=float(default_details.get("maintenance", 0)) * rate,
                step=10.0
            )
        
        st.markdown("### Performance")
        col5, col6 = st.columns(2)
        with col5:
            custom_lifetime = st.number_input(
                "Lifetime (hours)",
                min_value=1000,
                value=int(default_details.get("lifetime_hours", 5000)),
                step=1000
            )
        with col6:
            power_watt = st.number_input(
                "Power (W)",
                min_value=1,
                value=int(default_details.get("avg_power_watts", 120)),
                step=5
            )

# Set power based on selection or advanced settings
if show_advanced := st.session_state.get('advanced_settings', False):
    power = power_watt
else:
    power = printer_power_dict.get(make, {}).get(model, 120)

# --- Main: STL Upload and Processing ---
st.subheader("Upload 3D Model Files")
uploaded_files = st.file_uploader(
    "Upload your 3D model files", 
    type=["stl", "obj", "3mf"],
    accept_multiple_files=True,
    help="Supported formats: STL, OBJ, 3MF"
)

if uploaded_files:
    # Create tabs for each uploaded file
    tabs = st.tabs([f.name for f in uploaded_files])
    
    # Process each file in its own tab
    for tab, uploaded_file in zip(tabs, uploaded_files):
        with tab:
            try:
                # Parse file and get volume
                file_extension = uploaded_file.name.split('.')[-1].lower()
                volume_cm3, bbox, mesh = parse_3d_file(uploaded_file, file_extension)
                st.success(f"Volume: {volume_cm3:.2f} cm³")

                # Convert volume for later use
                volume_mm3 = volume_cm3 * 1000  # convert cm³ to mm³

                # Reset file pointer for preview
                uploaded_file.seek(0)

                # --- 3D Preview (Interactive) ---
                st.subheader("3D Preview")
                import plotly.graph_objects as go
                import numpy as np

                # Extract vertices and faces
                x, y, z = mesh.vertices.T
                i, j, k = mesh.faces.T

                # Fix orientation and scaling
                def fix_mesh_orientation(x, y, z):
                    # Calculate bounding box
                    x_min, x_max = np.min(x), np.max(x)
                    y_min, y_max = np.min(y), np.max(y)
                    z_min, z_max = np.min(z), np.max(z)
                    
                    # Calculate dimensions
                    dx = x_max - x_min
                    dy = y_max - y_min
                    dz = z_max - z_min
                    
                    # Scale to uniform size (e.g., max dimension = 10 units)
                    max_dim = max(dx, dy, dz)
                    scale = 10.0 / max_dim if max_dim > 0 else 1.0
                    
                    x_scaled = x * scale
                    y_scaled = y * scale
                    z_scaled = z * scale
                    
                    # Center the model
                    x_center = (np.max(x_scaled) + np.min(x_scaled)) / 2
                    y_center = (np.max(y_scaled) + np.min(y_scaled)) / 2
                    z_center = (np.max(z_scaled) + np.min(z_scaled)) / 2
                    
                    return (x_scaled - x_center, 
                           y_scaled - y_center, 
                           z_scaled - z_center)

                # Apply fixes
                x, y, z = fix_mesh_orientation(x, y, z)

                # Create the 3D mesh figure
                fig = go.Figure(data=[
                    go.Mesh3d(
                        x=x, y=y, z=z,
                        i=i, j=j, k=k,
                        color='#00E5FF',  # Cyan color
                        opacity=1.0,      # Full opacity
                        lighting=dict(
                            ambient=0.6,
                            diffuse=0.8,
                            specular=0.2,
                            roughness=0.5
                        ),
                        lightposition=dict(
                            x=100,
                            y=200,
                            z=150
                        )
                    )
                ])

                # Update layout with better camera positioning
                fig.update_layout(
                    scene=dict(
                        aspectmode='data',
                        camera=dict(
                            up=dict(x=0, y=1, z=0),  # Set up vector
                            center=dict(x=0, y=0, z=0),  # Look at center
                            eye=dict(x=1.5, y=1.5, z=1.5)  # Camera position
                        ),
                        xaxis=dict(range=[-5, 5]),
                        yaxis=dict(range=[-5, 5]),
                        zaxis=dict(range=[-5, 5])
                    ),
                    margin=dict(l=0, r=0, b=0, t=0)
                )

                st.plotly_chart(fig, use_container_width=True)

                # --- Cost Calculations ---
                # Calculate material cost
                material_cost = calc_material_cost(volume_cm3, density, cost_per_kg)
                
                # Calculate print time (basic estimation)
                print_time_hr = volume_cm3 / 11.0  # Simple approximation
                
                # Calculate energy cost
                energy_cost = calc_energy_cost(print_time_hr, power, electricity_rate)
                
                # Calculate depreciation using printer details
                depreciation_cost = calc_depreciation_cost(printer_details_dict[make][model], print_time_hr)
                
                # Calculate total cost with markup
                subtotal = material_cost + energy_cost
                markup = subtotal * (markup_percent / 100)
                total_cost = subtotal + markup

                # --- Total Cost Summary Box ---
                total_with_depreciation = total_cost + depreciation_cost
                
                cost_col1, cost_col2 = st.columns([2, 1])
                with cost_col1:
                    st.markdown("""
                        <div style='
                            background-color: #1e2227;
                            padding: 20px;
                            border-radius: 10px;
                            border-left: 5px solid #4CAF50;
                            margin: 10px 0;'>
                            <h3 style='color: #4CAF50; margin: 0;'>Total Cost</h3>
                            <p style='font-size: 28px; margin: 10px 0;'>{}{:.2f}</p>
                            <p style='color: #666; margin: 0;'>Including depreciation and {}% markup</p>
                        </div>
                    """.format(symbol, total_with_depreciation, markup_percent), unsafe_allow_html=True)
                with cost_col2:
                    st.markdown("""
                        <div style='
                            background-color: #1e2227;
                            padding: 20px;
                            border-radius: 10px;
                            border-left: 5px solid #2196F3;
                            margin: 10px 0;'>
                            <h3 style='color: #2196F3; margin: 0;'>Print Time</h3>
                            <p style='font-size: 28px; margin: 10px 0;'>{:.1f}h</p>
                            <p style='color: #666; margin: 0;'>Estimated duration</p>
                        </div>
                    """.format(print_time_hr), unsafe_allow_html=True)

                # --- Detailed Breakdown in Expander ---
                with st.expander('Cost Breakdown'):
                    # Update the Advanced Settings section
                    if show_advanced:
                        st.sidebar.markdown("### Custom Printer Details")
                        
                        # Get default values from printer_details_dict
                        default_details = printer_details_dict.get(make, {}).get(model, {})
                        
                        # Custom printer details inputs
                        custom_printer_cost = st.sidebar.number_input(
                            f"Printer Cost ({symbol})", 
                            min_value=0.0, 
                            value=float(default_details.get("cost", 0)) * rate,
                            step=10.0
                        )
                        
                        custom_upgrades = st.sidebar.number_input(
                            f"Planned Upgrades ({symbol})", 
                            min_value=0.0, 
                            value=float(default_details.get("upgrades", 0)) * rate,
                            step=10.0
                        )
                        
                        custom_maintenance = st.sidebar.number_input(
                            f"Expected Maintenance ({symbol})", 
                            min_value=0.0, 
                            value=float(default_details.get("maintenance", 0)) * rate,
                            step=10.0
                        )
                        
                        custom_lifetime = st.sidebar.number_input(
                            "Expected Lifetime (hours)", 
                            min_value=1000, 
                            value=int(default_details.get("lifetime_hours", 5000)),
                            step=1000
                        )
                        
                        power_watt = st.sidebar.number_input(
                            "Printer Power (W)", 
                            min_value=1, 
                            value=int(default_details.get("avg_power_watts", 120)),
                            step=5
                        )
                        
                        # Use custom values in calculations
                        printer_details = {
                            "cost": custom_printer_cost,
                            "upgrades": custom_upgrades,
                            "maintenance": custom_maintenance,
                            "lifetime_hours": custom_lifetime,
                            "avg_power_watts": power_watt,
                            "cost_per_kwh": electricity_rate
                        }
                    else:
                        # Use default values from printer_details_dict
                        printer_details = printer_details_dict.get(make, {}).get(model, {})
                        power_watt = printer_details.get("avg_power_watts", 120)

                    # Update the depreciation calculation to use the custom values
                    depreciation_cost = calc_depreciation_cost(printer_details, print_time_hr)
                    energy_cost = calc_energy_cost(print_time_hr, printer_details["avg_power_watts"], electricity_rate)
                    
                    # Create detailed breakdown
                    breakdown_data = {
                        "Cost Component": [
                            "Material Cost",
                            "Energy Cost",
                            "Printer Depreciation",
                            "Additional Costs (Markup)",
                            "Total Cost"
                        ],
                        "Amount": [
                            f"{symbol}{material_cost:.2f}",
                            f"{symbol}{energy_cost:.2f}",
                            f"{symbol}{depreciation_cost:.2f}",
                            f"{symbol}{(total_cost - material_cost - energy_cost - depreciation_cost):.2f}",
                            f"{symbol}{(total_cost + depreciation_cost):.2f}"
                        ],
                        "Details": [
                            f"{volume_cm3:.1f}cm³ of {material}",
                            f"{print_time_hr:.1f}h at {power_watt}W" + (" (Custom)" if show_advanced else ""),
                            f"{print_time_hr:.1f}h of printer use ({symbol}{printer_details['cost']:.0f} printer)" + (" (Custom values)" if show_advanced else ""),
                            f"{markup_percent}% markup",
                            f"Final price inc. depreciation"
                        ]
                    }
                    
                    df = pd.DataFrame(breakdown_data)
                    st.dataframe(
                        df.style
                        .hide(axis='index')
                        .set_properties(**{
                            'background-color': '#22272e',
                            'color': '#fff',
                            'border-color': '#22272e',
                            'font-size': '1.1em'
                        })
                        .set_table_styles([
                            {'selector': 'th', 'props': [
                                ('background-color', '#1a1d23'),
                                ('color', '#4CAF50'),
                                ('font-size', '1.1em'),
                                ('text-align', 'left')
                            ]}
                        ]),
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Add pie chart visualization
                    # plot_cost_pie(material_cost, energy_cost, total_cost)
            except Exception as e:
                st.error(f"Error processing file {uploaded_file.name}: {str(e)}")
                continue

else:
    st.info("Please upload one or more 3D model files to begin.")
    
    # Show empty cost breakdown with example format
    st.markdown("#### Cost Breakdown")
    empty_data = {
        "Cost Type": ["Material", "Energy", "Markup"],
        "Amount": [f"{symbol}0.00", f"{symbol}0.00", f"{symbol}0.00"]
    }
    df = pd.DataFrame(empty_data)
    
    st.dataframe(
        df.style
        .hide(axis='index')
        .set_properties(**{
            'background-color': '#22272e',
            'color': '#fff',
            'border-color': '#22272e',
            'font-size': '1.1em'
        })
        .set_table_styles([
            {'selector': 'th', 'props': [
                ('background-color', '#1a1d23'),
                ('color', '#4CAF50'),
                ('font-size', '1.1em')
            ]}
        ]),
        use_container_width=True,
        hide_index=True
    )