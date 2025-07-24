import trimesh
import numpy as np

def parse_stl(file_obj):
    """
    Load an STL file and extract volume (cm³) and bounding box dimensions.
    Args:
        file_obj: File-like object (from Streamlit uploader)
    Returns:
        volume_cm3 (float): Volume in cubic centimeters
        bbox (tuple): Bounding box dimensions (x, y, z) in mm
    """
    mesh = trimesh.load(file_obj, file_type='stl')
    volume_cm3 = mesh.volume / 1000  # Trimesh gives mm³, convert to cm³
    bbox = mesh.bounding_box.extents  # (x, y, z) in mm
    return volume_cm3, tuple(np.round(bbox, 2)) 