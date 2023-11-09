# Installation instructions
This software is being developed in Python 3.8.

## Guideline for Windows and Linux

### Anaconda installation
Anaconda free community edition can be downloaded from [Anaconda Website](https://www.anaconda.com/products/distribution). For Windows, please follow this [tutorial](https://www.datacamp.com/tutorial/installing-anaconda-windows) to install Anaconda and make sure to check 'Add Anaconda to my PATH environment variable' in Step 6. After following the tutorial, you should be able to search and open 'Anaconda PowerShell Prompt' and get a prompt similar to the following screenshot:
<p align="center">
  <img width="550" height="320" src="https://github.com/cnr-isti-vclab/MoReLab/blob/main/readme_images/prompt_screenshot.png">
</p>

### Environment setup and installation of requirements

- Open Anaconda Powershell prompt and create a Python 3.8 environment by entering the command:
~~~
conda create --name morelab_env python=3.8
~~~

- Activate the environment by entering the command
~~~
conda activate morelab_env
~~~

- Clone this repository using the command:
~~~
git clone https://github.com/cnr-isti-vclab/MoReLab.git
~~~

- Also clone the SuperGlue repository using this command:
~~~
git clone https://github.com/magicleap/SuperGluePretrainedNetwork.git
~~~

- Copy the folder of models from SuperGlue repository to . You can do it manually or use this command:
~~~
cp -r SuperGluePretrainedNetwork/models MoRelab/
~~~

- Move to the repository:
~~~
cd MoReLab
~~~

- Install all python libraries using the following command:
~~~
pip install -r requirements.txt
~~~

- If previous command installs all libraries, then run the following command to run software:
~~~
python main.py
~~~
