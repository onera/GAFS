# scenario_generation
Folder : 
 - main.py : System building
             Foresight scenario generation
             Results loading
- scenarios_generation.py : System building functions definition
                            Scenarios generation funtions definition
- main_analysis.py 
- tools.py
- analyse_bdd_general
- analyse_spmf


To generate the scenarios, run the main.py file.
You can choose the depth of the tree (example has been run with a depth of 3)
The example has been made using the data of usecase_initialdata.xlsx, result can be read in allscenarios_output.txt 

The main_analysis.py file can be run next (uncomment the parts you need).
It returns :
- statistics and values of variables never reached
- goal achievements information
- statistics on conflicts
- scenarios representation (using bokeh library)
- sequential rule mining 
    - run the 2 first functions (inputBDDspmf, inputspmfprincipe)
    - use spmf to produce the files for the following analysis part (https://www.philippe-fournier-viger.com/spmf/index.php?link=download.php)
        - the example files have been produced using :
            - RuleGrowth (min sup = 0.005 and minconf = 0.6) (output_miniusecase1_usereasyflight.txt) 
            - PrefixSpan (minsup = 0.1) (output_miniusecase_usereasyflight_prefixspan.txt)
    - run the end of the analysis file

- best scenarios retrieving (return the result in a readable file : bestscenarios_output.txt)
