# 👩‍🎓 Generative AI for 2.5D content creation with depth-guided object placement
Implementation of the "Generative AI for 2.5D content creation with depth-guided object placement" pipeline as the part of the bachelor thesis conducted by [Viktoriia Maksymiuk](https://www.linkedin.com/in/vihtoriaaa/) under the supervision of [Dr. Mikołaj Jankowski](https://scholar.google.com/citations?user=NENQPkQAAAAJ&hl=en). It was submitted in fulfilment of the requirements for the Bachelor of Science degree in the Department of Computer Science and Information Technologies at the Faculty of Applied Sciences.

## 🦿 Launch instructions
Follow the next steps to set up the pipeline for creating 2.5D content with depth-guided object placement.

### 🧌 Step 1. Setting Up Blender as a Command Line Tool
This guide will walk you through the process of setting up Blender as a command-line tool on various operating systems. Once set up, you'll be able to run Blender from the command line by simply typing `blender`.

#### Prerequisites
Before you begin, ensure that you have Blender installed on your system. You can download the latest version of Blender from the official website: [Blender Download](https://www.blender.org/download/)

#### Adding Blender to the System Path Permanently
Follow the steps outlined in the tutorial related to your OS to add Blender to the system path permamently. 
- **Windows**: [Windows guideline](https://www.architectryan.com/2018/03/17/add-to-the-path-on-windows-10/)
- **macOS**: [macOS guideline](https://www.architectryan.com/2012/10/02/add-to-the-path-on-mac-os-x-mountain-lion/#.Uydjga1dXDg)
- **Linux**: [Linux guideline](https://www.geeksforgeeks.org/how-to-set-path-permanantly-in-linux/#:~:text=Method%202%3A%20Setting%20a%20Permanent%20%24PATH%20Variable)

To ensure that Blender has been set up correctly, open a new command prompt/terminal window and type `blender`. Blender should launch without any errors.

### 📦 Step 2. Access Repository Code
Clone the repository using the following command:
```bash
git clone https://github.com/Vihtoriaaa/GenAI-2.5D-Content-Creation
```

Move to the proper project folder:
```bash
cd GenAI-2.5D-Content-Creation/
```

### 🐍 Step 3. Set Up Conda environment
To ensure smoother integration and management of dependencies, we recommend using the [Anaconda](https://www.anaconda.com/) package manager to avoid dependency/reproducibility problems.

#### Install Conda
If you haven't already, install Conda for your OS by following the instructions provided in the official [Conda Documentation](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html#regular-installation).

#### Create a Conda Environment with dependencies
> [!NOTE]\
> Before setting up the Conda environment, please note that depending on your chosen configuration (CPU or GPU), the pipeline run will be different, as the CPU pipeline will utilize external sources for specific processes, while for the GPU, every step will run directly on your local machine. Certain processes or computations may be accelerated when using GPU, while they might run slower on the CPU. Make sure to select the appropriate setup that aligns with your system resources and requirements.

- If you have GPU (CUDA) available, create a new Conda environment using the following commands one by one:
```bash
conda env create -f gpu_environment.yaml
conda activate genai-env
```
- If you have CPU only, use the following command:
```bash
conda env create -f cpu_environment.yaml
conda activate genai-env
```
These commands will create a new Conda environment named 'genai-env', install all the necessary packages depending on the selected configuration specified in the corresponding environment file, and activate it.

### 🏃‍♀️ Step 4. Pipeline Run

<details>
<summary><b>GPU configuration set up and run </b></summary>
   
   The GPU-accelerated version is designed for users with local GPU resources who can run the entire pipeline workflow processes locally. For optimal performance when running the GPU version, it is recommended to use an Nvidia GPU with CUDA support and at least 6–8 GB of VRAM, as this configuration ensures efficient processing and sufficient memory for running the pipeline locally.

#### 💐 Installation of automatic1111
GPU pipeline executes the entire workflow locally, starting from scene image generation with Stable Diffusion (SD) and ending with content rendering in Blender. To set everything up for such a run, you need to use **automatic1111**, a web-based interface for the SD model, to simplify and speed up scene creation using its API. Please follow installation instructions from the official repository [automatic1111](https://github.com/AUTOMATIC1111/stable-diffusion-webui?tab=readme-ov-file#installation-and-running). 

#### 🦜 Downloading Stable Diffusion Models

For our pipeline, we decided to utilize the **Juggernaut v7** model, a variant of the Stable Diffusion XL (SDXL) model. The SDXL model is an improved version of the original SD, providing more realistic and detailed generated images. The Juggernaut v7 model is a widely recognized and selected model by the GenAI community on CivitAI, a platform for accessing and collaborating on generative AI models and research. The model can be downloaded from [CivitAI2 link](https://civitai.com/models/133005?modelVersionId=240840), please click on the `1 File` drop-down list on the right and download the model with ".safetensors" extension. 

When the model is downloaded, go to the `stable-diffusion-webui` folder, and then navigate to the `models/Stable-diffusion` folder, where you should see a file named "Put Stable Diffusion checkpoints here.txt." Put the previously downloaded Juggernaut v7 model checkpoint file in this folder. You can also download other models, for instance, the Stable Diffusion v1.5 model checkpoint file [download link](https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.ckpt), also supported for our pipeline. 

The last step is to enable usage of automatic1111 through API. To achieve this, go to `stable-diffusion-webui` folder, right-click on the file `webui-user.bat` and select Edit. Replace the line

```bat
set COMMANDLINE_ARGS=
```
with
```bat
set COMMANDLINE_ARGS=--api
```
> Each individual argument need to be separated by a space.

Additionally, if you have less than 8 GB VRAM on GPU, it is a good idea to add the `--medvram` argument to save memory to generate more images at a time. Add this argument after an api one. Finally, save the changes and double-click the `webui-user.bat` file to run Stable Diffusion.

#### 🎀 Pipeline Run (finally:D)
Now, to run the 2.5D content creation with depth-guided object placement pipeline, follow the next steps using terminal:

1.  
   Move to the place where the `GenAI-2.5D-Content-Creation` project was cloned.
1.  
   Run  `cd pipeline/` to move to folder with pipeline code.
   
2.  To launch the pipeline, run `python gpu_pipeline.py --prompt "{your scene description}"`. Provide the scene description you want to generate for your content.
3.  Wait for the pipeline to generate the scene image. It is necessary to note that you can regenerate images if needed; you will be asked during the generation process whether to proceed with the generated image.
4.  After the scene image is generated, you will be asked to provide the 3D object you want to place within the generated scene; please choose an appropriate one. The object has to be of ".fbx" extension.
5.  When the object is selected, you will be asked to choose where to place the previously provided object. A scene image is displayed. You can then simply click on any location within the generated scene image where you wish to place your 3D object. When the desired location is selected, press 'Enter' to continue or 'R' to reselect the location.
6.  You're done 🎉 Wait till the pipeline finishes its execution. Generated 2.5D content results are saved under `pipeline/results` folder, check them out!🧍‍♀️

Other command line arguments that can be provided to configure the pipeline run are listed in the table below:
| Name | Description | Type | Default Value |
| ------- | --------- | ---- | ------------- |
| `negative_prompt` | Negative text promp. | str | `""` (empty string) |
| `width` | Generated image width in pixels | int | `1024` |
| `height` | Generated image height in pixels | int | `1024` |
| `steps` | Number of steps to run the generation process | int | `30` |
| `sampler_name` | Name of the sampler to use | str | `"DPM++ 2M Karras"` |
| `cfg_scale` | CFG scale number | int | `7` |
| `seed` | Seed for reproducibility (-1 for random) | int | `-1` |
| `checkpoint` | Stable Diffusion checkpoint | str | `"juggernautXL_v7Rundiffusion.safetensors [0724518c6b]"` |
| `marigold_checkpoint` | Marigold checkpoint path or hub name | str | `"prs-eth/marigold-lcm-v1-0"` |

To use any of the arguments shown in the table, include them in the command along with `--prompt`. Here's the usage example with all available options:

```bash
python gpu_pipeline.py [-h] --prompt PROMPT [--negative_prompt NEGATIVE_PROMPT] [--width WIDTH] [--height HEIGHT] [--steps STEPS]
                [--sampler_name {DPM++ 2M Karras,Euler a,DPM++ SDE Karras}] [--cfg_scale CFG_SCALE] [--seed SEED]
                [--checkpoint {juggernautXL_v7Rundiffusion.safetensors [0724518c6b],v1-5-pruned-emaonly.safetensors [6ce0161689]}]
                [--marigold_checkpoint {prs-eth/marigold-lcm-v1-0,prs-eth/marigold-v1-0,Bingxin/Marigold}]
```

Additional options for certain arguments:

- **`sampler_name`**:
  - Choices: `"DPM++ 2M Karras"`, `"Euler a"`, `"DPM++ SDE Karras"`

- **`checkpoint`**:
  - Choices:
    - `"juggernautXL_v7Rundiffusion.safetensors [0724518c6b]"`
    - `"v1-5-pruned-emaonly.safetensors [6ce0161689]"`

- **`marigold_checkpoint`**:
  - Choices:
    - `"prs-eth/marigold-lcm-v1-0"` (LCM version - faster speed)
    - `"prs-eth/marigold-v1-0"`
    - `"Bingxin/Marigold"`

</details>

<details>
<summary><b>CPU configuration set up and run</b></summary>
   The CPU-based version is for users with limited computational resources, therefore, certain pipeline steps, such as scene image and depth map generation, will rely on external services. This approach ensures all users can test and use the project regardless of their system’s capabilities. To enable pipeline run, follow the next steps.

#### 🧝‍♀️ Scene image generation with Stable Diffusion XL (SDXL)
For our pipeline, we decided to utilize the **Juggernaut v7** model, a variant of the Stable Diffusion XL (SDXL) model. The SDXL model is an improved version of the original SD, providing more realistic and detailed generated images. The Juggernaut v7 model is a widely recognized and selected model by the GenAI community on CivitAI, a platform for accessing and collaborating on generative AI models and research. To generate a scene image, you can use spaces on Hugging Face for SDXL. At least two Hugging Face spaces are available for scene image generation with the Juggernaut v7 model. These are: [Option A](https://huggingface.co/spaces/prodia/sdxl-stable-diffusion-xl) and [Option B](https://huggingface.co/spaces/artificialguybr/JUGGERNAUT-XL-FREE-DEMO). Generate the needed scene image by providing the text prompt describing it, and then download the generated image and put it into the project folder somewhere.

#### 🦆 Depth map estimation with Marigold
For our pipeline, we decided to utilize the [Marigold](https://marigoldmonodepth.github.io) model for depth map estimation because of its significant advancement for the Monocular Depth Estimation (MDE) task within the computer vision area. Moreover, it is fast and easy to use to capture the necessary depth information for realistic object placement. To generate a depth map for the scene image, you can use the following [Hugging Face space](https://huggingface.co/spaces/prs-eth/marigold). Please provide the previously SD-generated and saved scene image as input and wait for the output results. Download an image with "_depth_16bit.png" on its name. This is a file we need for our pipeline.

#### 🎀 Pipeline Run
Now, to run the 2.5D content creation with depth-guided object placement pipeline, follow the next steps using terminal:

1.  
   Have generated scene image, its depth map, and selected 3D object to appropriate folders.
   
2.  Run `cd pipeline/` to move to folder with pipeline code.
3.  Run `python cpu_pipeline.py` to launch the pipeline.
4.  You will be asked to provide the 3D object you want to place within the generated scene; please choose an appropriate one. The object has to be of ".fbx" extension.
5.  When the object is selected, you will be asked to choose where to place the previously provided object. A scene image is displayed. You can then simply click on any location within the generated scene image where you wish to place your 3D object. When the desired location is selected, press 'Enter' to continue or 'R' to reselect the location.
6.  You're done 🎉 Wait till the pipeline finishes its execution. Generated 2.5D content results are saved under `pipeline/results` folder, check them out!🧍‍♀️
</details>

### 🗃️ Repository Organization
This repository is organized into several directories, each serving a specific function. Below is a description of each directory:

- `3d_objects`: a 3D object folder with an example of an object used for pipeline 2.5D content creation.
- `depth_maps`: an image folder with examples of depth maps generated with the Marigold model.
- `colored_depth_maps`: an image folder with examples of colored depth maps generated with the Marigold model.
- `rendered_results`: an image folder with examples of the pipeline's final results of 2.5D content.
- `to_depth`: an image folder with examples of scene images generated with the Stable Diffusion model.
- `pipeline`: a folder containing pipeline implementation code. Here is a general overview of the files contained in this folder:

| Name                          | Description                                                                                                                          |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `background_enhancement.py`         | Contains the code for High Dynamic Range Imaging (HDRI) image generation, used to provide a realistic and natural lighting source for the 2.5D scene.                                |
| `blender.py`         | Contains the code for content creation using Blender API.                            |
| `cpu_pipeline.py`         | Contains CPU-based pipeline version code used by users with limited computational resources.                         |
| `gpu_pipeline.py`         | Contains GPU-accelerated pipeline version code used by users with local GPU resources.                                                           |
| `depthToNormal.py`           | Contains the code for surface normal map estimation from depth map.                                                             |
| `depth_estimation_marigold.py` | Contains the code for local depth map estimation with the Marigold model. Used only for the GPU pipeline version.                  |
| `extract_clicked_points.py`                 | Contains the code to extract the points clicked on the image. Saves the points' coordinates to the "clicked_points.txt" file, which can be used with the DepthToNormalMap file to visualize extracted surface normals for clicked points. |
| `payload_base.json`                 | Contains default configuration json data used for API calls to the automatic1111 API to generate scene images with Stable Diffusion. Used only for the GPU pipeline version. |
| `diode_metrics.ipynb`                 | Contains the code used to process the [DIODE](https://diode-dataset.org) Indoor validation dataset and extract surface normal estimation metrics. |
| `results/`                 | Folder containing intermediate images generated during the pipeline run. Files such as: for CPU version - HDRI images, for GPU version - generated scene images with Stable Diffusion, their depth maps (with colored version), HDRI images. |

### 👩‍🌾 Contributors
- [Viktoriia Maksymiuk](https://www.linkedin.com/in/vihtoriaaa/)
- [Dr. Mikołaj Jankowski](https://scholar.google.com/citations?user=NENQPkQAAAAJ&hl=en)

### 🎫 License
Distributed under the [**MIT**](https://github.com/Vihtoriaaa/GenAI-2.5D-Content-Creation/blob/main/LICENSE) license.
