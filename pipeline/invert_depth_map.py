import os
import argparse
import numpy as np
from PIL import Image


def invert_depth_map(input_path, output_dir):
    """Invert depth map image and save it."""
    depth_image = Image.open(input_path)
    depth_array = np.array(depth_image)
    inverted_depth_array = np.abs(depth_array - 2**16 - 1)
    inverted_depth_array_uint16 = inverted_depth_array.astype(np.uint16)
    inverted_depth_image = Image.fromarray(inverted_depth_array_uint16)
    
    # Extract the filename without extension from depth_map_path
    image_name = os.path.basename(input_path)
    name, ext = os.path.splitext(image_name)
    
    output_path = os.path.join(output_dir, f"{name}_depth.png")
    inverted_depth_image.save(output_path)
    print("Image saved:", output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Invert depth map")
    parser.add_argument(
        "--input",
        type=str,
        help="Path to depth map image"
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="results",
        help="Output directory for inverted depth image. Default: results",
    )
    args = parser.parse_args()

    if args.input is None:
        print("Error: Please provide --input path to the depth map image.")

    else:
        os.makedirs(args.output_dir, exist_ok=True)
        invert_depth_map(args.input, args.output_dir)
