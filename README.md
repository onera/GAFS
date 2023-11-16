# installation

use the pipreqs.txt file to install the required library

# scenario_generation
Folder : 
 - main.ipynb (Notebook file): System building
                               Foresight scenario generation
                               Results storage
- scenarios_generation.py : System building functions definition
                            Scenarios generation funtions definition
- main_analysis.ipynb 
- tools.py
- analyse_bdd_general
- analyse_spmf


To generate the scenarios, run the main.ipynb notebook file.
You can choose the depth of the tree (example has been run with a depth of 3)
The example has been made using the data of usecase_initialdata.xlsx

# analysis

The main_analysis.ipynb notebook file can be run next to analyze the generated scenarios.
It returns :
- general statistics
- conflicts analysis information
    - conflicts statistics
    - sequential rule and pattern mining to avoid conflicts
- goals achievments analysis
- best scenarios retrieving (return the result in a lisible file : result3_copy.txt)
