import trimesh
import numpy as np

def parse_3d_file(file_obj, file_type):
    """Parse 3D model file and return volume and bounding box"""
    try:
        # Special handling for 3MF files
        if file_type.lower() == '3mf':
            mesh_or_scene = trimesh.load(
                file_obj,
                file_type='3mf',
                force='mesh',
                process=True,
                maintain_order=True,
                skip_materials=True,
                resolver=None  # Disable external references
            )
        else:
            mesh_or_scene = trimesh.load(
                file_obj,
                file_type=file_type,
                force='mesh'
            )
        
        # Handle Scene vs Mesh
        if isinstance(mesh_or_scene, trimesh.Scene):
            # Extract all meshes from scene
            geometries = list(mesh_or_scene.geometry.values())
            if len(geometries) == 0:
                raise ValueError(f"No geometry found in {file_type} scene")
            # Combine all meshes
            mesh = trimesh.util.concatenate(geometries)
        elif isinstance(mesh_or_scene, trimesh.Trimesh):
            mesh = mesh_or_scene
        else:
            raise ValueError(f"Unsupported format or no mesh found")

        # Calculate volume and bounding box
        volume_cm3 = mesh.volume / 1000  # Convert mm³ to cm³
        bbox = {
            'x': abs(mesh.bounds[1][0] - mesh.bounds[0][0]),
            'y': abs(mesh.bounds[1][1] - mesh.bounds[0][1]),
            'z': abs(mesh.bounds[1][2] - mesh.bounds[0][2])
        }
        
        return volume_cm3, bbox, mesh

    except Exception as e:
        raise ValueError(f"Failed to parse {file_type} file: {str(e)}")