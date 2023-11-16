# -*- coding: utf-8 -*-
"""
Created on Tue Sep 28 10:21:25 2021

@author: cablanch
"""

import pandas as pd
import numpy as np
import pickle
import scenarios_generation
import copy


#######################################################
# storage
#######################################################

def storage(scenarios, file) :
    with open(file,'wb') as file1:
        pickle.dump(scenarios,file1)
        
def dataload (file) :
    with open(file,'rb') as file1:
        scenarios = pickle.load(file1)
    return(scenarios)

#######################################################
# print and read
#######################################################    

def printcombi(combi):
    dec = {}
    for act in combi :
        l = []
        for decision in combi.get(act):
            l.append(decision.maniere)
        dec.update({act:l})
    return(dec)
    
def scenariotoread(scenario, state_dict):
    affichage = "Scenario :" + "\n"
    for node in scenario :
        dec = {}
        if type(node.mean)!= list :
            for act in node.mean :
                l = []
                for d in node.mean.get(act):
                    l.append(d.maniere)
                dec.update({act:l})
        else :    
            for act in node.mean[2] :
                l = []
                for decision in node.mean[2].get(act):
                    l.append(decision.maniere)
                dec.update({act:l})
                
        if dec != {} :
            affichage += "Decisions : " + str(dec) +"\n"
        
        if node != scenario[len(scenario)-1] :
            affichage += "State ("+str(node.data)+"): " + str(state_dict.get(node.data).etat_variables) + "\n"

    if scenario[len(scenario)-1].final == 'conflit logique' or scenario[len(scenario)-1].final == 'conflit moral' :
        affichage += "End of scenario : " + scenario[len(scenario)-1].final + str(scenario[len(scenario)-1].mean[1])
    else :
        if type(scenario[len(scenario)-1].final) == bool :
            affichage += "At least one goal reached"
        else :
            affichage += "End of scenario : " + scenario[len(scenario)-1].final
    return(affichage)

def dictio_decision_excel(dict_decision):
    dict_decision1 = {}
    for i in dict_decision :
        dict_decision1.update({dict_decision.get(i):i.maniere})
    dict_decisionex = pd.DataFrame(dict_decision1, index = ['Maniere'])
    dict_decisionex.to_excel('Dictio_decision.xlsx')
    return(dict_decision1)

def allscenariostoread (scenarios):
    """
    Parameters
    ----------
    scenarios : liste
        liste des listes des scénarios présentés sous
        forme de succession des numéros des états.

    Returns
    -------
    la feuille xlsx Resultat complétée avec les scénarios lisibles

    """
    dicttotal = {}
    indice = 0
    for scenario1 in scenarios :
        dict1 = {}
        indice2 = 0
        for i in scenario1 :
            dict1.update({indice2:[i.data,i.mean,i.final]})
            indice2 = indice2+1
        dicttotal.update({indice:dict1})
        indice = indice + 1
    dict_res = pd.DataFrame(dicttotal)
    a = dict_res.transpose()
    a.to_csv('Resultat.csv')
    
def allscenariostoreadbetter(file, scenarios,state_dict):
    with open(file,'w') as f: 
        index = 0
        for k in scenarios :
            x = scenariotoread(k,state_dict)
            f.write(str(index)+str(x)+'\n')
            index +=1



def removeduplicate(scenarios):
    for i, scenario in enumerate(scenarios) :
        for j in range(len(scenarios)-1, i, -1):
            if scenario==scenarios[j]:
                scenarios.pop(j)
    return(scenarios)



#######################################################
# decisions number
#######################################################

def nbdecision(systeme,scenario,principe, data_positions, data_opinions):
    """
    Function returning the number of decisions made by an agent favorable or unfavorable to a principle in a scenario, not considering (1,-) and (-1,-) situations
    """
    nb_defavorable = 0
    nb_favorable = 0
    utilisateur = utilisateurqui(systeme).name
    for k in range(1,len(scenario)) :
        noeud = scenario[k]
       
        if type(noeud.mean) != list :
            for decision in noeud.mean.get(utilisateur) :               
                if decision.transgresseppe != []:                    
                    for i in decision.transgresseppe :                        
                        if i == principe :
                            nb_defavorable +=1 
                if type(decision) == scenarios_generation.DecisionAction :
                    if data_positions.loc[utilisateur][principe]=='+' and data_opinions.loc[decision.variable,decision.valeur_arrivee][utilisateur,principe] == 1:
                        nb_favorable += 1
                else :
                    if data_positions.loc[utilisateur][principe]=='+' and data_opinions.loc[decision.variable,systeme.v.get(decision.variable).valeur_actuelle][utilisateur,principe] == 1:
                        nb_favorable += 1
        else :
            for listdecision in list(noeud.mean[2].values()):
                for decision in listdecision :
                    if decision.transgresseppe != []:
                    
                        for i in decision.transgresseppe :
                        
                            if i == principe :
                                nb_defavorable +=1 
                    if type(decision) == scenarios_generation.DecisionAction :
                        if data_positions.loc[utilisateur][principe]=='+' and data_opinions.loc[decision.variable,decision.valeur_arrivee][utilisateur,principe] == 1:
                            nb_favorable += 1
                    else :
                        if data_positions.loc[utilisateur][principe]=='+' and data_opinions.loc[decision.variable,systeme.v.get(decision.variable).valeur_actuelle][utilisateur,principe] == 1:
                            nb_favorable += 1
                
    return([nb_favorable,nb_defavorable])

def nbdecisionnuance(system,scenario, dict_etat, principe, data_positions, data_opinions):
    """
    Function returning the number of decisions made by an agent favorable or unfavorable to a principle in a scenario, considering also (1,-) and (-1,-)

    Parameters
    ----------
    principe : (str) principle used to judge the decisions

    Returns : a list [nb_favorable,nb_unfavorable]
    """
    nb_defavorable = 0
    nb_favorable = 0
    utilisateur = utilisateurqui(system).name
    for k in range(1,(len(scenario))) :
        noeud = scenario[k]
        str(noeud)
       
        if type(noeud.mean) != list : # no conflict
            for decision in noeud.mean.get(utilisateur) :
                if type(decision) == scenarios_generation.DecisionAction :
                    if data_positions.loc[utilisateur][principe]=='-' and data_opinions.loc[decision.variable,decision.valeur_arrivee][utilisateur,principe] == 1:
                        nb_defavorable +=1
                    if data_positions.loc[utilisateur][principe]=='+' and data_opinions.loc[decision.variable,decision.valeur_arrivee][utilisateur,principe] == -1:
                        nb_defavorable +=1
                    if data_positions.loc[utilisateur][principe]=='+' and data_opinions.loc[decision.variable,decision.valeur_arrivee][utilisateur,principe] == 1:
                        nb_favorable += 1
                    if data_positions.loc[utilisateur][principe]=='-' and data_opinions.loc[decision.variable,decision.valeur_arrivee][utilisateur,principe] == -1:
                        nb_favorable += 1
                else : #do nothing situation
                    valeur = dict_etat.get(noeud.data).etat_variables.get(decision.variable)
                    if data_positions.loc[utilisateur][principe]=='-' and data_opinions.loc[decision.variable,valeur][utilisateur,principe] == 1:
                        nb_defavorable += 1
                    if data_positions.loc[utilisateur][principe]=='+' and data_opinions.loc[decision.variable,valeur][utilisateur,principe] == -1:
                        nb_defavorable +=1
                    if data_positions.loc[utilisateur][principe]=='+' and data_opinions.loc[decision.variable,valeur][utilisateur,principe] == 1:
                        nb_favorable += 1
                    if data_positions.loc[utilisateur][principe]=='-' and data_opinions.loc[decision.variable,valeur][utilisateur,principe] == -1:
                        nb_favorable += 1
        else :    
            for decision in noeud.mean[2].get(utilisateur) :

                if type(decision) == scenarios_generation.DecisionAction :
                    if data_positions.loc[utilisateur][principe]=='-' and data_opinions.loc[decision.variable,decision.valeur_arrivee][utilisateur,principe] == 1:
                        nb_defavorable +=1
                    if data_positions.loc[utilisateur][principe]=='+' and data_opinions.loc[decision.variable,decision.valeur_arrivee][utilisateur,principe] == -1:
                        nb_defavorable +=1
                    if data_positions.loc[utilisateur][principe]=='+' and data_opinions.loc[decision.variable,decision.valeur_arrivee][utilisateur,principe] == 1:
                        nb_favorable += 1
                    if data_positions.loc[utilisateur][principe]=='-' and data_opinions.loc[decision.variable,decision.valeur_arrivee][utilisateur,principe] == -1:
                        nb_favorable += 1
                else :
                    
                    valeur = dict_etat.get(noeud.data).etat_variables.get(decision.variable)
                    if data_positions.loc[utilisateur][principe]=='-' and data_opinions.loc[decision.variable,valeur][utilisateur,principe] == 1:
                        nb_defavorable += 1
                    if data_positions.loc[utilisateur][principe]=='+' and data_opinions.loc[decision.variable,valeur][utilisateur,principe] == -1:
                        nb_defavorable +=1
                    if data_positions.loc[utilisateur][principe]=='+' and data_opinions.loc[decision.variable,valeur][utilisateur,principe] == 1:
                        nb_favorable += 1
                    if data_positions.loc[utilisateur][principe]=='-' and data_opinions.loc[decision.variable,valeur][utilisateur,principe] == -1:
                        nb_favorable += 1
                       
    return([nb_favorable,nb_defavorable])

def nbdecisionnuance_allact(system,scenario, dict_etat, principe, data_positions, data_opinions):
    """
    Function returning the number of decisions made by an agent favorable or unfavorable to a principle in a scenario, considering also (1,-) and (-1,-)

    Parameters
    ----------
    principe : (str) principle used to judge the decisions

    Returns : a list [nb_favorable,nb_unfavorable]
    """
    nb_defavorable = 0
    nb_favorable = 0
    utilisateur = utilisateurqui(system).name
    act = list(system.a.keys())
    for k in range(1,(len(scenario))) :
        noeud = scenario[k]
        str(noeud)
       
        if type(noeud.mean) != list : # no conflict
            for actors in act : 
                for decision in noeud.mean.get(actors) :
                    if type(decision) == scenarios_generation.DecisionAction :
                        if data_positions.loc[utilisateur][principe]=='-' and data_opinions.loc[decision.variable,decision.valeur_arrivee][utilisateur,principe] == 1:
                            nb_defavorable +=1
                        if data_positions.loc[utilisateur][principe]=='+' and data_opinions.loc[decision.variable,decision.valeur_arrivee][utilisateur,principe] == -1:
                            nb_defavorable +=1
                        if data_positions.loc[utilisateur][principe]=='+' and data_opinions.loc[decision.variable,decision.valeur_arrivee][utilisateur,principe] == 1:
                            nb_favorable += 1
                        if data_positions.loc[utilisateur][principe]=='-' and data_opinions.loc[decision.variable,decision.valeur_arrivee][utilisateur,principe] == -1:
                            nb_favorable += 1
                    else : #do nothing situation
                        valeur = dict_etat.get(noeud.data).etat_variables.get(decision.variable)
                        if data_positions.loc[utilisateur][principe]=='-' and data_opinions.loc[decision.variable,valeur][utilisateur,principe] == 1:
                            nb_defavorable += 1
                        if data_positions.loc[utilisateur][principe]=='+' and data_opinions.loc[decision.variable,valeur][utilisateur,principe] == -1:
                            nb_defavorable +=1
                        if data_positions.loc[utilisateur][principe]=='+' and data_opinions.loc[decision.variable,valeur][utilisateur,principe] == 1:
                            nb_favorable += 1
                        if data_positions.loc[utilisateur][principe]=='-' and data_opinions.loc[decision.variable,valeur][utilisateur,principe] == -1:
                            nb_favorable += 1
        else :    
            for actors in act :
                for decision in noeud.mean[2].get(actors) :

                    if type(decision) == scenarios_generation.DecisionAction :
                        if data_positions.loc[utilisateur][principe]=='-' and data_opinions.loc[decision.variable,decision.valeur_arrivee][utilisateur,principe] == 1:
                            nb_defavorable +=1
                        if data_positions.loc[utilisateur][principe]=='+' and data_opinions.loc[decision.variable,decision.valeur_arrivee][utilisateur,principe] == -1:
                            nb_defavorable +=1
                        if data_positions.loc[utilisateur][principe]=='+' and data_opinions.loc[decision.variable,decision.valeur_arrivee][utilisateur,principe] == 1:
                            nb_favorable += 1
                        if data_positions.loc[utilisateur][principe]=='-' and data_opinions.loc[decision.variable,decision.valeur_arrivee][utilisateur,principe] == -1:
                            nb_favorable += 1
                    else :
                        
                        valeur = dict_etat.get(noeud.data).etat_variables.get(decision.variable)
                        if data_positions.loc[utilisateur][principe]=='-' and data_opinions.loc[decision.variable,valeur][utilisateur,principe] == 1:
                            nb_defavorable += 1
                        if data_positions.loc[utilisateur][principe]=='+' and data_opinions.loc[decision.variable,valeur][utilisateur,principe] == -1:
                            nb_defavorable +=1
                        if data_positions.loc[utilisateur][principe]=='+' and data_opinions.loc[decision.variable,valeur][utilisateur,principe] == 1:
                            nb_favorable += 1
                        if data_positions.loc[utilisateur][principe]=='-' and data_opinions.loc[decision.variable,valeur][utilisateur,principe] == -1:
                            nb_favorable += 1
                       
    return([nb_favorable,nb_defavorable])

def nbdecisiontotalact(scenario, system, agent):
    """
    function counting the total number of decisions made by an agent
    
    Parameter
    -----------
    scenario : liste de noeuds
    systeme : objet systeme
    acteur : str de l'acteur qu'on souhaite étudier
    """
    nbvariable = 0
    for i in system.a.get(agent).va :
        nbvariable +=1
    nbdecisiontotal = (len(scenario)-1)*nbvariable
    return(nbdecisiontotal)
    
#######################################################
# other functions
#######################################################

def utilisateurqui(system):
    """Return the user of the system"""
    for agent in system.a :
        if type(system.a.get(agent)) == scenarios_generation.ActeurInterieur:
            if system.a.get(agent).utilisateur == True :
                return(system.a.get(agent))

def valeursNonAtteintes(dict_etat,system):
    """return values not reached in the scenarios"""
    valeursnonatteintes = {}
    l_etat = list(dict_etat.values()) #states list
    l_var = list(system.v.keys()) #variables list
    
    for var in l_var :
        kbar = []
        k = []
        for i in l_etat :
            val = i.etat_variables.get(var)
            if val not in k :
                k.append(val)
        
        for j in system.v.get(var).valeurs :
            if j not in k :
                kbar.append(j)
        valeursnonatteintes.update({var:kbar})

    return(valeursnonatteintes)

def scenarioobjatteint(scenarios, end):
    """
    Return all the scenarios ending by a specific ending 

    Parameters
    ----------
    scenarios : list returned by scenarios_generation.py
    end : str of the ending selected
    """
    scenarios_voulus = []
    for i in scenarios:
        noeud_final = i[len(i)-1]
        if noeud_final.final == end:
            scenarios_voulus.append(i)
    return(scenarios_voulus)

def listedecisionscenario1(scenarios):
    """
    Return a list of lists, every one of these is a scenario and is composed of the decisions and end of the scenario
    """    
    listefinale = []
    #etatNumber = np.max(list(dict_etat.keys()))
    #itemNumber = etatNumber + 1
    #for k in D.values():
       # dict_decision[itemNumber]=k
        #itemNumber += 1

   # conflitNumber = itemNumber
   # boucleNumber = itemNumber +1
   # objNumber = itemNumber +2
    #key_list = list(dict_decision.keys())
    #val_list = list(dict_decision.values())

    for i in scenarios :
            unscenario = []
            for noeud in i :               
                if noeud.mean != {}: #initial node
                    if type(noeud.mean)==list: #logical conflict
                        for listdecision in list(noeud.mean[2].values()):
                            for decision in listdecision :    
                                #position = val_list.index(decision)
                                #decisionNumber = key_list[position]                         
                                unscenario.append(decision.maniere)                        
                    else :                    
                        l = list(noeud.mean.keys()) #list of agents
                        for acteur in l :
                            for decision in noeud.mean.get(acteur) :
                                #position = val_list.index(decision)
                                #decisionNumber = key_list[position]
                                unscenario.append(decision.maniere)
                    if noeud.final == "conflit logique" :
                            unscenario.append(["conflit logique"])
                    if noeud.final == "boucle" :
                            unscenario.append(["boucle"])
                    if noeud.final == "objectif(s) atteint(s)" :
                            unscenario.append(["objectif(s) atteint(s)"])
            listefinale.append(unscenario)
    return(listefinale)


def listedecisionscenario2(scenarios, dict_etat, dict_decision,D):
    """
    Return a list of lists, every one of these is a scenario and is composed of the numbers matching decisions and a number matching an end of the scenario
    """    
    listefinale = []
    etatNumber = np.max(list(dict_etat.keys()))
    itemNumber = etatNumber + 1
    for k in D.values():
        dict_decision[itemNumber]=k
        itemNumber += 1

    conflitNumber = itemNumber
    boucleNumber = itemNumber +1
    objNumber = itemNumber +2
    key_list = list(dict_decision.keys())
    val_list = list(dict_decision.values())

    for i in scenarios :
            unscenario = []
            for noeud in i :               
                if noeud.mean != {}: #initial node
                    if type(noeud.mean)==list: #logical conflict
                        for listdecision in list(noeud.mean[2].values()):
                            for decision in listdecision :    
                                position = val_list.index(decision)
                                decisionNumber = key_list[position]                         
                                unscenario.append(decisionNumber)                        
                    else :                    
                        l = list(noeud.mean.keys()) #list of agents
                        for acteur in l :
                            for decision in noeud.mean.get(acteur) :
                                position = val_list.index(decision)
                                decisionNumber = key_list[position]
                                unscenario.append(decisionNumber)
                    if noeud.final == "conflit logique" :
                            unscenario.append(conflitNumber)
                    if noeud.final == "boucle" :
                            unscenario.append(boucleNumber)
                    if noeud.final == "objectif(s) atteint(s)" :
                            unscenario.append(objNumber)
            listefinale.append(unscenario)
    return(listefinale)
        

def contains(small, big):
    """
    True if the elements of a small list are included whatever the order in the big list
    """
    return all(elem in big for elem in small)

def decisions_in_scenario(decision, scenario):
    """
    True if a list of set of decisions is included in a scenario in the right order
    Ex : [["a","b"], ["c"]] in [["e"],["b","a","g"],["f"], ["c"]]==True
    """
    cutlist = scenario
    index=0
    for k in range (len(decision)):
        print(k)
        for j in range(len(cutlist)) :
            print(j)
            if contains(decision[k],cutlist[j])==True:
                index+=1
                cutlist = cutlist[j+1:len(cutlist)]
                print(cutlist)
                break
    if index == len(decision):           
        return (True)
    else :
        return(False)
    
def ReachedValuesScenario(scenario,state_dict):
    """return values reached in a scenarios
    first return is for the value with no order {var1:[val1,val2], var2:[val1]...}
    second return is keeping the dict of values in the same order as the states of the system
    [{var1:val1, var2:val1},{var1:val1,var2:val2}...]
    """
    reachedvalues = {}
    reachedvaluesinorder = []
    
    for node in scenario :    
        if node.children != [] :
            state_nb = node.data
            state_variables = state_dict.get(state_nb).etat_variables
            reachedvaluesinorder.append(state_variables)
            keylist = reachedvalues.keys()
            for var in state_variables :
                val = state_variables.get(var)
                if var in keylist :
                    currentvalues = reachedvalues.get(var)
                    if val not in currentvalues :
                        currentvalues.append(val)
                        reachedvalues[var]=currentvalues

                else :
                    reachedvalues.update({var:[state_variables.get(var)]})

        
        else : #to consider the last state of the scenario even if its a potential one because of a logical conflict
            if type(node.mean)==list :
                combidecision = node.mean[2]
            else :
                combidecision = node.mean
            previous_var = state_dict.get(almostlastnode.data).etat_variables
            etat_variables = copy.deepcopy(previous_var) #do almost the same thing as newsystemstate(previous_state,combidecision) but just for the variables
            for act in combidecision : 
                for k in combidecision.get(act):
                    for n in etat_variables :
                        if k.variable == n :
                            if type(k) != scenarios_generation.Decision :
                                etat_variables[n] = k.valeur_arrivee

            keylist = reachedvalues.keys()
            reachedvaluesinorder.append(etat_variables) #dealing with the new created state
            
            for var in etat_variables :
                val = etat_variables.get(var)
                if var in keylist :
                    currentvalues = reachedvalues.get(var)
                    if val not in currentvalues :
                        currentvalues.append(val)
                        reachedvalues[var] = currentvalues

                else :
                    reachedvalues.update({var:[etat_variables.get(var)]})
        almostlastnode = node
    return(reachedvalues, reachedvaluesinorder)

def value_in_scenarios(value,scenarios, state_dict):
    """
    the value is like {variable : [value1,value2]}
    no order is taken into consideration
    return the list of scenarios concerned
    """
    final_list = []

    for scenario in scenarios :
        val_dict = ReachedValuesScenario(scenario, state_dict)[0]
        for var in value :
            for val in value.get(var) :
                if val in val_dict.get(var) :
                    final_list.append(scenario)
    return(final_list)


def data_parallel_scenario(scenarios, state_dict, system):
    ids=[]
    var_dimension= []
    dct_states = {} #{state1:[val1,val2...],state2 :}
    max_length = 0
    scenarios_nb = len(scenarios)
    var_count = 0
 
    #maximum number of states (or steps) in the scenarios
    for i in scenarios :
        length = len(i)
        if length > max_length :
            max_length = length

    var_list = list(system.v.keys()) #list of the var names
    none_dict={}
    for var in var_list : #a dict to initialize every variable
        none_dict.update({var:None})
    
    for k in range(max_length) :
        for scenario in scenarios :
            if k<len(scenario):
                if scenario[k].children != [] :
                    state_variables = state_dict.get(scenario[k].data).etat_variables
                else : #case of the last node of the scenario 
                    if type(scenario[k])==list : #logical conflict
                        node=scenario[k]
                        combidecision = node.mean[2]
                        previous_var = state_dict.get(node.data).etat_variables
                        etat_variables = copy.deepcopy(previous_var) #do almost the same thing as newsystemstate(previous_state,combidecision) but just for the variables
                        for act in combidecision : 
                            for k in combidecision.get(act):
                                for n in etat_variables :
                                    if k.variable == n :
                                        if type(k) != scenarios_generation.Decision :
                                            etat_variables[n] = k.valeur_arrivee
                    else : #other ends
                        state_variables = state_dict.get(scenario[k].data).etat_variables
            else : 
                state_variables= none_dict 
            keys_states = list(dct_states.keys())
            state = 'state '+str(k)  #état
            if state not in keys_states :
                dct_states[state] = [state_variables]
            else :
                a=dct_states.get(state)
                a.append(state_variables)
                dct_states.update({state : a})
    
    for vstate in dct_states :
        newvalue=[]
        for var in var_list :
            for mini_dict in dct_states.get(vstate) :
                newvalue.append(mini_dict[var])
        dct_states.update({vstate:newvalue})

    #var list
    for var in var_list:
        var_dimension.extend([var for i in range (scenarios_nb)])
    var_nb = len(dct_states)
    #id list
    id_list=list(range(1,scenarios_nb+1))
    ids = np.tile(id_list,var_count)
    #print(ids)
    return(ids, var_dimension, dct_states)
    

