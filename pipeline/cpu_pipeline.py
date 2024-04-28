import os
import cv2
import subprocess
from datetime import datetime
from tkinter import filedialog as fd
from depthToNormal import DepthToNormalMap


class Pipeline():
    """A class representing a CPU version of the pipeline for 2.5D content creation with
        depth-guided object placement."""

    def __init__(self):
        """
        Attributes:
            scene_image_path (str): The path to the selected scene (colored) image file.
            depth_map_path (str): The path to the selected depth map file.
            object_3d_path (str): The path to the selected 3D object file.
            selected_point (tuple): The coordinates of the selected point on the original image.
            max_depth (int): The maximum depth value used in depth-to-normal conversion.
            depth_to_normal_converter (DepthToNormalMap): An instance of DepthToNormalMap class
                for converting depth maps to normal maps.
        """
        self.scene_image_path = self.upload_image("Select Scene Image File")
        self.depth_map_path = self.upload_image("Select Depth Image File")
        self.object_3d_path = self.upload_3d_object()
        self.selected_point = self.choose_point(self.scene_image_path)
        self.output_folder_path = "results"
        self.max_depth = 255
        self.enable_gpu = False
        self.depth_to_normal_converter = DepthToNormalMap(self.depth_map_path, max_depth=self.max_depth)

    def upload_image(self, title):
        """
        Prompts the user to select an image (allowed types: jpg, jpeg, png).

        Returns:
            str: The path to the selected image file.
        """
        file_path = fd.askopenfilename(title=title,
                                        filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        return file_path
    
    def upload_3d_object(self):
        """
        Prompts the user to select a 3D object file.

        Returns:
            str: The path to the selected 3D object file.
        """
        file_path = fd.askopenfilename(title="Select 3D Object File",
                                       filetypes=[("Object files", "*.fbx")])
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

    def get_surface_normal_vector(self, point):
        """Get surface normal vector values from image normal map."""
        x, y = point
        self.normal_to_surface = self.depth_to_normal_converter.normals_map[y, x]
        self.depth_value = self.depth_to_normal_converter.depth_map[y, x]

    def generate_scene(self):
        """Calls Blender for scene generation and object placement."""
        try:
            command = [
                "blender",
                "-P",
                "blender.py",
                "--",
                self.depth_map_path,
                self.scene_image_path,
                self.hdri_image_path,
                self.object_3d_path,
                str(self.selected_point[0]),
                str(self.selected_point[1]),
                str(self.normal_to_surface[0]),
                str(self.normal_to_surface[1]),
                str(self.normal_to_surface[2]),
                str(self.depth_value),
                str(self.enable_gpu)
            ]
            subprocess.run(command)

        except Exception as exc:
            print(f"Error while generating scene in Blender: {exc}")

    def draw_normal_to_surface(self):
        """Draws normal vector to the surface at the selected point."""
        image = cv2.imread(self.scene_image_path)
        x, y = self.selected_point
        arrow_length = 50
        end_point = (int(x + arrow_length * self.normal_to_surface[0]), int(y + arrow_length * self.normal_to_surface[1]))
        cv2.arrowedLine(image, (x, y), end_point, (0, 255, 0), thickness=2)

        while True:
            cv2.imshow("Normal to the Surface at the Selected Point", image)
            key = cv2.waitKey(1) & 0xFF

            if key == ord('r') or key == ord('R'):
                # Allow user to reselect the point by pressing 'R'
                cv2.destroyAllWindows()
                self.selected_point = self.choose_point(self.scene_image_path)
                self.get_surface_normal_vector(self.selected_point)
                x, y = self.selected_point
                image = cv2.imread(self.scene_image_path)
                end_point = (int(x + arrow_length * self.normal_to_surface[0]), int(y + arrow_length * self.normal_to_surface[1]))
                cv2.arrowedLine(image, (x, y), end_point, (0, 255, 0), thickness=2)

            # Press 'ESC' or 'Enter' to exit
            elif key == 27 or key == 13:
                cv2.destroyAllWindows()
                break

    def generate_hdri_image(self):
        """Run HDRI image generation process from the scene image."""
        try:
            args = [
                "python",
                "background_enhancement.py",
                "--input_image_path", self.scene_image_path,
                "--output_dir", self.output_folder_path
            ]
            subprocess.run(args, check=True)

            root, ext = os.path.splitext(self.scene_image_path)
            output_hdri_path = os.path.join(self.output_folder_path, f"{os.path.basename(root)}_hdri{ext}")
            self.hdri_image_path = output_hdri_path

        except Exception as exc:
            print(f"Error while generating HDRI image: {exc}")

    def run_pipeline(self):
        """Run the pipeline."""
        startTime = datetime.now()

        if not os.path.exists(self.output_folder_path):
            os.makedirs(self.output_folder_path)

        self.get_normal_map()
        self.get_surface_normal_vector(self.selected_point)
        self.draw_normal_to_surface()
        self.generate_hdri_image()
        self.generate_scene()

        print("Pipeline run time:", datetime.now() - startTime)


if __name__ == "__main__":
    pipeline = Pipeline()
    pipeline.run_pipeline()
