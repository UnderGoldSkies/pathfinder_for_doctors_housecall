from setuptools import find_packages, setup
from typing import List

def get_requirements(file_path:str)->List[str]:
    """
    this function will return a list of requirements
    """

    #initialize a empty requirements list to read
    requirements=[]

    #open requirements.txt, read line by line and replace \n with ""
    with open(file_path) as file_obj:
        requirements=file_obj.readlines()
        requirements=[line.replace("\n","") for line in requirements]

    return requirements



setup(
name = 'pathfinder_for_doctor_housecall',
version= '0.0.1',
author= 'JackWeiXuan',
author_email= 'jackweixuan@gmail.com',
description= 'pathfinder_for_doctor_housecall',
url='https://github.com/UnderGoldSkies/pathfinder_for_doctors_housecall',
packages=find_packages(),
install_requires=get_requirements('requirements.txt')
)
