# Installation instructions
This software is being developed in Python 3.8.

## Guideline for Windows, Linux and MacBook with Intel Chip

# Anaconda installation
Anaconda free community edition can be downloaded from [Anaconda Website](https://www.anaconda.com/products/distribution). For Windows, please follow this [tutorial](https://www.datacamp.com/tutorial/installing-anaconda-windows) to install Anaconda and make sure to check 'Add Anaconda to my PATH environment variable' in Step 6. After following the tutorial, you should be able to search and open 'Anaconda PowerShell Prompt' and get a prompt similar to the following screenshot:
<p align="center">
  <img width="550" height="320" src="https://github.com/cnr-isti-vclab/MoReLab/blob/main/readme_images/prompt_screenshot.png">
</p>

# Environment setup and installation of requirements
Open Anaconda Powershell prompt and enter the following commands:

- Create a Python 3.8 environment by entering the command:
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

- Move to the repository:
~~~
cd MoReLab
~~~

- Install all python libraries using the following command:
~~~
pip install -r requirements.txt
~~~



## Guideline to install PyQt5 on MacBook with Apple M1 or M2 chip
On Apple Silicon chip, requirements may fail to get installed. On a Macbook with Apple M1 or M2 chip (instead of Intel), this command throws error. The solution has been stated [here](https://stackoverflow.com/questions/65901162/how-can-i-run-pyqt5-on-my-mac-with-m1chip). The steps are as follows:
- First, we have to open mac terminal in Rosetta mode as explained in this [article](https://dev.to/courier/tips-and-tricks-to-setup-your-apple-m1-for-development-547g) . For this, go to **Applications/utilities/** and right click on terminal to create it's copy. Rename the copy as **Rosetta-Terminal**. Then right click again and go to **Get info**. Check  **Open using Rosetta** option and then close. With Cmd + Space, open up "Rosetta-Terminal". To confirm, enter the command **arch** which should return i386. If it returns, arm64 then the terminal is not in Rosetta mode.
- Create and activate a virtual enrvironment using the following commands. Anaconda virtual environments might not work. It's better to create system's own virtual environment using the following commands.
~~~
/usr/bin/python3 -m venv env
source env/bin/activate
~~~
- Now, enter the following commands and PyQt should be installed successfully.
~~~
pip install --upgrade pip
pip install PyQt5
~~~

- Install all python libraries using the following command:
~~~
pip install -r requirements.txt
~~~


