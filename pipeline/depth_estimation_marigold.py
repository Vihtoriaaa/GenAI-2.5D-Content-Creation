import os
import torch
import argparse
import numpy as np
from PIL import Image
from diffusers.utils import load_image
from diffusers import DiffusionPipeline


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Run single-image depth estimation using Marigold."
    )
    parser.add_argument(
        "--checkpoint",
        type=str,
        default="prs-eth/marigold-lcm-v1-0",
        choices=["prs-eth/marigold-lcm-v1-0", "prs-eth/marigold-v1-0", "Bingxin/Marigold"],
        help="Checkpoint path or hub name.",
    )
    parser.add_argument(
        "--input_image_path",
        type=str,
        required=True,
        help="Path to the input image.",
    )
    args = parser.parse_args()

    if torch.cuda.is_available():
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")
        print("CUDA is not available. Running on CPU will be slow.")

    print(f"device = {device}")

    marigold_checkpoint = args.checkpoint
    pipe = DiffusionPipeline.from_pretrained(
        marigold_checkpoint,
        custom_pipeline="marigold_depth_estimation"
        # torch_dtype=torch.float16,  # (optional) Run with half-precision (16-bit float).
        # variant="fp16",             # (optional) Use with `torch_dtype=torch.float16`, to directly load fp16 checkpoint
    )
    pipe.to(device)

    img_path = args.input_image_path
    
    root, ext = os.path.splitext(img_path)
    output_depth_path =  f"{root}_depth{ext}"
    output_colored_depth_path =  f"{root}_col_depth{ext}"

    image: Image.Image = load_image(img_path)

    pipeline_output = pipe(
        image,                    # Input image.
        # ----- recommended setting for DDIM version -----
        # denoising_steps=10,     # (optional) Number of denoising steps of each inference pass. Default: 10.
        # ensemble_size=10,       # (optional) Number of inference passes in the ensemble. Default: 10.
        # ------------------------------------------------
        # ----- recommended setting for LCM version ------
        # denoising_steps=4,
        # ensemble_size=5,
        # -------------------------------------------------
        # processing_res=768,     # (optional) Maximum resolution of processing. If set to 0: will not resize at all. Defaults to 768.
        # match_input_res=True,   # (optional) Resize depth prediction to match input resolution.
        # batch_size=0,           # (optional) Inference batch size, no bigger than `num_ensemble`. If set to 0, the script will automatically decide the proper batch size. Defaults to 0.
        # seed=2024,              # (optional) Random seed can be set to ensure additional reproducibility. Default: None (unseeded). Note: forcing --batch_size 1 helps to increase reproducibility. To ensure full reproducibility, deterministic mode needs to be used.
        # color_map="Spectral",   # (optional) Colormap used to colorize the depth map. Defaults to "Spectral". Set to `None` to skip colormap generation.
        show_progress_bar=True, # (optional) If true, will show progress bars of the inference progress.
    )

    depth: np.ndarray = pipeline_output.depth_np                    # Predicted depth map
    depth_colored: Image.Image = pipeline_output.depth_colored      # Colorized prediction

    #marigold by default produces depth map where black is front, for controlnets etc. we want the opposite
    inverse_depth = 1.0 - depth

    if os.path.exists(output_depth_path):
        print(f"Existing file: depth map '{output_depth_path}' will be overwritten")

    if os.path.exists(output_colored_depth_path):
        print(f"Existing file: colorized depth map '{output_colored_depth_path}' will be overwritten")

    # Save as uint16 PNG
    depth_uint16 = (inverse_depth * 65535.0).astype(np.uint16)
    Image.fromarray(depth_uint16).save(output_depth_path, mode="I;16")

    # Save colorized depth map
    depth_colored.save(output_colored_depth_path)
