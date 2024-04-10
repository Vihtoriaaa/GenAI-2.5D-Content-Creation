# Generative AI for 2.5D content creation with depth-guided object placement
Bachelor Thesis Repository

## Launch instructions

### Step 1. Setting Up Blender as a Command Line Tool
This guide will walk you through the process of setting up Blender as a command-line tool on various operating systems. Once set up, you'll be able to run Blender from the command line by simply typing `blender`.

#### Prerequisites
Before you begin, ensure that you have Blender installed on your system. You can download the latest version of Blender from the official website: [Blender Download](https://www.blender.org/download/)

#### Adding Blender to the System Path Permanently
Follow the steps outlined in the tutorial related to your OS to add Blender to the system path permamently. 
- **Windows**: [Windows guideline](https://www.architectryan.com/2018/03/17/add-to-the-path-on-windows-10/)
- **macOS**: [macOS guideline](https://www.architectryan.com/2012/10/02/add-to-the-path-on-mac-os-x-mountain-lion/#.Uydjga1dXDg)
- **Linux**: [Linux guideline](https://www.geeksforgeeks.org/how-to-set-path-permanantly-in-linux/#:~:text=Method%202%3A%20Setting%20a%20Permanent%20%24PATH%20Variable)

To ensure that Blender has been set up correctly, open a new command prompt/terminal window and type `blender`. Blender should launch without any errors.

### Step 2. Access Repository Code
Clone the repository using the following command:
```bash
git clone https://github.com/Vihtoriaaa/GenAI-2.5D-Content-Creation
```

Move to the proper project folder:
```bash
cd GenAI-2.5D-Content-Creation/
```

### Step 3. Set Up Conda environment
To ensure smoother integration and management of dependencies, we recommend using the [Anaconda](https://www.anaconda.com/) package manager to avoid dependency/reproducibility problems.

#### Install Conda
If you haven't already, install Conda for your OS by following the instructions provided in the official [Conda Documentation](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html#regular-installation).

#### Create a Conda Environment with dependencies
> [!NOTE]\
> Before setting up the Conda environment, please note that depending on your chosen configuration (CPU or GPU), the pipeline run will be different, as the CPU pipeline will utilize external sources for specific processes, while for the GPU, every step will run directly on your local machine. Certain processes or computations may be accelerated when using GPU, while they might run slower on the CPU. Make sure to select the appropriate setup that aligns with your system resources and requirements.

- If you have GPU (CUDA) available, create a new Conda environment using the following commands one by one:
```bash
conda env create -n env -f gpu_environment.yaml
conda activate env
```
- If you have CPU only, use the following command:
```bash
conda env create -n env -f cpu_environment.yaml
conda activate env
```
These commands will create a new Conda environment named 'env', install all the necessary packages depending on the selected configuration specified in the corresponding environment file, and activate it.

### Step 4. Pipeline Run

<details>
<summary><b>GPU configuration run </b></summary>

1.  
   TODO
   
2.  Run `cd pipeline/` to move to folder with pipeline code.
3.  Run `python pipeline.py` to launch the pipeline.
4.  You're done 🎉
</details>


<details>
<summary><b>CPU configuration run</b></summary>

1.  
   Add generated scene image, its depth map, and selected 3D object to appropriate folders.
   
2.  Run `cd pipeline/` to move to folder with pipeline code.
3.  Run `python pipeline.py` to launch the pipeline.
4.  You're done 🎉
</details>

### License
Distributed under the [**MIT**](https://github.com/Vihtoriaaa/GenAI-2.5D-Content-Creation/blob/main/LICENSE) license.
