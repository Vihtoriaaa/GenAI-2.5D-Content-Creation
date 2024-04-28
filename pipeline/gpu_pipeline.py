import os
import io
import cv2
import json
import torch
import base64
import argparse
import requests
import subprocess
from PIL import Image
from datetime import datetime
from tkinter import filedialog as fd
from depthToNormal import DepthToNormalMap


class Pipeline:
    """A class representing a GPU version of the pipeline for 2.5D content creation with
        depth-guided object placement."""

    def __init__(
        self, prompt, negative_prompt, width, height, steps, sampler_name,
        cfg_scale, seed, checkpoint, marigold_checkpoint
    ):
        """
        Args:
            prompt (str): The scene prompt to guide the image generation process.
            negative_prompt (str): The negative scene prompt to guide the generation process.
            width (int): The width of the generated image.
            height (int): The height of the generated image.
            steps (int): The number of steps in the generation process.
            sampler_name (str): The name of the sampler used in generation.
            cfg_scale (float): The scale factor for the generation configuration.
            seed (int): The seed value for reproducibility.
            checkpoint (str): The path to the Stable diffusion model checkpoint.
            marigold_checkpoint (str): The path to the Marigold model checkpoint.

        Attributes:
            sd_url (str): The automatic1111 url.
            max_depth (int): The maximum depth value used in depth-to-normal conversion.
            output_folder_path (str): The path to the folder where results will be saved.
        """
        self.sd_url = "http://localhost:7860"
        self.max_depth = 255
        self.output_folder_path = "results"
        self.enable_gpu = True if torch.cuda.is_available() else False

        self.prompt = prompt
        self.negative_prompt = negative_prompt
        self.width = width
        self.height = height
        self.steps = steps
        self.sampler_name = sampler_name
        self.cfg_scale = cfg_scale
        self.seed = seed
        self.checkpoint = checkpoint
        self.marigold_checkpoint = marigold_checkpoint

    def run_pipeline(self):
        """Run the pipeline."""
        print("Running pipeline with the following arguments:")
        print("Prompt:", self.prompt)
        print("Negative prompt:", self.negative_prompt)
        print("Width:", self.width)
        print("Height:", self.height)
        print("Number of steps:", self.steps)
        print("Sampler name:", self.sampler_name)
        print("CFG Scale:", self.cfg_scale)
        print("Seed:", self.seed)
        print("Stable Diffusion checkpoint:", self.checkpoint)
        print("Marigold checkpoint:", self.marigold_checkpoint)
        print("----------------------------------------------")

        startTime = datetime.now()

        if not os.path.exists(self.output_folder_path):
            os.makedirs(self.output_folder_path)
        
        self.run_scene_generation()
        print("Scene image has been generated and selected!")

        _ = input('Exit automatic1111 (input "ok" when done): ')
        self.generate_depth_map()
        print("Depth map has been generated!")

        # Select the 3D object to place at the generated scene
        self.object_3d_path = self.upload_3d_object()
        print("3D object has been selected!")

        # Select the point where to place selected object at the scene
        self.selected_point = self.choose_point(self.scene_image_path)
        print("Target point has been selected!")

        # Get normal map for generated scene image
        self.depth_to_normal_converter = DepthToNormalMap(self.depth_map_path, max_depth=self.max_depth)
        self.get_normal_map()
        print("Normal map has been generated!")

        # Get surface normal vector for the selected point
        self.get_surface_normal_vector(self.selected_point)
        self.draw_normal_to_surface()

        # Generated HDRI image for scene lightning
        self.generate_hdri_image()
        print("HDRI image has been generated!")

        self.generate_blender_scene()

        print("Pipeline run time:", datetime.now() - startTime)

    def generate_scene(self):
        """Run scene image generation process using provided arguments for the model."""
        try:
            url = self.sd_url + "/sdapi/v1/options"

            payload = {'sd_model_checkpoint': self.checkpoint}
            response = requests.post(url=url, json=payload)

            url = self.sd_url + "/sdapi/v1/txt2img"
            with open("payload_base.json", "r") as f:
                payload = json.load(f)

            payload["override_settings"]["sd_model_checkpoint"] = self.checkpoint
            payload["prompt"] = self.prompt
            payload["negative_prompt"] = self.negative_prompt
            payload["width"] = self.width
            payload["height"] = self.height
            payload["steps"] = self.steps
            payload["sampler_name"] = self.sampler_name
            payload["cfg_scale"] = self.cfg_scale
            payload["seed"] = self.seed

            print("Generating scene image...")
            response = requests.post(url=url, json=payload)
            return response.json()["images"][0]

        except Exception as exc:
            print(f"Error while generating scene image: {exc}")

    def run_scene_generation(self):
        """Run scene image generation process using provided text prompt. Process continues
            generating images until the user receives one they consider good enough to proceed with."""
        try:
            scene_img = self.generate_scene()
            print("Scene image generated!")
    
            prompt_words = self.prompt.split()[:5]
            cleaned_words = [word.replace(',', '').replace('.', '') for word in prompt_words]
            image_name = f"scene_{'_'.join(cleaned_words)}.png"
            self.scene_image_path = os.path.join(self.output_folder_path, image_name)

            img = Image.open(io.BytesIO(base64.b64decode(scene_img)))
            img.save(self.scene_image_path)
            print(f"Scene image saved in folder {self.output_folder_path} as {image_name}")

            img = Image.open(self.scene_image_path)
            img.show()

            # Ask user whether generated image is good enought to proceed with
            while True:
                user_input = input("Proceed with the generated image? (yes/no): ").strip().lower()
                if user_input == 'yes':
                    break
                elif user_input == 'no':
                    self.run_scene_generation()
                    break
                else:
                    print("Invalid input. Please enter 'yes' or 'no'.")
        
        except Exception as exc:
            print(f"Error while generating scene image: {exc}")

    def generate_depth_map(self):
        """Run depth map generation process from the scene image using Marigold model."""
        try:
            args = [
                "python",
                "depth_estimation_marigold.py",
                "--checkpoint", self.marigold_checkpoint,
                "--input_image_path", self.scene_image_path,
            ]
            subprocess.run(args, check=True)

            root, ext = os.path.splitext(self.scene_image_path)
            output_depth_path = f"{root}_depth{ext}"
            self.depth_map_path = output_depth_path

        except Exception as exc:
            print(f"Error while generating depth image: {exc}")

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

    def generate_blender_scene(self):
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
                "--input_image_path", self.scene_image_path
            ]
            subprocess.run(args, check=True)

            root, ext = os.path.splitext(self.scene_image_path)
            output_hdri_path =  f"{root}_hdri{ext}"
            self.hdri_image_path = output_hdri_path

        except Exception as exc:
            print(f"Error while generating HDRI image: {exc}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate scene images from text prompts."
    )
    parser.add_argument(
        "--prompt",
        type=str,
        help="Text prompt",
        required=True
    )
    parser.add_argument(
        "--negative_prompt",
        type=str,
        help="Negative text prompt",
        required=False,
        default="",
    )
    parser.add_argument(
        "--width",
        type=int,
        help="Generated image width",
        required=False,
        default=1024
    )
    parser.add_argument(
        "--height",
        type=int,
        help="Generated image height",
        required=False,
        default=1024
    )
    parser.add_argument(
        "--steps",
        type=int,
        help="Number of steps to run",
        required=False,
        default=30
    )
    parser.add_argument(
        "--sampler_name",
        type=str,
        help="Sampler name",
        required=False,
        default="DPM++ 2M Karras",
        choices=["DPM++ 2M Karras", "Euler a", "DPM++ SDE Karras"]
    )
    parser.add_argument(
        "--cfg_scale",
        type=int,
        help="CFG scale number",
        required=False,
        default=7
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Seed",
        required=False,
        default=-1
    )
    parser.add_argument(
        "--checkpoint",
        type=str,
        help="Stable Diffusion checkpoint",
        required=False,
        default="juggernautXL_v7Rundiffusion.safetensors [0724518c6b]",
        choices=[
            "juggernautXL_v7Rundiffusion.safetensors [0724518c6b]",
            "v1-5-pruned-emaonly.safetensors [6ce0161689]"
        ]
    )
    parser.add_argument(
        "--marigold_checkpoint",
        type=str,
        help="Marigold checkpoint path or hub name",
        required=False,
        default="prs-eth/marigold-lcm-v1-0",
        choices=[
            "prs-eth/marigold-lcm-v1-0", #LCM version (faster speed)
            "prs-eth/marigold-v1-0",
            "Bingxin/Marigold"
        ]
    )
    args = parser.parse_args()

    pipeline = Pipeline(
        args.prompt,
        args.negative_prompt,
        args.width,
        args.height,
        args.steps,
        args.sampler_name,
        args.cfg_scale,
        args.seed,
        args.checkpoint,
        args.marigold_checkpoint
    )

    pipeline.run_pipeline()
