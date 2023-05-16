# -*- coding: utf-8 -*-
"""
Created on Tue Sep 28 10:21:25 2021

@author: cablanch
"""
import itertools
import copy
import pandas as pd
import numpy as np
import pickle
from math import *

########### System components #####################

class System : 
    """
    System studied

     Parameters
    ----------
     agents: dict agents objects of the system 
     principles: list principles of the system
     variables: dict variables objects of the system
    """
 
    def __init__(self, agents, principles, variables):
        self.a = agents        
        self.pp = principles     
        self.v = variables        
        
    def add_agent(self, objet):
        self.a.update({objet.name : objet})
        
    def add_variable(self, variable):
        self.v.update({variable.name : variable}) 
    
    def renvoyer_etats_variables(self):
        """ 
        Dict of specific variables in a precise state
        """
        etat_variables = {}
        for k in self.v :
            etat_variables.update(
                {self.v.get(k).name : self.v.get(k).valeur_actuelle})
        return etat_variables
        


class Acteur:
    """
    An agent of the system
    
    name: str of the agent's name
    variables_actions: list of the variables the agent can change
    decisions_unique_acteur: dict of the decisions object the agent can make

    """
    
    def __init__(self, name, actions_variables, single_agent_decision):
        
        self.name = name
        self.va = actions_variables
        self.decisions_unique_acteur = single_agent_decision
        

class ActeurInterieur(Acteur):
    """
    Agent inside the system that have opinions and positions

     Parameters
    ----------
    Acteur : str name
    utilisateur : boolean true if the agent is the user of the software
    position : list of the agent's position
    opinion : list of the agent's opinion
    """
    
    def __init__(self, name, utilisateur, variables_actions, 
                 decisions_unique_acteur, position, opinion):
        super().__init__(name, variables_actions, decisions_unique_acteur)
        self.p = position  
        self.o = opinion
        self.utilisateur = utilisateur
        
       
class Variable:
    """
    Variable of the system
    
     Parameters
    ----------
    valeurs_possibles: list of the values the variable can have
    valeur_actuelle: str of the value the variable currently has
    """
    
    def __init__(self, name, valeurs_possibles, valeur_actuelle):
        self.name = name
        self.valeurs = valeurs_possibles
        self.valeur_actuelle = valeur_actuelle
    
    def valeur_initiale(self, valeur_initiale_choisie):
        self.valeur_actuelle = valeur_initiale_choisie
        
           
class EtatSysteme:
    """
    EtatSysteme is the state of the system
    
    positions: dict set of the positions of the actors in this state
    opinions: dict set of the opinions of the actors in this state
    etat_variables: dict set of the instantiate variables in this state
    """
    def __init__(self, positions, opinions, etat_variables):

        self.ens_positions = positions
        self.ens_opinions = opinions
        self.etat_variables = etat_variables
     
    def update_etat_systeme(self, System):
        """
        return the object SystemState after modification of the variables
        """
        self.etat_variables = System.renvoyer_etats_variables()
        
    def __eq__(self,other):
        if(isinstance(other, EtatSysteme)):
            return self.ens_positions.equals(other.ens_positions) and self.ens_opinions.equals(other.ens_opinions) and self.etat_variables == other.etat_variables
        return(False)
    
       
########## Elements de scénario ################

class Decision:
    """
    Decisions considered in the system
    
    :param variable: variable object concerned by the decision
    :param valeur_depart: starting value of the variable (before the decision)
    :param valeur_arrivee: ending value of the variable (after the action related to the decision)
    :param maniere: (str) way to go from one value to another
    transgresseppe : (str) None if the principle is not compromised, otherwise, the name of the principle
    """
    def __init__(self, variable, maniere, transgresseppe):
        self.variable = variable      
        self.maniere = maniere
        self.transgresseppe = transgresseppe
        
    def __eq__(self,other):
        if(isinstance(other, Decision)):
            return self.variable == other.variable and self.maniere == other.maniere
        return(False) 
        

class DecisionAction(Decision):
    def __init__(self, variable, valeur_depart, valeur_arrivee, maniere, transgresseppe):
        super().__init__(variable, maniere, transgresseppe)
        self.valeur_arrivee = valeur_arrivee
        self.valeur_depart = valeur_depart
        
    def prendre_decision(self, System):
        if System.v.get(self.variable).valeur_actuelle == self.valeur_depart:
            System.v.get(self.variable).valeur_actuelle = self.valeur_arrivee

    def __eq__(self,other):
        if(isinstance(other, DecisionAction)):
            return self.variable == other.variable and self.valeur_depart == other.valeur_depart and self.valeur_arrivee == other.valeur_arrivee and self.maniere == other.maniere
        return(False)            


class Conflit :
    """
    nature : str moral or logical
    v_concernée : list of 1variable if moral conflict, list of variables/values if logical conflict
    d_concernees: list of the decisions concerned by the conflict
    a_concernées : list of 1 agent if moral conflict, more than one otherwise
    """
    def __init__(self, nature, v_concernees, d_concernees, a_concernees):
        self.nature = nature      
        self.v_concernees = v_concernees
        self.d_concernees = d_concernees
        self.a_concernees = a_concernees

#-----------Fonctions éléments du système-----------#

def D_formation(data_decision):
    """
    Creation of decision object and dict of these decisions
    """
    D = {} #set of decision objects
    k = 0
    for i in data_decision["decision"] :
        variable = data_decision["variable"][k]
        if pd.isnull(data_decision["val depart"][k]) == False:
            maniere = i
            valeur_depart = data_decision["val depart"][k]
            valeur_arrivee = data_decision["val arrivee"][k]
            d1 = DecisionAction(variable, valeur_depart, valeur_arrivee, maniere, [])
            D.update({d1.maniere : d1})
        else:
            maniere = i
            d1 = Decision(variable, maniere, [])
            D.update({d1.maniere : d1})
        k = k+1
    return(D)

def decisions_acteurs_objets(D,data_decision):
    """
    Creation of the dict ens_decisions_acteurs_objets (association between agents and the decisions they can make)
    """
    ens_decisions_acteurs_objets = {} 
    n = 0
    l = len(data_decision.columns)
    for i in data_decision.iloc[:,4:l+1] : #i: agent's name
        d1 = {}
        for k in data_decision[i]: # k = ok if the agent can make the decision
            if pd.isnull(k) == False:
                d1.update({D.get(data_decision["decision"][n]).maniere:
                        D.get(data_decision["decision"][n])})
            n = n+1
        ens_decisions_acteurs_objets.update({i:d1})
        n=0
    return(ens_decisions_acteurs_objets)

def variables_formation(data_opinions, my_system):
    """
    Creation of variable object of the system
    """
    n = 0
    valeurs = []
    k = data_opinions.index.get_level_values("Variable")[0]
    valeur_actuelle = "pas de valeur actuelle"
    for i in data_opinions.index.get_level_values("Variable"): #going through the index of variables
        if i == k :
            valeurs.append(data_opinions.index.get_level_values("Valeur")[n])
        else :
            v1 = Variable(k, valeurs, valeur_actuelle)
            my_system.add_variable(v1)
            valeurs = []
            valeurs.append(data_opinions.index.get_level_values("Valeur")[n])
        k = i
        n=n+1
    v1 = Variable(k, valeurs, valeur_actuelle)
    my_system.add_variable(v1)
    return(my_system)

def acteurs_formation(data_utilisateur,ens_decisions_acteurs_objets,my_system, data_decision, data_positions, data_opinions):
    """
    Creation of the agent objects of the system
    """
    for i in data_utilisateur.index : 
        n = 0
        variables_actions = []
        
        if data_utilisateur['Exterieur'].loc[i] == False :
            position = data_positions.loc[i]
            opinion = data_opinions[i]
            decisions_unique_acteur = ens_decisions_acteurs_objets[i]
            utilisateur = data_utilisateur['Utilisateur'].loc[i]

            for k in data_decision[i]:

                if pd.isnull(k) == False and data_decision["variable"][n] not in variables_actions :
                    
                    variables_actions.append( data_decision["variable"][n])
                n = n+1
            a1 = ActeurInterieur(i, utilisateur, variables_actions, 
                                        decisions_unique_acteur, position, opinion)
            my_system.add_agent(a1)
            
        
        else :
            decisions_unique_acteur = ens_decisions_acteurs_objets[i]
            
            for k in data_decision[i]:
                if pd.isnull(k) == False and data_decision["variable"][n] not in variables_actions :
                    variables_actions.append( data_decision["variable"][n])
                n = n+1
            a1 = Acteur(i, variables_actions, decisions_unique_acteur)
            my_system.add_agent(a1)
    return(my_system)

def pp_formations(my_system,data_positions):
    """
    Fill the list of the moral principles of the system
    """
    ppe = []
    for k in data_positions.columns:
        ppe.append(k)
    my_system.pp = ppe
    return(my_system)

#-----------Fonctions décisions-------------#

def decisions_possibles(Agent, Variable, SystemState):
    """   
        Parameters
    ----------
    Agent : Agent object concerned by the decisions search
    Variable : Variable object concerned by the decisions search
    SystemState : EtatSysteme object concerned by the decisions search
        
       Returns
    -------
   possible_decisions : dict of the possible decision for an agent about a variable in a given system state     
    """
    possible_decisions = {}
    etat_v1 = SystemState.etat_variables.get(Variable.name)
   
    d_init = Agent.decisions_unique_acteur
    
    for i in d_init:
        if type (d_init[i]) != Decision:
            
            if d_init[i].valeur_depart == etat_v1 and d_init[i].variable == Variable.name:
                possible_decisions.update({i : d_init[i]})
        else:
            if d_init[i].variable == Variable.name :
                possible_decisions.update({i : d_init[i]})
    return possible_decisions

  

def decisions_coherentes(Agent, Variable, possible_decisions, D, opinions, positions, against_ppe):
    """
    the decisions_coherentes are the consistent decisions that are not going against the principles of the internal agents (except the user)
    
    Parameters
    ----------
    Agent : Agent
    Variable : Variable
    décisions_possibles : dict
    opinions : dict
    positions : list

    Returns
    -------
    decisions_coherentes1 : dict or Conflit object
    """
    decisions_coherentes1 = {}
    pseudo_etat_arrivee = {}
    opinion_decision_possible = {}
    if type(Agent) != ActeurInterieur :
        decisions_coherentes1 = possible_decisions
        
    else :
        #pseudo etat arrivee : set of the instanciate variables after decisions, 
        #only on the variable that the agent can control (no system dynamic)
        decisions_coherentes1 = possible_decisions
        for i in possible_decisions:    
            if type (possible_decisions[i]) != Decision :
                pseudo_etat_arrivee.update({
                    possible_decisions[i].variable : 
                    possible_decisions[i].valeur_arrivee})
    
                opinion_decision_possible.update({
                                possible_decisions[i].maniere : 
                                opinions.loc[Variable.name,pseudo_etat_arrivee.get(possible_decisions[i].variable)]
                                            [Agent.name]})
        
            else: #decision to do nothing
                pseudo_etat_arrivee.update({possible_decisions[i].variable : 
                                                Variable.valeur_actuelle})    
                opinion_decision_possible.update({
                                possible_decisions[i].maniere : 
                                opinions.loc[Variable.name,pseudo_etat_arrivee.get(possible_decisions[i].variable)]
                                            [Agent.name]})
    
                #We have here the pseudo_etat_arrivee (potential next state) and the opinion on the decision to reach it
            # Now we remove the decisions that have bad consequences
    
        n = 0       
        for i in opinion_decision_possible :
            ppetransgresse = []
            for k in positions.columns :
                if (i in decisions_coherentes1 and opinion_decision_possible.get(i).iloc[n] == -1 and positions.loc[Agent.name][k] == '+') or (i in decisions_coherentes1 and opinion_decision_possible.get(i).iloc[n] == 1 and positions.loc[Agent.name][k] == '-') :                   
                    if Agent.utilisateur == True:
                        i_objet = D.get(i)
                        ppetransgresse.append(str(k))
                        i_objet.transgresseppe = ppetransgresse
                    else :
                        decisions_coherentes1.pop(str(i)) 
                n = n+1
            n = 0
    
            # We remove the decision that go against the principle by nature
        for i in opinion_decision_possible : 
            if contraireprincipe(Agent, i, positions, against_ppe) == True :
                if Agent.utilisateur == True:
                    i_objet = D.get(i)
                    i_objet.transgresseppe = against_ppe["principe"].iloc[n]                   
                else :
                    decisions_coherentes1.pop(str(i))
                    
        # moral conflict situation        
        if decisions_coherentes1 == {} :
            decisions_coherentes1 = Conflit("dilemme moral",
                                            [Variable.name],[],[Agent.name])
        
    return(decisions_coherentes1)
            
#The next function allows to iterate decisions_coherentes on all the variables the agent can control
#We will have all the set of possible decisions for a variable. We can then do the combinatorial process

def ens_decisions_coherentes(Agent, System, D,
                             SystemState, opinions, positions, against_ppe):
    """
    All the consistent decisions on all the variable the agent can control

    Returns
    -------
    consistent_decisions_set1 :dict of decisions objects that an agent can make on every variables it can control in a specific system state
        {variable : {dict consistent decision}, v2 : {d1, d2}}
    """
    consistent_decisions_set1 = {}
    for i in Agent.va:   
        decisions_possibles1 = decisions_possibles(Agent, System.v.get(i), SystemState)
        decisions_coherentes1 = decisions_coherentes(
                Agent, System.v.get(i), decisions_possibles1, D, opinions, positions, 
                against_ppe)
        if type(decisions_coherentes1) == Conflit :
            consistent_decisions_set1 = decisions_coherentes1
            return(consistent_decisions_set1)    
        else :
            consistent_decisions_set1.update({i:decisions_coherentes1})
    return(consistent_decisions_set1)

def combinaison_decisions_coherentes(consistent_decisions_set1):
    """
    Generation of the possible combinations (the different set of possible decisions an agent can make in a state)
    
    Parameters
    ----------   
    consistent_decisions_set1 : dict return by function ens_decisions_coherentes

    Returns
    -------
    combinaison_unique_acteur: list of all the dict composed of the possible consistent decision combinations for an agent [{combi 1}, {combi 2}]
    """
    liste=[]
    consistent_decisions_set2 ={}
    combinaison_unique_acteur={}
    
    if type(consistent_decisions_set1)== Conflit :     #Moral conflict
        combinaison_unique_acteur = consistent_decisions_set1
    else :
        for i in consistent_decisions_set1:
            for k in consistent_decisions_set1[i]:

                liste.append(consistent_decisions_set1[i][k])
            consistent_decisions_set2.update({i:liste})
            liste = []
        keys, values = zip(*consistent_decisions_set2.items())
        combinaison_unique_acteur = [dict(zip(keys,v)) for v in itertools.product(*values)]
      
    return combinaison_unique_acteur


def combi_decisions_coherentes_acteurs(System, D, EtatSysteme, opinions, positions, against_ppe):
   
    """
    All the possible combination of the decision combinations that all the agents can make
        
    Returns
    -------
    combi_decisions_coherentes_acteurs1 : list of the dict including the combinations of consistent decisions for each agents 
        [{agent1:[combi1], ag2:[combi1]}, {ag1:[combi 2], ag2:[combi1]}]

    """
    
    liste = [] #list of the set of consistent possible decisions for one agent
    liste_decisions_coherentes = [] #list od the list of the set of consistent decisions
    ens_decisions_coherentes_acteurs = {} #dict of lists of consistent decisions, keys are the agents
    combi_decisions_coherentes_acteurs1 = {}
    for i in System.a:
        ens_decision_coherente_unique_acteur = ens_decisions_coherentes(
                System.a.get(i), System, D, EtatSysteme, 
                opinions, positions, against_ppe)
        combinaison_unique_acteur = combinaison_decisions_coherentes(
            ens_decision_coherente_unique_acteur)
        
        if type(combinaison_unique_acteur) == Conflit : 
            combi_decisions_coherentes_acteurs1 = combinaison_unique_acteur
            return combi_decisions_coherentes_acteurs1
            
        else :
            for k in combinaison_unique_acteur:
                for m in k:
                    liste.append(k[m])
                liste_decisions_coherentes.append(liste)
                liste = []
            ens_decisions_coherentes_acteurs.update({i:liste_decisions_coherentes})
            liste_decisions_coherentes = []
    keys, values = zip(*ens_decisions_coherentes_acteurs.items())   
    liste_utile = [keys, values]
    
    return(liste_utile)            
   
def liste_decision_combi (combi):
    """
  list of the decision objects that are included in a combination
    """
    decisions = []
    for i in combi: 
        for k in combi[i]:
            decisions.append(k)
    return(decisions)
    
def dict_dec_var(decisions,system,combi):
    """
    make a dict variable/ending value thanks to a list of decisions
    check is a variable has 2 different values given the decision list
    
    return :  [dict,conflict]
    conflit = [] or Conflict object
    """
    dictvar = {} #dict of the variables/values that are csq of the decisions
    conflit = []
    for d in decisions :
                varname = system.v.get(d.variable).name #name of the variable concerned by the decision
                
                if type(d) == DecisionAction :
                    csqvar = d.valeur_arrivee
                else :
                    csqvar = system.v.get(d.variable).valeur_actuelle                  
                if varname in dictvar : #when a variable is instantiate by two or more different values
                    if csqvar != dictvar.get(varname):
                        conflit.append(Conflit("logique",[varname],combi,[]))
                else :
                    dictvar.update({varname:csqvar})
            
    return(dictvar,conflit)

def agregation(all_combinations, system, log_conf):

    """
    Paramètres
        -------
    all_combination : list of dict of all possible consistent decisions combinations between agents

    Returns
        -------
    state1 : list with logical conflict when there is one in the combination and otherwise, the combination
            The combination represent the possible states after the previous one
    """
    state1 = []
    conflitsnum = log_conf['conflit'].value_counts() #table associating a number of logical conflict to the number of variables concerned by the conflict
    if type(all_combinations) == Conflit : #Moral conflict in the combination
        state1.append(all_combinations)
    else :
        keys = all_combinations[0]
        values = all_combinations[1]
        
        for v in itertools.product(*values):
            combi = dict(zip(keys,v))            
            state1.append(combianalyse(combi,log_conf,system,conflitsnum))
    
    return(state1)
                    
def combianalyse (combi,logconf,system, conflicts_num):
    dictvar = {} #dict of the variable/values that are the csq of the decisions
             #make the list of all the decision objects
    decisions = liste_decision_combi(combi)
            #dict of the variable with their ending values (next state)
    dictvar = dict_dec_var(decisions,system,combi)[0]
    conflit = dict_dec_var(decisions,system,combi)[1]
            # conflict when dictvar is made, 2 agents want different values for the same variable
    if conflit != [] : 
        etatcombi = conflit[0] 
        return(etatcombi) 
                        
    for idconf in conflicts_num.index: #idconf = number of the conflict               
        isconflog = []
        confvalide = False                 
                #table with he studied conflict only
        for i in logconf[logconf['conflit']==idconf].index :
                                
            var = logconf[logconf['conflit']==idconf]['var'][i] #var concerned by the conflict
            val = logconf[logconf['conflit']==idconf]['val'][i] #val concerned by the conflict
                    
                #if the value of the variable is the same in dictvar than in the conflict table
            if val == dictvar.get(var):    
                confvalide=True
            else :
                confvalide=False
                break #at list on of the values doesn't work so no conflict
                        
        if confvalide == True:
            varsconf = []
            for i in logconf[logconf['conflit']==idconf]['var'] :
                varsconf.append(i) 
            confactuel = Conflit("logique",varsconf,combi,[]) #completed by the decisions causing the conflict 
            isconflog.append(1)
            break # remove the break if we want to consider all the conflict of a situation, here only the first conflict found is considered
    if 1 in isconflog :           
        etatcombi = confactuel                                                           
    else :
        etatcombi = combi
    return(etatcombi)                        

def contraireprincipe(agent,decision,position,against_ppe):
    """
        Parameters
    ----------
    agent : agent object
    decision : (str) name of the decision (ObjetDécision.maniere)
    position : Dataframe positions of the agents on the moral principles of the system
    against_ppe : Dataframe of the law of the domain about the decisions against the moral principles 

    Returns
    -------
    contraireppepresent : Bool
        contrairepppresent == True if the decision is against the principles for the agent   
    """
    contraireppepresent = False
    n = 0
    for k in against_ppe["acteur"] :
        if k == agent.name :
            if against_ppe["decision"].iloc[n] == decision:
                principe = against_ppe["principe"].iloc[n]
                if position.loc[agent.name][principe] == "-" :
                    contraireppepresent = True
        n = n+1
    return(contraireppepresent)


def newsystemstate(previous_state,combidecision):
    """
    Generation of the new system state by updating the previous one with the combination of decisions made by the agents
     
        Parameters
    ----------
    previous_state : dict previous variables state
    combidecision : dict combination of the decisions after the previous state

    Returns
    -------
    new_state : dict the new values of the variables
    """

    positions = previous_state.ens_positions 
    opinions = previous_state.ens_opinions   
    etat_variables = copy.deepcopy(previous_state.etat_variables) 
    for act in combidecision : 
        for k in combidecision.get(act):
            for n in etat_variables :
                if k.variable == n :
                    if type(k) != Decision :
                        etat_variables[n] = k.valeur_arrivee

    new_state = EtatSysteme(positions, opinions, etat_variables)
    return(new_state)

def accordetatsystemevaleurvariable(systemstate,system):
    """
    the actual values of the system variables need to take the values required by the systemstate
    """
    system2 = copy.deepcopy(system)
    for i in systemstate.etat_variables : 
        system2.v.get(i).valeur_actuelle = systemstate.etat_variables.get(i)
    return(system2)

class Node: 
    """
        Parameters
    ----------
    final : Bool True if the node is a the end of the scenario
    data : System state object (present as a number matching the table of systemstate)
    children : list of the following nodes
    mean = dict of decisions allowing to go in this state
    """
    def __init__(self,final,data,children,mean,depth,next=None):
        self.final = final
        self.data = data
        self.children = children
        self.mean = mean
        self.next = next
        self.profondeur = depth
        
    def add_children(self, obj):
        self.children.append(obj)

    def del_children(self, obj):
        self.children.remove(obj)

    def __str__(self, level = 0):
        if self.next == None :
            ret = "\t"*level+repr(self.data)+repr(self.final)+"\n"
        else :
            ret = "\t"*level+repr(self.data)+"\n"
        for child in self.children:
            ret += child.__str__(level+1)
        return ret

    def __eq__(self,other):
        if(isinstance(other, Node)):
            return self.data==other.data and self.mean == other.mean
        return(False)


def fill_dictetat(next_state, state_dict, depth, i):
    #fill dict_etat table with all the states included in the scenarios
    if next_state in state_dict.values():                       
        #find the key matching the state
        key_list = list(state_dict.keys())
        val_list = list(state_dict.values())
        position = val_list.index(next_state)
        indice = key_list[position]        
        #create the node with the key
        nodefils = Node(False, indice,[],i,depth, None)
                        
    else :
        key_list = list(state_dict.keys())
        indice_max=int(np.max(key_list))
        indice = indice_max +1
        state_dict.update({indice:next_state})
        nodefils = Node(False,indice,[],i,depth, None)
    return(nodefils)

def condition_generation(cutcriteria, nbscenarios, node1, writer):
    max = np.max(nbscenarios)                    
    if type(cutcriteria) == int :    
        if max == cutcriteria :                           
            return(True) 
        nbscenarios.append(max+1)
        pickle.dump(node1[0],writer)
    elif type(cutcriteria) == list and cutcriteria != []:                        
        if max%cutcriteria[0]==0:
            pickle.dump(node1[0],writer)
        nbscenarios.append(max+1)
    else : 
        nbscenarios.append(max+1)
        pickle.dump(node1[0],writer)
    return(nbscenarios)

def treegeneration3(writer,cutcriteria, nbscenarios, indice,dict_etat,root,node,system,opinions, positions, against_ppe,D,contraintelogique, MAX_PROF, data_objetrupture) :
    """
    This function store the different scenarios generated in the csv file
    """
    previous_state = dict_etat.get(node.data)  
    combi = combi_decisions_coherentes_acteurs(system, D,
                                                   previous_state,
                                                   opinions, 
                                                   positions, 
                                                   against_ppe)

    conflitsnum = contraintelogique['conflit'].value_counts()
    
    if type(combi) == Conflit : #When the combination has a moral conflict inside  
        i = combi
        prof = node.profondeur+1
        next_node = Node("conflit moral",node.data,[],[i.nature, i.v_concernees, i.d_concernees, i.a_concernees],prof,None)
        node.next = next_node
        node.add_children(next_node)
        max = np.max(nbscenarios)
        nbscenarios.append(max+1)
        node1 = getallscenarios(root)
        pickle.dump(node1[0],writer)
    else :
        keys1 = combi[0]
        values1 = combi[1]       
        for v in itertools.product(*values1):
            combinaison = dict(zip(keys1,v))
            i = combianalyse(combinaison,contraintelogique,system,conflitsnum)

            if type(i) == Conflit :
                if i.nature == "logique" :
                    prof = node.profondeur+1               
                    next_node = Node("conflit logique",node.data,[],[i.nature, i.v_concernees, i.d_concernees, i.a_concernees],prof,None)
                    node.next = next_node
                    node.add_children(next_node)
                    node1 = getallscenarios(root)
                    a = condition_generation(cutcriteria, nbscenarios, node1, writer)
                    if a == True :
                        break
                    else : 
                        nbscenarios = a
                                
            else :
                # create a new state with the decisions made
                next_state = newsystemstate(previous_state,i)
                # match the actual values of the variables of the system with this next_state
                new_system = accordetatsystemevaleurvariable(next_state,system)
                prof = node.profondeur+1                
                next_node = fill_dictetat(next_state, dict_etat, prof,i)
                node.next = next_node
                
                if next_node == node :
                    next_node.final = "boucle"
                    node.add_children(next_node)
                    node1 = getallscenarios(root)
                    a = condition_generation(cutcriteria, nbscenarios, node1, writer)
                    if a == True :
                        break
                    else : 
                        nbscenarios = a
                
                elif detectCycle(root):
                    next_node.final = "boucle"
                    node.add_children(next_node)
                    node1 = getallscenarios(root)
                    a = condition_generation(cutcriteria, nbscenarios, node1, writer)
                    if a == True :
                        break
                    else : 
                        nbscenarios = a
            
                elif interetatteint2(next_node.data, dict_etat, data_objetrupture, "Objectif") :
                    next_node.final = "objectif(s) atteint(s)"
                    node.add_children(next_node)
                    node1 = getallscenarios(root)
                    a = condition_generation(cutcriteria, nbscenarios, node1, writer)
                    if a == True :
                        break
                    else : 
                        nbscenarios = a
                    
                elif prof == MAX_PROF:
                    next_node.final = "branche trop longue"
                    node.add_children(next_node)
                    node1 = getallscenarios(root)
                    a = condition_generation(cutcriteria, nbscenarios, node1, writer)
                    if a == True :
                        break
                    else : 
                        nbscenarios = a
 
                else :
                    node.add_children(next_node)
                    treegeneration3(writer,cutcriteria, nbscenarios, indice,dict_etat,root,next_node, new_system, opinions, positions, against_ppe, D, contraintelogique, MAX_PROF, data_objetrupture)      
            node.del_children(next_node)
    return(dict_etat)


def detectCycle(head):
    slow = fast = head 
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            return True
    return False



def interetatteint2(datanode, dict_etat, data_objetrupture, goal):
    
    """
Check if the goal (or breakthrough) is reached in the state of this node
    """
    data = dict_etat.get(datanode).etat_variables
    index1 = 0
    d = {}
    for k in data_objetrupture[goal]:
        if pd.isnull(k)==False:
            variable = data_objetrupture["Variable"][index1]
            valeur = data_objetrupture["Valeur"][index1]
            d.update({variable : valeur})
        index1 += 1
    interet = False
    interet2 = 0
    for i in d :       
        if data.get(i) == d.get(i):  
            interet2 += 1
    if interet2 == len(d):
        interet = True
    return(interet)

def getallscenarios(node):
    """
take a node and build a list of all the scenarios starting at this node   
    """
    if len(node.children) == 0:
        return [[node]]
    return [
        [node] + path for child in node.children for path in getallscenarios(child)
    ]