import cv2
import argparse
import numpy as np


class DepthToNormalMap:
    """A class for converting a depth map image to a normal map image."""

    def __init__(self, depth_map_path: str, max_depth: int = 255) -> None:
        """Constructs a DepthToNormalMap object.

        Args:
            depth_map_path (str): The path to the depth map image file.
            max_depth (int, optional): The maximum depth value in the depth map image.
                Defaults to 255.

        Raises:
            ValueError: If the depth map image file cannot be read.
        """
        self.depth_map = cv2.imread(depth_map_path, cv2.IMREAD_UNCHANGED)

        if self.depth_map is None:
            raise ValueError(
                f"Could not read the depth map image file at {depth_map_path}"
            )
        # Normalize the depth map to [0, 1]
        self.depth_map = self.depth_map / 65535
        self.max_depth = max_depth
        self.scaling_factor = 255
        self.clicked_points = []

    def circular_filter(self, image, radius):
        """Applies a circular filter of specified radius to the input image."""
        kernel = np.zeros((2*radius + 1, 2*radius + 1))
        y_circle, x_circle = np.ogrid[-radius:radius + 1, -radius:radius + 1]
        circular_mask = x_circle**2 + y_circle**2 <= radius**2
        kernel[circular_mask] = 1
        kernel /= np.sum(kernel)
        return cv2.filter2D(image, -1, kernel)

    def calculate_normals(self) -> None:
        """Calculates normal vectors for the entire image."""
        rows, cols = self.depth_map.shape

        x, y = np.meshgrid(np.arange(cols), np.arange(rows))
        x = x.astype(np.float32)
        y = y.astype(np.float32)
        
        scaled_image = (self.depth_map * self.scaling_factor)
        depth_float32 = scaled_image.astype(np.float32)
        depth_float32 = cv2.GaussianBlur(depth_float32, (7, 7), 1.4)
        # Median Filter 
        # depth_float32 = cv2.medianBlur(depth_float32, 5)
        # Bilateral Filter:
        # depth_float32 = cv2.bilateralFilter(depth_float32, 9, 75, 75)
        # Circular 
        # depth_float32 = self.circular_filter(depth_float32, radius=9)

        dx = cv2.Scharr(depth_float32, cv2.CV_32F, 1, 0)
        dy = cv2.Scharr(depth_float32, cv2.CV_32F, 0, 1)

        normal = np.dstack((-dx, -dy, np.ones((rows, cols))))
        norm = np.sqrt(np.sum(normal**2, axis=2, keepdims=True))
        normal = np.divide(normal, norm, out=np.zeros_like(normal), where=norm != 0)

        self.normals_map = normal

    def save_normal_map(self, output_path: str):
        """Converts the depth map image to a normal map image.

        Args:
            output_path (str): The path to save the normal map image file.
        """
        normal = (self.normals_map + 1) * 127.5
        normal = normal.clip(0, 255).astype(np.uint8)
        normal_bgr = cv2.cvtColor(normal, cv2.COLOR_RGB2BGR)
        cv2.imwrite(output_path, normal_bgr)

    def draw_normal_vectors(self, x, y, length=30, color=(0, 255, 255), thickness=2, image=None):
        """Draws longer red normal vectors on the image at specified points.

        Args:
            x (int): x-coordinate of the point.
            y (int): y-coordinate of the point.
            length (int, optional): Length of the normal vectors. Defaults to 50.
            color (tuple, optional): Color of the normal vectors in BGR format. Defaults to (0, 0, 255) (red).
            thickness (int, optional): Thickness of the lines. Defaults to 2.
        """
        normal_vector = self.get_normal_vector(x, y)
        x, y = int(x), int(y)
        scaled_normal = normal_vector * length
        endpoint = (
            int(x + scaled_normal[0]),
            int(y + scaled_normal[1]),
        )
        if image is None:
            image = self.depth_map

        cv2.arrowedLine(image, (x, y), endpoint, color, thickness)

    def get_normal_vector(self, x, y):
        """Gets the normal vector at a specific point.

        Args:
            x (int): x-coordinate of the point.
            y (int): y-coordinate of the point.

        Returns:
            numpy.ndarray: Normal vector at the specified point.
        """
        return self.normals_map[y, x]

    def draw_normals_from_file(self, coordinated_path, norm_drawing_path):
        """Draws normal vectors at specified points from a file.

        Args:
            coordinated_path (str): Path to the file containing coordinates.
            norm_drawing_path (str): Path to save the image with drawn normal vectors.
        """
        depth_map_with_normals = self.depth_map.copy()

        with open(coordinated_path, "r") as file:
            for line in file:
                x, y = map(int, line.strip().split(","))
                self.draw_normal_vectors(x, y, image=depth_map_with_normals)

        cv2.imwrite(norm_drawing_path, (depth_map_with_normals*255).astype(np.uint8))

    def on_mouse_click(self, event, x, y, flags, param):
        """Callback function to be called when a mouse click event occurs.

        Args:
            event (int): The mouse event type.
            x (int): The x-coordinate of the mouse click.
            y (int): The y-coordinate of the mouse click.
        """
        if event == cv2.EVENT_LBUTTONDOWN:
            self.clicked_points.append((x, y))
            self.draw_normal_vectors(x, y)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert depth map to normal map")
    parser.add_argument(
        "--input",
        type=str,
        help="Path to depth map image"
    )
    parser.add_argument(
        "--max_depth",
        type=int,
        default=255,
        help="Maximum depth value (default: 255)"
    )
    parser.add_argument(
        "--save_normal_map",
        type=str,
        choices=["y", "n"],
        default="n",
        help="Save normal vectors on the depth map to an image (y/n)",
    )
    parser.add_argument(
        "--norm_map_path",
        type=str,
        default=None,
        help="Output path for normal map image",
    )
    parser.add_argument(
        "--draw_points",
        type=str,
        choices=["y", "n"],
        default="n",
        help="Draw normal vectors for points from file (y/n)",
    )
    parser.add_argument(
        "--points_normals_path",
        type=str,
        default=None,
        help="Output path for image with normals for points",
    )
    parser.add_argument(
        "--draw_on_click",
        type=str,
        choices=["y", "n"],
        default="n",
        help="Draw normal vectors on click for the depth map (y/n)",
    )
    args = parser.parse_args()

    converter = DepthToNormalMap(args.input, max_depth=args.max_depth)
    converter.calculate_normals()

    if args.save_normal_map == "y":
        converter.save_normal_map(args.norm_map_path)

    if args.draw_points == "y":
        converter.draw_normals_from_file("clicked_points.txt", args.points_normals_path)

    if args.draw_on_click == "y":
        cv2.imshow("Depth Map", converter.depth_map)
        cv2.setMouseCallback("Depth Map", converter.on_mouse_click)

        while True:
            cv2.imshow("Depth Map", converter.depth_map)
            key = cv2.waitKey(1) & 0xFF
            # Press 'ESC' to exit
            if key == 27:
                break

        cv2.destroyAllWindows()
