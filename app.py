import streamlit as st
import numpy as np
import pandas as pd
from utils.stl_parser import parse_stl
from utils.cost_calculator import (
    calc_material_cost, calc_energy_cost, calc_total_cost, get_materials
)
from utils.visualisation import plot_cost_pie
from utils.business_logic import (
    calc_depreciation, calc_labour, apply_fail_rate, calc_final_business_price
)

st.set_page_config(page_title="3D Printer Cost Estimator", layout="centered")
st.title("3D Printer Cost Estimator")

# --- Currency Selector ---
currency_options = {
    'GBP (£)': {'symbol': '£', 'rate': 1.0},
    'USD ($)': {'symbol': '$', 'rate': 1.27},
    'EUR (€)': {'symbol': '€', 'rate': 1.17}
}
currency_label = st.sidebar.selectbox(
    'Currency',
    options=list(currency_options.keys()),
    help='Select the currency for all costs.'
)
currency = currency_options[currency_label]
symbol = currency['symbol']
rate = currency['rate']

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
        "Neptune 4": 100, "Neptune 4 Pro": 100, "Neptune 4 Max": 100, "Neptune 3 Plus": 100
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
# Use display dict for selection
make = st.sidebar.selectbox("Select 3D Printer Make", list(printer_display_dict.keys()))
model_display = st.sidebar.selectbox("Select Model", printer_display_dict[make])
# Extract the model name (remove power info)
if "(" in model_display:
    model = model_display.split("(")[0].strip()
else:
    model = model_display
# Get default power for this make/model
power = None
if "/" in model:
    submodels = [s.strip() for s in model.split("/")]
    for sub in submodels:
        if sub in printer_power_dict.get(make, {}):
            power = printer_power_dict[make][sub]
            break
else:
    power = printer_power_dict.get(make, {}).get(model)

# --- Sidebar: Material selection ---
MATERIALS = get_materials()
material = st.sidebar.selectbox(
    "Material",
    options=list(MATERIALS.keys()),
    help="Choose filament type."
)
density = MATERIALS[material]['density']
cost_per_kg = MATERIALS[material]['cost_per_kg'] * rate

# Remove print_time_hr input
# print_time_hr = st.sidebar.number_input("Print Time (hours)", min_value=0.1, value=4.0, step=0.1)

# --- Advanced Settings Toggle for Printer Power ---
show_advanced = st.sidebar.checkbox("Advanced Settings")
if show_advanced:
    power_watt = st.sidebar.number_input("Printer Power (W)", min_value=1, value=power if power else 120)
else:
    power_watt = power if power else 120

# --- UK Electricity Rates Dropdown ---
uk_rates = {
    f"Standard Variable ({symbol}0.30/kWh)": 0.30,
    f"Economy 7 (Day) ({symbol}0.32/kWh)": 0.32,
    f"Economy 7 (Night) ({symbol}0.12/kWh)": 0.12,
    f"Octopus Agile (avg) ({symbol}0.20/kWh)": 0.20,
    "Custom": None
}
electricity_rate_label = st.sidebar.selectbox(
    f"UK Electricity Rate",
    options=list(uk_rates.keys()),
    help=f"Select a typical UK electricity rate or choose Custom."
)
if uk_rates[electricity_rate_label] is None:
    electricity_rate = st.sidebar.number_input(f"Custom Electricity Rate ({symbol}/kWh)", min_value=0.01, value=0.30, step=0.01) * rate
else:
    electricity_rate = uk_rates[electricity_rate_label] * rate

# --- Business Mode Toggle and Fields ---
st.sidebar.markdown("---")
business_mode = st.sidebar.checkbox("Business Mode (Commercial)")
if business_mode:
    st.sidebar.subheader("Business Parameters")
    printer_cost = st.sidebar.number_input(f"Printer Cost ({symbol})", min_value=0.0, value=400.0 * rate, step=10.0 * rate)
    printer_lifespan = st.sidebar.number_input("Printer Lifespan (hrs)", min_value=1.0, value=2000.0, step=10.0)
    setup_time = st.sidebar.number_input("Setup Time (hrs)", min_value=0.0, value=0.25, step=0.05)
    post_time = st.sidebar.number_input("Post-processing Time (hrs)", min_value=0.0, value=0.25, step=0.05)
    hourly_wage = st.sidebar.number_input(f"Hourly Wage ({symbol}/hr)", min_value=0.0, value=12.0 * rate, step=1.0 * rate)
    fail_rate = st.sidebar.slider("Expected Fail Rate (%)", 0, 50, 10)
    shipping_cost = st.sidebar.number_input(f"Shipping & Packaging ({symbol})", min_value=0.0, value=5.0 * rate, step=0.5 * rate)
    markup_percent = st.sidebar.slider("Markup (%)", 0, 100, 25)
else:
    markup_percent = st.sidebar.slider("Markup (%)", 0, 100, 20)

# --- Main: STL Upload ---
st.subheader("Upload STL File")
uploaded_file = st.file_uploader("Choose an STL file", type=["stl"])

if uploaded_file:
    # Parse STL
    try:
        volume_cm3, bbox = parse_stl(uploaded_file)
        st.success(f"Volume: {volume_cm3:.2f} cm³")
        st.write(f"Bounding Box: {bbox}")
        # --- STL Preview (Interactive) ---
        import trimesh
        import plotly.graph_objects as go
        import streamlit as st

        st.subheader("STL Preview")

        try:
            # Load the STL file
            mesh_or_scene = trimesh.load(uploaded_file, file_type='stl')

            # Handle Scene vs Mesh
            if isinstance(mesh_or_scene, trimesh.Scene):
                # Combine geometries if available
                geometries = list(mesh_or_scene.geometry.values())
                if len(geometries) == 0:
                    raise ValueError("No geometry found in STL scene.")
                mesh = trimesh.util.concatenate(geometries)
            elif isinstance(mesh_or_scene, trimesh.Trimesh):
                if mesh_or_scene.is_empty:
                    raise ValueError("STL mesh is empty.")
                mesh = mesh_or_scene
            else:
                raise ValueError("Unsupported STL format or no mesh found.")

            # Extract vertices and faces
            x, y, z = mesh.vertices.T
            i, j, k = mesh.faces.T

            # Plot using Plotly
            fig = go.Figure(data=[
                go.Mesh3d(
                    x=x, y=y, z=z,
                    i=i, j=j, k=k,
                    color='lightblue', opacity=0.5
                )
            ])
            fig.update_layout(
                scene=dict(aspectmode='data'),
                margin=dict(l=0, r=0, b=0, t=0)
            )
            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.warning(f"Could not render STL preview: {e}")
    except Exception as e:
        st.error(f"Failed to parse STL: {e}")
        st.stop()

    # --- Estimate Print Time ---
    from utils.cost_calculator import estimate_print_time
    # Use defaults: nozzle_diameter=0.4mm, layer_height=0.2mm, print_speed=50mm/s, efficiency_factor=1.1
    nozzle_diameter = 0.4
    layer_height = 0.2
    print_speed = 50
    efficiency_factor = 1.1
    volume_mm3 = volume_cm3 * 1000  # convert cm³ to mm³
    print_time_result = estimate_print_time(volume_mm3, nozzle_diameter, layer_height, print_speed, efficiency_factor)
    if "error" in print_time_result:
        st.error("Could not estimate print time: invalid geometry or settings.")
        print_time_hr = 1.0
    else:
        print_time_hr = print_time_result["print_time_hours"]

    # --- Cost Calculation ---
    material_cost = calc_material_cost(volume_cm3, density, cost_per_kg)
    energy_cost = calc_energy_cost(print_time_hr, power_watt, electricity_rate)
    if business_mode:
        depreciation_cost = calc_depreciation(printer_cost, printer_lifespan, print_time_hr)
        labour_cost = calc_labour(setup_time, post_time, hourly_wage)
        base_cost = material_cost + energy_cost + depreciation_cost + labour_cost
        adjusted_cost = apply_fail_rate(base_cost, fail_rate)
        adjusted_cost += shipping_cost
        final_price = adjusted_cost * (1 + markup_percent / 100)
        total_cost = final_price
    else:
        total_cost = calc_total_cost(material_cost, energy_cost, markup_percent)

    # --- Modern Minimalist Summary ---
    if print_time_hr < 1:
        print_time_min = int(round(print_time_hr * 60))
        time_label = 'Estimated Print Time (min)'
        time_value = f"{print_time_min} min"
    else:
        time_label = 'Estimated Print Time (h)'
        time_value = f"{print_time_hr:.2f} h"
    st.markdown(f"""
        <div style='display: flex; gap: 2em; justify-content: center; margin: 2em 0;'>
            <div style='background: #22272e; border-radius: 1em; padding: 1.5em 2em; min-width: 220px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.07);'>
                <div style='color: #4CAF50; font-size: 1.1em; letter-spacing: 1px; margin-bottom: 0.5em;'>{time_label}</div>
                <div style='font-size: 2.5em; font-weight: 700; color: #fff;'>{time_value}</div>
            </div>
            <div style='background: #22272e; border-radius: 1em; padding: 1.5em 2em; min-width: 220px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.07);'>
                <div style='color: #2196F3; font-size: 1.1em; letter-spacing: 1px; margin-bottom: 0.5em;'>Total Cost</div>
                <div style='font-size: 2.5em; font-weight: 700; color: #fff;'>{symbol}{total_cost:.2f}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- Detailed Breakdown in Expander ---
    with st.expander('Show Detailed Cost Breakdown'):
        import pandas as pd
        if business_mode:
            st.markdown("#### Cost Breakdown (Business Mode)")
            breakdown_data = {
                "Cost Type": [
                    "Material", "Energy", "Depreciation", "Labour", "Base", "Fail Adj.", "Shipping", "Markup", "Total"
                ],
                "Amount": [
                    material_cost, energy_cost, depreciation_cost, labour_cost, base_cost,
                    adjusted_cost - shipping_cost, shipping_cost, final_price - adjusted_cost, final_price
                ]
            }
        else:
            st.markdown("#### Cost Breakdown")
            breakdown_data = {
                "Cost Type": ["Material", "Energy", "Markup"],
                "Amount": [material_cost, energy_cost, total_cost - material_cost - energy_cost]
            }
        df = pd.DataFrame(breakdown_data)
        df["Amount"] = df["Amount"].apply(lambda x: f"{symbol}{x:,.2f}")
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
                  {'selector': 'th', 'props': [('background-color', '#1a1d23'), ('color', '#4CAF50'), ('font-size', '1.1em')]}
              ]),
            use_container_width=True,
            hide_index=True
        )
        plot_cost_pie(material_cost, energy_cost, total_cost if not business_mode else final_price)

else:
    st.info("Please upload an STL file to begin.") 