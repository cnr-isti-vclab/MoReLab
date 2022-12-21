# Installation instructions
This software is being developed in Python 3.8 and can be installed by performing the following steps in an anaconda environment or a python virtual environment:

## Steps

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
