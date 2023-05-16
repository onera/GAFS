# -*- coding: utf-8 -*-
"""
Created on Mon Oct 18 15:36:45 2021

@author: cablanch
"""
import pandas as pd

def tablecreation(fichier):
    # opinions of the agents on the moral principles
    data_opinions = pd.read_excel(fichier, 
                                  header = [0,1] , 
                                  index_col = [0,1] , 
                                  sheet_name = "opinions")


# positions of the agents on the moral principles

    data_positions = pd.read_excel(fichier,
                               header = 0,
                               index_col = 0,
                               sheet_name = "positions")


# user
    data_user = pd.read_excel(fichier,
                                 header = 0,
                                 index_col = 0,
                                 sheet_name = "user") 


# possible decisions of the agents
    data_decision = pd.read_excel(fichier,
                              header = 0,
                              sheet_name = "decision")

# law of the domain (logical conflict)
    data_logicalconstraints = pd.read_excel(fichier,
                                       header = 0,
                                       sheet_name = "logicalcon")

# law of the domain (moral conflict: decision against a principle by nature)
    data_againstprinciple = pd.read_excel(fichier,
                                        header = 0,
                                        sheet_name = "agppe")


# initial state
    data_initialstate = pd.read_excel(fichier,
                                          header = 0,
                                          index_col = 0,
                                          sheet_name = "initstate")

    
# goals of the user
    data_goals = pd.read_excel(fichier, 
                                      header = 0,
                                      sheet_name = "goals")
    
    return(data_opinions,data_positions,data_user,data_decision, 
           data_logicalconstraints, data_againstprinciple, data_initialstate, data_goals)