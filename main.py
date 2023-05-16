# -*- coding: utf-8 -*-
"""
Created on Wed Oct 20 10:14:57 2021

@author: cablanch
"""

import scenarios_generation 
import TraitementDataconflit
import pandas as pd
import pickle
import tools
import analyse_bdd_general

################### Data ###########################
a = TraitementDataconflit.tablecreation("usecase_initialdata.xlsx")

data_decision = a[3]
data_opinions = a[0]
data_positions = a[1]
data_user = a[2]
data_initialstate = a[6]
data_logicalconstraint = a[4]
data_pplconstraint = a[5]
data_goals = a[7]

###################### System Creation ############################

my_system = scenarios_generation.System({},[],{})

D = scenarios_generation.D_formation(data_decision)

ens_decisions_acteurs_objets = scenarios_generation.decisions_acteurs_objets(D,data_decision)

my_system = scenarios_generation.variables_formation(data_opinions, my_system)
   
my_system = scenarios_generation.acteurs_formation(data_user, ens_decisions_acteurs_objets,my_system,data_decision,data_positions,data_opinions)         
    
my_systeme = scenarios_generation.pp_formations(my_system,data_positions)

for i in data_initialstate.index:
    my_system.v.get(i).valeur_initiale(data_initialstate.loc[i].Valeur)
     
etat_mon_systeme = scenarios_generation.EtatSysteme(data_positions, data_opinions, my_system.renvoyer_etats_variables())

print("System creation done")

#####################################

dict_etat = {} #the file with the system states and there numbers
dict_decision = {}
indice = 1
nbscenarios = [0]
dict_etat.update({1:etat_mon_systeme})
root = scenarios_generation.Node(False,1,[],{}, 0,None)
compteur = 0
MAX_PROF = int(input("Entrer la profondeur max de l'arbre : "))
#MAX_PROF = 3

cutcriteria = [] #if input == [] : return 1 scenario for x scenarios, elses return the first n scenarios

with open('stockage_generation.pkl','wb')as writer :
    t3 = scenarios_generation.treegeneration3(writer,cutcriteria,nbscenarios, indice, dict_etat,root,root,my_system, data_opinions, 
                            data_positions, data_pplconstraint,D, data_logicalconstraint, MAX_PROF, data_goals)



print("End generation")


dict_etat1 = {}
for i in dict_etat :
    dict_etat1.update({i:dict_etat.get(i).etat_variables})
dict_etatex = pd.DataFrame(dict_etat1)
dict_etatex.to_excel('dict_states.xlsx')

data = []
with open('stockage_generation.pkl','rb')as file :
    while True :
        try:
            data.append(pickle.load(file))
        except EOFError:
            break


print("data done")

#-----------Storage------------------
tools.storage(data,'stockage_scenarios.pkl')
tools.storage(dict_etat, 'stockagedict_etat.pkl')
tools.storage(D, 'stockage_d.pkl')
tools.storage(my_system,'stockage_systeme.pkl')

print("Storage done")

tools.allscenariostoreadbetter('allscenarios_output.txt', data, dict_etat)
print(analyse_bdd_general.statistiques(data, dict_etat, data_opinions))