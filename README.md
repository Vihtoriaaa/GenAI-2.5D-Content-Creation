## Generative AI for 2.5D content creation with depth-guided object placement
Bachelor Thesis Repository

### Launch instructions

#### Setting Up Blender as a Command Line Tool
This guide will walk you through the process of setting up Blender as a command-line tool on various operating systems. Once set up, you'll be able to run Blender from the command line by simply typing `blender`.

##### Prerequisites
Before you begin, ensure that you have Blender installed on your system. You can download the latest version of Blender from the official website: [Blender Download](https://www.blender.org/download/)

##### Adding Blender to the System Path Permanently
Follow the steps outlined in the tutorial related to your OS to add Blender to the system path permamently. 
- **Windows**: [Windows guideline](https://www.architectryan.com/2018/03/17/add-to-the-path-on-windows-10/)
- **macOS**: [macOS guideline](https://www.architectryan.com/2012/10/02/add-to-the-path-on-mac-os-x-mountain-lion/#.Uydjga1dXDg)
- **Linux**: [Linux guideline](https://www.geeksforgeeks.org/how-to-set-path-permanantly-in-linux/#:~:text=Method%202%3A%20Setting%20a%20Permanent%20%24PATH%20Variable)

##### Testing
To ensure that Blender has been set up correctly, open a new command prompt/terminal window and type `blender`. Blender should launch without any errors.

#### Access Repository Code
Clone the repository using the following command:
```bash
git clone https://github.com/Vihtoriaaa/GenAI-2.5D-Content-Creation
```
Move to the proper folder:
```bash
cd GenAI-2.5D-Content-Creation/
```

#### Creating Conda environment
To ensure smoother integration and management of dependencies, we recommend using Conda to manage both Blender and the required Python packages.
##### Install Conda
If you haven't already, install Conda by following the instructions provided in the official Conda documentation: [Conda Documentation](https://conda.io/projects/conda/en/latest/user-guide/getting-started.html)

##### Create a Conda Environment with dependencies
Create a new Conda environment for this project using the following commands one by one:
```bash
conda create -n env python=3.10 pip
conda activate env
conda install --yes --file requirements.txt
```
These commands will create a new Conda environment named 'env', activate it, and install all the necessary packages specified in the 'requirements.txt' file. 
