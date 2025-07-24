import os
import json

# Load materials from JSON
MATERIALS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'material_db', 'materials.json')
def get_materials():
    with open(MATERIALS_PATH, 'r') as f:
        return json.load(f)

def calc_material_cost(volume_cm3, density_g_cm3, cost_per_kg):
    """
    Calculate material cost based on volume, density, and cost per kg.
    """
    grams = volume_cm3 * density_g_cm3
    kg = grams / 1000
    return round(kg * cost_per_kg, 4)

def calc_energy_cost(print_time_hr, power_watt, electricity_rate):
    """
    Calculate energy cost: time (hr) * power (W) * rate ($/kWh)
    """
    kwh = (power_watt * print_time_hr) / 1000
    return round(kwh * electricity_rate, 4)

def calc_total_cost(material_cost, energy_cost, markup_percent):
    """
    Calculate total cost with markup.
    """
    subtotal = material_cost + energy_cost
    markup = subtotal * (markup_percent / 100)
    return round(subtotal + markup, 4)

def estimate_print_time(volume_mm3, nozzle_diameter=0.4, layer_height=0.2, 
                       print_speed=50, infill_density=20, shell_thickness=1.2,
                       acceleration=500, jerk=8, retraction_speed=45):
    """
    Enhanced 3D print time estimation based on volume and print parameters
    """
    try:
        # Calculate extrusion width (typically 120% of nozzle diameter)
        extrusion_width = nozzle_diameter * 1.2
        
        # Calculate number of shells
        num_shells = round(shell_thickness / extrusion_width)
        
        # Calculate approximate model dimensions
        dimension = pow(volume_mm3, 1/3)
        
        # Calculate number of layers
        num_layers = dimension / layer_height
        
        # Estimate shell volume (outer walls)
        shell_volume = (dimension * dimension * 6) * (extrusion_width * num_shells)
        
        # Calculate infill volume
        interior_volume = volume_mm3 - shell_volume
        infill_volume = interior_volume * (infill_density / 100)
        
        # Calculate total extrusion length
        total_extrusion = (shell_volume + infill_volume) / (extrusion_width * layer_height)
        
        # Base print time from extrusion length and print speed
        base_time = total_extrusion / print_speed
        
        # Add time for acceleration and jerk
        acceleration_factor = 1 + (30 / acceleration) + (2 / jerk)
        
        # Add time for retractions (estimate 1 retraction per layer)
        retraction_time = (num_layers * 2) / retraction_speed
        
        # Total print time in hours
        print_time_hours = (base_time * acceleration_factor + retraction_time) / 3600
        
        # Add 10% for non-printing moves
        print_time_hours *= 1.1
        
        return {
            "print_time_hours": print_time_hours,
            "details": {
                "layers": num_layers,
                "shell_volume": shell_volume,
                "infill_volume": infill_volume,
                "total_extrusion": total_extrusion
            }
        }
        
    except Exception as e:
        return {"error": str(e)}