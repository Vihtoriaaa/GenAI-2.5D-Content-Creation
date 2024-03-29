import bpy
import sys
import os


def load_image(image_path):
    try:
        return bpy.data.images.load(image_path)
    except Exception as e:
        print("Error loading image:", e)
        return None

def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)

def get_image_dimensions(image):
    return image.size[0], image.size[1]

def set_render_resolution(image_width, image_height):
    bpy.context.scene.render.resolution_x = image_width
    bpy.context.scene.render.resolution_y = image_height

def add_camera():
    bpy.ops.object.camera_add(enter_editmode=False, align='VIEW', location=(0, -3, 1), rotation=(1.5708, 0, 0))
    bpy.context.scene.camera = bpy.context.object
    # Set camera to orthographic projection
    bpy.context.object.data.type = 'ORTHO'
    # Adjust orthographic scale
    bpy.context.object.data.ortho_scale = 2

def add_light():
    light_data = bpy.data.lights.new(name="Light-data", type='POINT')
    light_data.energy = 100
    # Create new object, pass the light data 
    light_object = bpy.data.objects.new(name="Light", object_data=light_data)
    # Link object to collection in context
    bpy.context.collection.objects.link(light_object)
    # Change light position
    light_object.location = (0, -2, 2)

def import_3d_model(file_path, scale_factor=0.7):
    supported_formats = {
        ".fbx": bpy.ops.import_scene.fbx,
        ".stl": bpy.ops.import_mesh.stl,
    }
    
    _, file_extension = os.path.splitext(file_path)
    file_format = file_extension.lower()

    if file_format in supported_formats:
        try:
            supported_formats[file_format](filepath=file_path)
            bpy.ops.transform.resize(value=(scale_factor, scale_factor, scale_factor))
        except RuntimeError as e:
            print(f"Importing {file_format} failed: {e}")
    else:
        print(f"Unsupported file format: {file_format}")

def main():
    # Clear existing objects
    clear_scene()

    depth_image = load_image(depth_map_path)
    if not depth_image:
        sys.exit(1)

    image_width, image_height = get_image_dimensions(depth_image)
    aspect_ratio = image_width / image_height

    # Set the plane size based on the aspect ratio
    plane_size_x = 2 * aspect_ratio
    plane_size_y = 2

    # Add a plane with the calculated size
    bpy.ops.mesh.primitive_plane_add(size=1, enter_editmode=True)
    bpy.ops.transform.resize(value=(plane_size_x, plane_size_y, 1))
    # Subdivide the plane
    bpy.ops.mesh.subdivide(number_cuts=100)

    # Add a displace modifier and a new texture
    displace_modifier = bpy.context.object.modifiers.new(name="Displace", type='DISPLACE')
    displace_texture = bpy.data.textures.new("DisplaceTexture", type='IMAGE')
    displace_modifier.texture = displace_texture
    # displace_modifier.strength = 0.8

    displace_texture.image = depth_image

    # Switch to Edit mode and perform a Shade smooth of the object
    bpy.ops.object.editmode_toggle()
    bpy.ops.object.shade_smooth()

    # Get the active object, rotate and translate it
    obj = bpy.context.active_object
    obj.rotation_euler = (1.5708, 0, 0)
    obj.location = (0, 0, 1)


    new_material = bpy.data.materials.new(name="MyMaterial")
    new_material.use_nodes = True

    node_tree = bpy.data.materials['MyMaterial'].node_tree
    texture_node = node_tree.nodes.new('ShaderNodeTexImage')
    texture_node.location = (-300, 200)

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
    # add a point light source to the scene
    add_light()
    import_3d_model(model_3d_path)


if __name__ == "__main__":
    if len(sys.argv) == 7:
        depth_map_path = sys.argv[4]
        texture_image_path = sys.argv[5]
        model_3d_path = sys.argv[6]
    else:
        print("Usage: blender -P script.py -- /path/to/your/depth_map /path/to/texture_image /path/to/3d_object")
        sys.exit(1)

    # Check if the file exists for both depth map and texture image
    if not os.path.exists(depth_map_path) or not os.path.exists(texture_image_path) or not os.path.exists(model_3d_path):
        print("Image file not found. Check your file paths.")
        sys.exit(1)

    main()

# blender -P blender.py -- ../depth_maps/inverted_depth_map0.png ../to_depth/0.png ../3d_objects/worm.fbx