import numpy as np
from PIL import Image
from diffusers import DiffusionPipeline
from diffusers.utils import load_image
import diffusers
import os


# Directories
repo_dir = "content/Marigold"
input_dir = os.path.join(repo_dir, "input")
output_dir = os.path.join(repo_dir, "output")
output_dir_color = os.path.join(output_dir, "depth_colored")
output_dir_tif = os.path.join(output_dir, "depth_bw")
output_dir_npy = os.path.join(output_dir, "depth_npy")


os.makedirs(repo_dir, exist_ok=True)
os.makedirs(input_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

os.chdir(repo_dir)

# !export HF_HOME=$(pwd)/checkpoint


pipe = DiffusionPipeline.from_pretrained(
    "Bingxin/Marigold",
    custom_pipeline="marigold_depth_estimation"
)

pipe = pipe.to("cuda")


img_path_or_url = "to_depth/trees.png"
image = Image.open(img_path_or_url)
# image = image.resize((256, 512))

pipeline_output = pipe(
    image,                  # Input image.
    # denoising_steps=10,     # (optional) Number of denoising steps of each inference pass. Default: 10.
    # ensemble_size=10,       # (optional) Number of inference passes in the ensemble. Default: 10.
    # processing_res=768,     # (optional) Maximum resolution of processing. If set to 0: will not resize at all. Defaults to 768.
    # match_input_res=True,   # (optional) Resize depth prediction to match input resolution.
    # batch_size=0,           # (optional) Inference batch size, no bigger than `num_ensemble`. If set to 0, the script will automatically decide the proper batch size. Defaults to 0.
    # color_map="Spectral",   # (optional) Colormap used to colorize the depth map. Defaults to "Spectral".
    # show_progress_bar=True, # (optional) If true, will show progress bars of the inference progress.
)

depth: np.ndarray = pipeline_output.depth_np                    # Predicted depth map
depth_colored: Image.Image = pipeline_output.depth_colored      # Colorized prediction

# Save as uint16 PNG
depth_uint16 = (depth * 65535.0).astype(np.uint16)
Image.fromarray(depth_uint16).save("./depth_map2.png", mode="I;16")

# Save colorized depth map
depth_colored.save("./depth_colored2.png")
