import os
import bpy
import sys
import numpy as np
from datetime import datetime


def load_image(image_path):
    """Loads an image file into Blender."""
    if os.name == "nt":  # windows os
        image_path = os.path.abspath(image_path)
    try:
        return bpy.data.images.load(image_path)
    except Exception as e:
        print("Error loading image:", e)
        return None

def clear_scene():
    """Clears the Blender scene by deleting all objects."""
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)

def get_image_dimensions(image):
    """Retrieves the dimensions (width and height) of an image."""
    return image.size[0], image.size[1]

def set_render_resolution(image_width, image_height):
    """
    Sets the render resolution of the Blender scene.

    Args:
      image_width (int): The width of the render resolution.
      image_height (int): The height of the render resolution.
    """
    bpy.context.scene.render.resolution_x = image_width
    bpy.context.scene.render.resolution_y = image_height

def add_camera():
    """Adds a camera with orthographic projection to the Blender scene."""
    bpy.ops.object.camera_add(enter_editmode=False, align='VIEW', location=(1, -3, 1), rotation=(1.5708, 0, 0))
    bpy.context.scene.camera = bpy.context.object
    bpy.context.object.data.type = 'ORTHO'
    bpy.context.object.data.ortho_scale = 2

def add_light(hdri_path):
    """
    Adds an HDRI image as light source.

    Args:
        hdri_path (str): The file path to the HDRI image.
    """
    world = bpy.context.scene.world
    world.use_nodes = True
    node_tree = world.node_tree
    enode = node_tree.nodes.new("ShaderNodeTexEnvironment")
    hdri_image = load_image(hdri_path)
    hdri_image.source = 'GENERATED'
    hdri_image.colorspace_settings.name = 'Non-Color'
    enode.image = hdri_image
    node_tree.links.new(enode.outputs['Color'], node_tree.nodes['Background'].inputs['Color'])
    node_tree.nodes['Background'].inputs['Strength'].default_value = 1

def adjust_rendering_settings(enable_gpu=False):
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.use_gtao = True
    scene.cycles.gtao_distance = 0.3
    scene.cycles.gtao_quality = 0.3
    scene.cycles.use_bloom = True
    scene.cycles.shadow_cube_size = '1024'
    scene.cycles.use_denoising = True
    scene.cycles.samples = 200
    scene.cycles.device = 'GPU' if enable_gpu else 'CPU'
    scene.view_settings.view_transform = 'Filmic'
    scene.view_settings.look = 'High Contrast'
    scene.view_settings.exposure = 0.5
    scene.render.film_transparent = True

def import_3d_model(object_path, scale_factor=0.5):
    """
    Imports a 3D model file into the Blender scene.

    This function supports importing 3D models in FBX (.fbx) and STL (.stl) formats.

    Args:
      object_path (str): The path to the 3D model file.
      scale_factor (float, optional): The scaling factor applied to the imported model. Default is 0.5.
    """
    supported_formats = {
        ".fbx": bpy.ops.import_scene.fbx,
        ".stl": bpy.ops.import_mesh.stl,
    }
    
    _, file_extension = os.path.splitext(object_path)
    file_format = file_extension.lower()

    if file_format in supported_formats:
        try:
            supported_formats[file_format](filepath=object_path)
            bpy.ops.transform.resize(value=(scale_factor, scale_factor, scale_factor))
        except Exception as e:
            print(f"Importing {file_format} failed: {e}")
    else:
        print(f"Unsupported file format: {file_format}")

def set_output_path():
    """Sets the output path for the rendered image with a current date (ex: 2024-03-31-9-46-22)."""
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    output_filename = f"{timestamp}.png"
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../rendered_results/", output_filename)
    return output_path

def render_and_save(output_path):
    """
    Renders the scene and saves the image to the specified output path.

    Args:
      output_path (str): The path where the rendered image will be saved.
    """
    bpy.context.scene.render.filepath = output_path
    bpy.ops.render.render(write_still=True)

def move_object(obj_name, x, z, image_width, image_height, ratio):
    """Moves imported 3D object to previously selected place."""
    obj_list = bpy.context.scene.objects
    model_3D = obj_list[obj_name]

    obj_x = (x / image_width) * 2 * ratio
    obj_z = 2 - (z / image_height) * 2
    model_3D.location = (obj_x, -0.1, obj_z)

def rotate_object(obj_name, normal_vector):
    """Rotates the object considering surface normal vector."""
    obj_list = bpy.context.scene.objects
    model_3D = obj_list[obj_name]
    
    x_norm, y_norm, z_norm = normal_vector
    rotation_angle_rad = np.arccos(y_norm * (-1) / np.sqrt(x_norm**2 + y_norm**2))
    rotation_angle_rad = -rotation_angle_rad if x_norm < 0 else rotation_angle_rad

    current_rotation_x = model_3D.rotation_euler[0]
    current_rotation_z = model_3D.rotation_euler[2]

    model_3D.rotation_euler = (current_rotation_x, rotation_angle_rad, current_rotation_z)

def main():
    """The main function orchestrating the creation of a Blender scene."""
    # Clear existing objects
    clear_scene()

    # Load the depth image
    depth_image = load_image(depth_map_path)
    if not depth_image:
        sys.exit(1)

    # Calculate image dimensions and aspect ratio
    image_width, image_height = get_image_dimensions(depth_image)
    aspect_ratio = image_width / image_height

    # Set the plane size based on the aspect ratio
    plane_size_x = 2 * aspect_ratio
    plane_size_y = 2

    # Add a plane with the calculated size
    bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=True)
    bpy.ops.transform.resize(value=(plane_size_x, plane_size_y, 1))
    # Subdivide the plane for smoother deformation
    bpy.ops.mesh.subdivide(number_cuts=100)

    # Add a displace modifier and a new texture
    displace_modifier = bpy.context.object.modifiers.new(name="Displace", type='DISPLACE')
    displace_texture = bpy.data.textures.new("DisplaceTexture", type='IMAGE')
    displace_modifier.texture = displace_texture
    displace_texture.image = depth_image
    # Set the strength of the Displace modifier
    displace_modifier.strength = 0.8

    # Switch to Edit mode and perform a Shade smooth of the object
    bpy.ops.object.editmode_toggle()
    bpy.ops.object.shade_smooth()

    # Get the active object, rotate and translate it
    obj = bpy.context.active_object
    obj.rotation_euler = (1.5708, 0, 0)
    obj.location = (1, 0, 1)

    # Create a new material with a texture image node
    new_material = bpy.data.materials.new(name="MyMaterial")
    new_material.use_nodes = True
    node_tree = bpy.data.materials['MyMaterial'].node_tree
    texture_node = node_tree.nodes.new('ShaderNodeTexImage')
    texture_node.location = (-300, 200)

    # Load the texture image and assign it to the texture node
    texture_image = load_image(texture_image_path)
    if texture_image:
        texture_node.image = texture_image

    # Find existing Principled BSDF node and connect Texture node to Principled BSDF node's Base Color input
    principled_bsdf_node = node_tree.nodes.get("Principled BSDF")
    node_tree.links.new(texture_node.outputs["Color"], principled_bsdf_node.inputs["Base Color"])

    # apply newly created material to be used by default
    obj.data.materials.append(new_material)

    # Show texture of an object
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.shading.color_type = 'TEXTURE'
            break
    
    # add camera and change its resolution to image's size
    add_camera()
    set_render_resolution(image_width, image_height)

    old_objs = set(bpy.context.scene.objects)
    # import selected 3D model
    import_3d_model(model_3d_path)
    imported_objs = set(bpy.context.scene.objects) - old_objs
    imported_obj_name = [obj.name for obj in imported_objs]

    # move 3D object to the specified place
    x, z = object_coordinates
    move_object(imported_obj_name[0], x, z, image_width, image_height, aspect_ratio)
    rotate_object(imported_obj_name[0], normal_vector)

    # add hdri as a light source to the scene
    add_light(hdri_image_path)

    # Deselect all the objects
    bpy.ops.object.select_all(action='DESELECT')

    # Adjust rendering settings, render the image and save it
    adjust_rendering_settings(enable_gpu=enable_gpu)
    output_path = set_output_path()
    render_and_save(output_path)


if __name__ == "__main__":
    if len(sys.argv) == 14:
        depth_map_path = sys.argv[4]
        texture_image_path = sys.argv[5]
        hdri_image_path = sys.argv[6]
        model_3d_path = sys.argv[7]
        object_coordinates = int(sys.argv[8]), int(sys.argv[9])
        normal_vector = float(sys.argv[10]), float(sys.argv[11]), float(sys.argv[12])
        enable_gpu_arg = sys.argv[13]
        enable_gpu = enable_gpu_arg.lower() == 'true'
    else:
        print("Usage: blender -P blender_code.py -- /path/to/your/depth_map /path/to/texture_image /path/to/hdri_image /path/to/3d_object x_coord z_coord x_norm y_norm z_norm enable_gpu")
        sys.exit(1)

    # Check if the file exists for depth map, texture image, hdri image, and 3D object
    if not os.path.exists(depth_map_path) or not os.path.exists(texture_image_path) or not os.path.exists(hdri_image_path) or not os.path.exists(model_3d_path):
        print("Image or object file not found. Check your file paths.")
        sys.exit(1)

    main()
