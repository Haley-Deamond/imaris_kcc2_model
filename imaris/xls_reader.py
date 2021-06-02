import os
import pandas as pd
import json
from model import IntensityVolumeData,ResearchData

# Threshold to ignore small relative and/or absolute difference
relative_value_threshold = 0.015
absolute_value_threshold = 2
intensity_trigger = 10

# Excel file Tab identification
"""Each Excel file contains different tabs with data concerning the intensity mean of neurons. Each tab contains the 
results for a 'channel'. Each channel represents the location of the neurons in the spinal cord location/layer """

membrane_channels = ["Intensity Mean Ch=10 Img=1","Intensity Mean Ch=12 Img=1","Intensity Mean Ch=14 Img=1",
                     "Intensity Mean Ch=16 Img=1"]
"""list of tab names for membrane channels """

intra_channels = [  "Intensity Mean Ch=9 Img=1","Intensity Mean Ch=11 Img=1","Intensity Mean Ch=13 Img=1",
                    "Intensity Mean Ch=15 Img=1"]
"""list of tab names for intracellular channels """

layer_dict = {"Intensity Mean Ch=10 Img=1":1,
        "Intensity Mean Ch=12 Img=1":2,
        "Intensity Mean Ch=14 Img=1":3,
        "Intensity Mean Ch=16 Img=1":4,
        "Intensity Mean Ch=9 Img=1":1,
        "Intensity Mean Ch=11 Img=1":2,
        "Intensity Mean Ch=13 Img=1":3,
        "Intensity Mean Ch=15 Img=1":4
        }
"""Dictionary to identify which channel [key] represents which layer [value] """

"""The Excel files follow a strict naming convention
drug_sex_animal_section_neuron_disease_type.xls

drug -> d (drug) or n (no drug) 
sex -> m (male) or f (female) 
animal -> integer 1 to 12 (animal number)
section -> integer 1 to 3 (section number)
neuron -> i (inhibitory) or e (excitatory)
disease -> c (contra) or i (ipsi) 
type -> i (intensity) or v (volume)
"""

info_dict = {
    0:{"d":True,
       "n":False},
    1:{"m":"male",
       "f":"female"},
    2: None,
    3: None,
    4: {"e":"excitatory",
        "i":"inhibitory"},
    5: {"i":"ipsi",
        "c":"contra"},
}

"""Dictionary to translate file naming convention in booleans or strings
  keys (integers) represent the position in the file name"""

def set_info(info:list, model:IntensityVolumeData):
    """
    set the model (IntensityVolumeData) information (drug, sex, animal, section, neuron, disease) from the file name
    (info) according to the naming convention.
    :param info list: parsed file name (from get_info)
    :param model IntensityVolumeData: model containing information and data
    :return: None
    """
    model.drug = info_dict[0][info[0]]
    model.sex = info_dict[1][info[1]]
    model.animal = info[2]
    model.section = info[3]
    model.neuron = info_dict[4][info[4]]
    model.disease = info_dict[5][info[5]]

def get_info(file:str)->list:
    """
    Parse the file name accordingly
    :param file str: Excel file path
    :return: List of identifiers to understand the content of the file
    """
    _, name = os.path.split(file)
    name = name.split(".xls")[0]
    info = name.split("_")
    return info

def get_membrane_data(channel:str,intensity_data:pd.DataFrame,volume_data:pd.DataFrame)-> (list,list):
    """
    Match intensity data to volume data
    Intensity data and Volume data are separated in two different files.
    Neurons do not have the same identifier number. They are matched thanks to their positions (x,y,z)

    X, Y, Z coordinates need to match as regard to both the relative adn absolute threshold.

    NOTE: As a result of high quality software resolution, a simple coordinate analysis is sufficient to identify the neurons.
          There is no need for more complex pairing calculation.

    :param channel str: Name of the channel tab (Excel file Tab)
    :param intensity_data pd.DataFrame: Data in the intensity file
    :param volume_data pd.DataFrame: Data in the volume file
    :return (list,list): list0 volume and list1 intensity. Each index representing the same neuron.
    """
    volume = []
    intensity = []
    for index, row in intensity_data[channel].iterrows():

        intensity_sum = row["Intensity Sum"]
        """iterates through all neurons on the channel"""
        if intensity_sum > intensity_trigger:
            """ small intensities are ignored"""
            ident = row.ID
            """get the neuron ID to get the total volume of the neuron"""
            matching_volume = intensity_data["Volume"][intensity_data["Volume"]["ID"] == ident]
            """here is is expected that the ID is unique """

            volume_total = float(matching_volume["Volume"])
            """total volume of the neuron"""

            matching_position = intensity_data["Position"][intensity_data["Position"]["ID"] == ident]
            """retrieve x, y, z coordinates of the given neuron"""
            intensity_x = float(matching_position["Position X"])
            intensity_y = float(matching_position["Position Y"])
            intensity_z = float(matching_position["Position Z"])

            matching_volume_position_x = volume_data["Position"][( ((volume_data["Position"]["Position X"] > (1-relative_value_threshold)*intensity_x) & (volume_data["Position"]["Position X"] < (1+relative_value_threshold)*intensity_x)) | ((volume_data["Position"]["Position X"] > intensity_x-absolute_value_threshold) & (volume_data["Position"]["Position X"] < intensity_x+absolute_value_threshold)))]
            matching_volume_position_y = volume_data["Position"][( ((volume_data["Position"]["Position Y"] > (1-relative_value_threshold)*intensity_y) & (volume_data["Position"]["Position Y"] < (1+relative_value_threshold)*intensity_y)) | ((volume_data["Position"]["Position Y"] > intensity_y-absolute_value_threshold) & (volume_data["Position"]["Position Y"] < intensity_y+absolute_value_threshold)))]
            matching_volume_position_z = volume_data["Position"][( ((volume_data["Position"]["Position Z"] > (1-relative_value_threshold)*intensity_z) & (volume_data["Position"]["Position Z"] < (1+relative_value_threshold)*intensity_z)) | ((volume_data["Position"]["Position Z"] > intensity_z-absolute_value_threshold) & (volume_data["Position"]["Position Z"] < intensity_z+absolute_value_threshold)))]
            """match for x,y and z all the neurons in the volume file that are considered close to the neurons 
            in the intensity file.
            LOGIC: look for  all neurons that are either in the acceptable relative distance OR
                    in an acceptable absolute distance.
             """

            matching_volume_position_x_index = matching_volume_position_x.index.tolist()
            matching_volume_position_y_index = matching_volume_position_y.index.tolist()
            matching_volume_position_z_index = matching_volume_position_z.index.tolist()
            """get the list of neurons that can match the given intensity neuron (row) """

            matching_index = list(set(matching_volume_position_x_index) & set(matching_volume_position_y_index) & set(matching_volume_position_z_index))
            """get the common index for the 3 coordinates
             Normally only one neuron will match"""
            if len(matching_index) !=1:
                print("--------------")
                print("----- ERROR -----")
                print(channel)
                print("ID", ident)
                print("Volume total", volume_total)
                print("INTENSITY SUM Value", intensity_sum)
                print("X,Y,Z", intensity_x,intensity_y,intensity_z)
                print("Matching X",matching_volume_position_x_index)
                print("Matching Y", matching_volume_position_y_index)
                print("Matching Z", matching_volume_position_z_index)
                print("MATCHING", matching_index)
                print("--------------")
            else:
                ident_intra = int(volume_data["Position"].iloc[matching_index]["ID"])
                volume_intra = float(volume_data["Volume"][volume_data["Position"]["ID"] == ident_intra]["Volume"])
                """get intracelullar volume from the Volume file for the matching neuron"""
                volume_membrane = volume_total - volume_intra
                """calculates the membrane volume"""

                intensity.append(intensity_sum)
                if channel in membrane_channels:
                    if volume_membrane < 0:
                        print("--------------")
                        print("----- ERROR -----")
                        print("ERROR: negative volume")
                        print(channel)
                        print("ID intensity", ident)
                        print("ID intra", ident_intra)
                        print("X,Y,Z", intensity_x, intensity_y, intensity_z)
                        print("MATCHING index", matching_index)
                        print("volume total", volume_total)
                        print("Volume intra", volume_intra)
                        print("volume membrane",volume_membrane)
                        print("--------------")
                    else:
                        volume.append(volume_membrane)
                elif channel in intra_channels:
                    volume.append(volume_intra)
                """Adding volume depending on location (intra vs membrane) """
    return volume, intensity

def read_xls(intensity_file:str, volume_file:str)-> list:
    print("\n\n---------------------------- !!!!!!!!!!!!!!!!!!!!!! ----------------------\n")
    print("STARTING ANALYSIS FOR ", intensity_file, "and ", volume_file)
    models = []
    info = get_info(intensity_file)


    intensity_data = pd.read_excel(intensity_file, sheet_name=["Position", 'Volume',
                                                               "Intensity Sum Ch=9 Img=1","Intensity Sum Ch=10 Img=1",
                                                               "Intensity Sum Ch=11 Img=1","Intensity Sum Ch=12 Img=1",
                                                               "Intensity Sum Ch=13 Img=1","Intensity Sum Ch=14 Img=1",
                                                               "Intensity Sum Ch=15 Img=1","Intensity Sum Ch=16 Img=1"],
                                    header = 1)

    volume_data = pd.read_excel(volume_file, sheet_name= ["Position", 'Volume'],header = 1)

    for channel in membrane_channels+intra_channels:
        model = IntensityVolumeData()
        models.append(model)
        if channel in membrane_channels:
            model.location = "membrane"
        if channel in intra_channels:
            model.location = "intra"

        model.layer = layer_dict[channel]

        set_info(info=info, model=model)
        volume_vals , intensity_vals = get_membrane_data(channel=channel,intensity_data=intensity_data,volume_data=volume_data)
        model.volume = volume_vals
        model.intensity = intensity_vals

    return models

def read_xls_intensity_mean(intensity_file:str,)-> list:
    """
    generates a model with Intensity mean as opposed to intensity sum and with no volume files (no matching)
    :param intensity_file:
    :return:
    """
    print("\n\n---------------------------- !!!!!!!!!!!!!!!!!!!!!! ----------------------\n")
    print("STARTING ANALYSIS FOR ", intensity_file)
    models = []
    info = get_info(intensity_file)


    intensity_data = pd.read_excel(intensity_file, sheet_name=[
                                                               "Intensity Mean Ch=9 Img=1","Intensity Mean Ch=10 Img=1",
                                                               "Intensity Mean Ch=11 Img=1","Intensity Mean Ch=12 Img=1",
                                                               "Intensity Mean Ch=13 Img=1","Intensity Mean Ch=14 Img=1",
                                                               "Intensity Mean Ch=15 Img=1","Intensity Mean Ch=16 Img=1"],
                                    header = 1)


    for channel in intra_channels + membrane_channels:
        model = IntensityVolumeData()
        models.append(model)
        if channel in membrane_channels:
            model.location = "membrane"
        if channel in intra_channels:
            model.location = "intra"
        model.intensity = list(intensity_data[channel]["Intensity Mean"])
        model.layer = layer_dict[channel]

        set_info(info=info, model=model)
        # volume_vals , intensity_vals = get_membrane_data(channel=channel,intensity_data=intensity_data,volume_data=volume_data)
        # model.volume = volume_vals
        # model.intensity = intensity_vals

    return models


if __name__ == '__main__':
    models = read_xls(r"./data/CLP290/intensity_intramem/d_f_2_1_e_c_i.xls", r"./data/CLP290/intra/d_f_2_1_e_c_v.xls") #type:list
    research = ResearchData()
    for model in models:
        research.add_data(point=model)
    with open("model.json", "w") as outfile:
        json.dump(research.to_json(), outfile, indent=4, separators=(',', ': '))