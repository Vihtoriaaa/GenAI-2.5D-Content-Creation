import cv2
from depthToNormal import DepthToNormalMap
from tkinter import Tk, filedialog
import subprocess


class Pipeline():
    """A class representing a pipeline for 2.5D content creation with depth-guided object placement."""

    def __init__(self):
        """
        Args:
            original_image_path (str): The path to the selected original (colored) image file.
            depth_map_path (str): The path to the selected depth map file.
            object_3d_path (str): The path to the selected 3D object file.
            selected_point (tuple): The coordinates of the selected point on the original image.
            max_depth (int): The maximum depth value used in depth-to-normal conversion.
            depth_to_normal_converter (DepthToNormalMap): An instance of DepthToNormalMap class
                for converting depth maps to normal maps.
        """
        self.original_image_path = self.upload_image("Select Original Image File")
        self.depth_map_path = self.upload_image("Select Depth Image File")
        self.object_3d_path = self.upload_3d_object()
        self.selected_point = self.choose_point(self.original_image_path)
        self.max_depth = 255
        self.depth_to_normal_converter = DepthToNormalMap(self.depth_map_path, max_depth=self.max_depth)

    def upload_image(self, title):
        root = Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(title=title,
                                                filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        
        return file_path
    
    def upload_3d_object(self):
        """
        Prompts the user to select a 3D object file.

        Returns:
            str: The path to the selected 3D object file.
        """
        root = Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(title="Select 3D Object File",
                                                filetypes=[("Object files", "*.fbx *.stl")])
        return file_path

    def choose_point(self, image_path):
        """
        Allows the user to select a point on an image.

        Args:
            image_path (str): The path to the image file.

        Returns:
            tuple: The coordinates (x, y) of the selected point.
        """
        def on_mouse_click(event, x, y, flags, param):
            """Handles mouse click events."""
            if event == cv2.EVENT_LBUTTONDOWN:
                nonlocal point
                point = (x, y)
                cv2.destroyAllWindows()

        point = None
        image = cv2.imread(image_path)
        window_name = "Select Point"

        cv2.imshow(window_name, image)
        cv2.setMouseCallback(window_name, on_mouse_click)

        while point is None:
            cv2.waitKey(100)

        return point

    def get_normal_map(self):
        """Calculates normal vectors for the entire image."""
        self.depth_to_normal_converter.calculate_normals()
        x, y = self.selected_point
        self.normal_to_surface = self.depth_to_normal_converter.normals_map[y, x]
        # self.depth_to_normal_converter.save_normal_map("lol.png")

    def generate_scene(self):
        """Calls Blender for scene generation and object placement."""
        command = [
            "blender",
            "-P",
            "blender.py",
            "--",
            self.depth_map_path,
            self.original_image_path,
            self.object_3d_path,
            str(self.selected_point[0]),
            str(self.selected_point[1]),
            str(self.normal_to_surface[0]),
            str(self.normal_to_surface[1]),
            str(self.normal_to_surface[2])
        ]
        subprocess.run(command)

    def draw_normal_to_surface(self):
        """Draws normal vector to the surface at the selected point."""
        image = cv2.imread(self.original_image_path)
        x, y = self.selected_point
        arrow_length = 50
        end_point = (int(x + arrow_length * self.normal_to_surface[0]), int(y + arrow_length * self.normal_to_surface[1]))
        cv2.arrowedLine(image, (x, y), end_point, (0, 255, 0), thickness=2)

        while True:
            cv2.imshow("Normal to the Surface at the Selected Point", image)
            key = cv2.waitKey(1) & 0xFF
            # Press 'ESC' to exit
            if key == 27:
                break

        cv2.destroyAllWindows()


if __name__ == "__main__":
    pipeline = Pipeline()
    pipeline.get_normal_map()
    pipeline.draw_normal_to_surface()
    pipeline.generate_scene()
