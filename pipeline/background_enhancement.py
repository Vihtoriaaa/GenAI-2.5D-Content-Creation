import io
from PIL import Image
import numpy as np
import cv2
from datetime import datetime


def image_to_hdri(image: np.ndarray, scale: float = 1) -> np.ndarray:
    """
    Converts a regular image to a high dynamic range image (HDRI) by creating a panorama-like effect.

    Args:
        image (numpy.ndarray): The input image to be converted to HDRI. It should be in the format (height,
          width, channels) with dtype np.uint8.
        scale (float, optional): Scaling factor applied to the input image, allows resizing the input image
          before converting it to HDRI. Default value = 1.

    Returns:
        numpy.ndarray - The HDRI representation of the input image with a panorama-like effect.
    """
    canvas_height, canvas_width = 4096, 8192

    image = cv2.resize(image.copy(), (int(scale * image.shape[1]), int(scale * image.shape[0])))
    image = image[0 : canvas_height, 0 : canvas_width]  # crop if scaled image dimensions > canvas dimensions
    image_height, image_width = image.shape[0], image.shape[1]

    canvas = np.zeros((canvas_height, canvas_width, 3), np.uint8)  # hdri

    cx, cy = canvas_height // 2, canvas_width // 2
    ox, oy = image_height // 2, image_width // 2

    # paste left half of image to right half of canvas
    left = image[:, : oy].copy()
    left = cv2.resize(left, (cy, canvas_height))
    canvas[:, cy :] = left

    # paste right half of image to left half of canvas
    right = image[:, oy :].copy()
    right = cv2.resize(right, (cy, canvas_height))
    canvas[:, : cy] = right

    return canvas


def generate_hdri_from_existing_image(image_path, output_path, scale=1):
    """
    Generates an HDRI from an existing image.

    Args:
        image_path (str): The path to the existing image file.
        output_path (str): The path to the output hdri image file.
        scale (float, optional): Scaling factor applied to the input image before generating the HDRI.
                                 Default is 1.

    Returns:
        The generated HDRI image.

    Raises:
        Exception: If image enhancement fails, the function will attempt to resize the image instead and
          raise an exception.
    """
    # Load the existing image
    existing_image = cv2.imread(image_path)

    # Check if the image is loaded successfully
    if existing_image is None:
        raise ValueError(f"Unable to load image from {image_path}")
    
    try:
        # Generate HDRI from the existing image
        hdri_image = image_to_hdri(existing_image, scale=scale)

        # Encode the enhanced image data in PNG format
        hdri_image = cv2.imencode(".png", hdri_image)[1]
        
        # Save the enhanced image to a file named as the provided output file name
        with open(output_path, "wb") as f:
            f.write(hdri_image)

        return hdri_image

    except Exception as e:
        # If image enhancement fails, resize the image to a blank 8192x4096 PNG image
        print(f"Image enhancement failed. Image will be resized instead. {e}")
        buffer = io.BytesIO()
        Image.new("RGB", (8192, 4096)).save(buffer, format="PNG")
        return buffer.getvalue()


if __name__ == '__main__':
    current_date = datetime.now().strftime("%m-%d_%H-%M")
    image_path = "../to_depth/0.png"
    output_path = f"../hdri_images/hdri_{current_date}.png"
    generate_hdri_from_existing_image(image_path=image_path, output_path=output_path)
