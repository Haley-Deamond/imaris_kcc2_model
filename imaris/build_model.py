from xls_reader import read_xls, get_info, read_xls_intensity_mean
from model import ResearchData
"""this is the model in which all experimental data will be stored"""

import json
import glob



def get_intra_equivalent(info:list, intra_files)->str:
    """
    finds the equivalent intra file based on volume file info
    :param info list: information regarding the volume file
    :param intra_files list: of all files containing intracellular data
    :return str: the corresponding intracellular file path
    """
    for file in intra_files:
        intra_info = get_info(file)
        if intra_info[:-1] == info[:-1]:
            """the corresponding file will have all the same attributes except for the last one (volume vs intensity)"""
            return file

def save_model(research:ResearchData,name:str="model.json"):
    with open(name, "w") as outfile:
        json.dump(research.to_json(), outfile, indent=4, separators=(',', ': '))


def build_research_data(intensity_path:str,intra_path:str):
    """
    Create a python model based on the excel files
    :param intensity_path str: path to the intensity folder
    :param intra_path str: path to the intra (or volume) folder
    :return: None
    """
    model = ResearchData()

    intra_files = glob.glob(intra_path+"/*.xls")
    for intensity_file in glob.glob(intensity_path+"/*.xls"):
        intensity_info = get_info(intensity_file)
        intra_file = get_intra_equivalent(intensity_info,intra_files)
        if intra_file is not None:
            new_points = read_xls(intensity_file=intensity_file,volume_file=intra_file)
            [model.add_data(point) for point in new_points]
        else:
            print("ERROR could not find intra equivalent for", intensity_file)


    save_model(model)
    """saves the model in a json format that can then be reloaded for further analysis"""

def build_research_intensity_mean_data(intensity_path:str):
    """
    Build the resarch model for intensity mean only, no volume files
    :param intensity_path: path to the intensity folder
    :return:
    """
    model = ResearchData()
    for intensity_file in glob.glob(intensity_path+"/*.xls"):
        intensity_info = get_info(intensity_file)
        new_points = read_xls_intensity_mean(intensity_file=intensity_file)
        [model.add_data(point) for point in new_points]
    save_model(model)
