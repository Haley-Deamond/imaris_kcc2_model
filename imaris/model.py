

class IntensityVolumeData:
    """
    Each data point is defined by various parameters, including the animal, sex, drug treatment etc.

    """
    def __init__(self, drug:bool=None, sex:str=None,animal:int=None,section:int=None,neuron:str=None,layer:int=None,
                 disease:str=None,location:str=None,
                 volume:list=None, intensity:list=None):

        self._drug = drug #type:bool
        """if the animal was treated with a drug or not"""

        self._sex = sex #type: str
        """if the animal is a male val="male" or a female val= "female" """

        self._animal = animal #type: int
        """animal number"""

        self._section = section #type: int
        """section number"""

        self._neuron = neuron #type: str
        """val="inhibitory" or val="excitatory" """

        self._layer = layer #type: int
        """layer in the section"""

        self._disease = disease #type: str
        """If the dataset represent the infected part of the animal ("ipsi") or not ("contra")"""

        self._location = location #type:str
        """intracellular (val="intra") or membrane (val="membrane") """

        if volume is not None:
            self._volume = volume
        else:
            self._volume = []
        """volume of each neuron, index match with intensity"""

        if intensity is not None:
            self._intensity = intensity
        else:
            self._intensity = []
        """intensity of each neuron, index match with volume"""

    @property
    def drug(self):
        return self._drug

    @drug.setter
    def drug(self, drug:bool):
        self._drug = drug

    @property
    def sex(self):
        return self._sex

    @sex.setter
    def sex(self, sex:str):
        self._sex = sex

    @property
    def animal(self):
        return self._animal

    @animal.setter
    def animal(self,animal:int):
        self._animal = animal

    @property
    def section(self):
        return self._section

    @section.setter
    def section(self, section:int):
        self._section = section

    @property
    def neuron(self):
        return self._neuron

    @neuron.setter
    def neuron(self, neuron:str):
        self._neuron = neuron

    @property
    def layer(self):
        return self._layer

    @layer.setter
    def layer(self, layer:int):
        self._layer = layer

    @property
    def disease(self):
        return self._disease

    @disease.setter
    def disease(self, disease:bool):
        self._disease = disease

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, location:str):
        self._location = location

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, volume:list):
        self._volume = volume

    @property
    def intensity(self):
        return self._intensity

    @intensity.setter
    def intensity(self, intensity:list):
        self._intensity = intensity

    def to_json(self)->dict:
        return {
            "drug":self.drug,
            "sex": self.sex,
            "animal": self.animal,
            "section":self.section,
            "neuron":self.neuron,
            "layer":self.layer,
            "disease":self.disease,
            "location":self.location,
            "volume":self.volume,
            "intensity": self.intensity
        }

class ResearchData:
    """
    Contains all data points (IntensityVolumeData) in the dataset.

    More could be done in the future to query data.
    """
    def __init__(self):
        self._datapoints = []

    def add_data(self, point:IntensityVolumeData):
        self._datapoints.append(point)

    def to_json(self):
        index = 0
        json_dict = {}
        for model in self._datapoints:#type: IntensityVolumeData
            json_dict[index] = model.to_json()
            index+=1
        return json_dict

def _from_dict_to_int_vol(dict_obj)-> IntensityVolumeData:
    """
    create one data point from a dictionary
    :param dict_obj dict: originate from IntensityVolumeData.to_json()
    :return:
    """
    model = IntensityVolumeData(drug=dict_obj["drug"],
                                sex=dict_obj["sex"],
                                animal=dict_obj["animal"],
                                section=dict_obj["section"],
                                neuron=dict_obj["neuron"],
                                layer=dict_obj["layer"],
                                disease=dict_obj["disease"],
                                location=dict_obj["location"],
                                volume=dict_obj["volume"],
                                intensity=dict_obj["intensity"]
                                )
    return model

def _from_dict_to_research_data(dict_obj)-> ResearchData:
    """
    re-build the research data object based on the saved json file
    :param dict_obj dict:
    :return ResearchData: the data object
    """
    model = ResearchData()
    for object in dict_obj:
        int_vol = _from_dict_to_int_vol(dict_obj[object])
        model.add_data(int_vol)
    return model