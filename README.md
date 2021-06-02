# imaris_kcc2_model

Overall Objective:
Extract and analyze data from IMARIS computation.

Logic:
In IMARIS, 288 microscopy images were manipulated to create surface rendered neurons such that levels of intracellular and extracellular ion channels could be quantified in specific neuron populations.
Each image manipulation creates 2 excel read-outs with a minimum of 50 sheets of data. Of interest are the intensity sum values, the volume values, the neuron ID, and the neuron coordinates. A minimum of 30 neuron values are listed in each sheet.
As making manual calculations between the 576 excel files with thousands of values would be infeasible, a script was written to automate the task.

Tasks:
The script retrieves data and sorts by animal, sex, drug treatment, neuron type, disease state, and location of ion channel. Then using the coordinates of each neuron, the intensity sum value from one file is matched with the corresponding volume value from another file, and subsequent calculations are performed.
These matched values are then normalized by pairing the disease state with the corresponding average healthy state intensity sum values.

Once values are retrieved, organized, and calculated they are plotted for subsequent statistical analysis in GraphPad software. The script allows the user to import the pre-formatted .csv file into GraphPad, again semi-automating a previous tedious manual task.
Overall, the benefits of this script is that it minimizes human error throughout the calculation process, allows for multiple iterations should an error be detected, and increases user efficiency as a result of task automation.

Structure:
imaris.build_model.build_research_data() - Used as an entry point to retrieve data.
imaris.model - Data structure.
imaris.xls_reader - To read excel files.
