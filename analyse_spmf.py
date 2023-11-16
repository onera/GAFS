# -*- coding: utf-8 -*-
"""
Created on Tue Sep 28 10:21:25 2021

@author: cablanch
"""

import numpy as np
import tools


def inputBDDspmf(scenarios, D, Dictio_etat):
    """
    Return database in the right format to be use in spmf tool.

    Parameters
    ----------
    scenarios : List of scenarios
    D : dict of decisions
    Dictio_etat : dict of states

    """
    Dnumbers = {}
    with open('inputBDD.txt','w') as f: #pas besoin de close avec le ouif (with)
        f.write('@CONVERTED_FROM_TEXT\n')
        etatNumber = np.max(list(Dictio_etat.keys()))
        itemNumber = etatNumber + 1
        for e in list(Dictio_etat.keys()):
            f.write('@ITEM='+str(e)+"=Etat"+str(e)+"\n")
        for k in D.keys():
            f.write('@ITEM='+str(itemNumber)+"="+k+"\n")
            Dnumbers[k]=itemNumber
            itemNumber += 1    
        conflitNumber = itemNumber
        f.write('@ITEM='+str(conflitNumber)+"=conflitlogique"+"\n")
        boucleNumber = itemNumber +1
        f.write('@ITEM='+str(boucleNumber)+"=boucle"+"\n")
        objNumber = itemNumber +2
        f.write('@ITEM='+str(objNumber)+"=objectif(s)atteint(s)"+"\n")
        for i in scenarios :
            for noeud in i :
                if noeud.mean != {}:
                    if type(noeud.mean)==list:
                        for decision in list(noeud.mean[2].values()):
                            for k in decision :                                
                                decisionNumber = Dnumbers.get(k.maniere)
                                f.write(str(decisionNumber)+" ")
                        f.write("-1 ")
                    else :
                    
                        l = list(noeud.mean.keys()) #liste des acteurs
                        for acteur in l :
                            for decision in noeud.mean.get(acteur) :
                                decisionNumber = Dnumbers.get(decision.maniere)
                                f.write(str(decisionNumber)+" ")
                        f.write("-1 ")
                    if noeud.final == "conflit logique" :
                            f.write(str(conflitNumber)+" -1 ")
                    if noeud.final == "boucle" :
                            f.write(str(boucleNumber)+" -1 ")
                    if noeud.final == "objectif(s) atteint(s)" :
                            f.write(str(objNumber)+" -1 ")
                    #f.write(str(noeud.data)+" -1 ")
            f.write("-2\n")
       
def inputspmfprincipe(scenarios, systeme):
    """
    The database to use spmf algorithms with the end of the scenarios and the principles compromised

    principle compromised : opinion = -1 et position = +
    """
    
    with open('inputBDDppe.txt','w') as f: 
        f.write('@CONVERTED_FROM_TEXT\n')
        utilisateur = tools.utilisateurqui(systeme).name
        
        Pnumber = {} 
        nb = 1
        for ppe in systeme.pp :
            f.write('@ITEM='+str(nb)+"="+ppe+"\n")
            Pnumber.update({ppe:nb})
            nb+=1
            
        conflitNumber = nb
        f.write('@ITEM='+str(conflitNumber)+"=conflitlogique"+"\n")
        boucleNumber = nb +1
        f.write('@ITEM='+str(boucleNumber)+"=boucle"+"\n")
        objNumber = nb +2
        f.write('@ITEM='+str(objNumber)+"=objectif(s)atteint(s)"+"\n")

        for scenario in scenarios :
            for noeud in scenario :
                
                if type(noeud.mean) != list and noeud.mean != {}:
                    
                    for decision in noeud.mean.get(utilisateur) :
                
                        if decision.transgresseppe != []:
                            for i in decision.transgresseppe :
                                
                                ppNumber = Pnumber.get(i)
                                
                                f.write(str(ppNumber)+" ")
                            f.write("-1 ")
                else :
                    if noeud.mean != {}:
                        for listdecision in list(noeud.mean[2].values()):
                            for dec in listdecision :                                
                                if dec.transgresseppe != []:
                                    for i in dec.transgresseppe :                               
                                        ppNumber = Pnumber.get(i)                               
                                        f.write(str(ppNumber)+" ")
                                    f.write("-1 ")
                
                if noeud.final == "conflit logique" :
                    f.write(str(conflitNumber)+" -1 ")
                if noeud.final == "boucle" :
                    f.write(str(boucleNumber)+" -1 ")
                if noeud.final == "objectif(s) atteint(s)" :
                    f.write(str(objNumber)+" -1 ")
            f.write("-2\n")

def outputspmf(fichier):
    """
    return the result given by the use of RuleGrowth (sequential rule mining) 
    algorithm through spmf under a list of ['sequence', 'sup', 'conf']
    sequence : 'A,B,C ==> 'end of scenario'
    """
    output = []
    with open(fichier,'r') as f:
        sequence = []
        for line in f:
            x = line [:-1]
            indice = 0
            nb = 0
            for k in x :
                indice +=1

                if k == '#' and nb == 1:
                    indice2 = indice
                    b = line[indice1+5:indice2-2]
                    sequence.append(b)
                    nb = 2

                if k == '#' and nb == 0:
                    indice1 = indice
                    a = line[:indice1-2]
                    sequence.append(a)
                    nb = 1

            c = line[indice2+6:-1]
            sequence.append(c)    
                   
            output.append(sequence)
            sequence = []
    return(output)

def outputspmf2 (fichier):
    """
    return the result given by the use of PrefixSpan (sequential pattern mining)
    algorithm through spmf under a list of [sequence, sup]
    """
    output = []
    with open(fichier,'r') as f:
        sequence = []
        nb = 0
        for line in f:
            x = line [:-1]
            indice = 0
            for k in x :
                indice +=1
                decision = []
                if k == '#' :
                    indicesup = indice
                    a = line[:indicesup-2]
                    indice1 = 0
                    indice2 = 0
                    for item in a :
                        indice2 +=1
                        if item == "-"and nb == 0:
                            aprime = line[indice1:indice2 -2]
                            indice1 = indice2
                            aprime2 = aprime.split()
                            decision.append(aprime2)
                            nb +=1
                        elif item == "-" and nb>0 :
                            aprime = line[indice1 + 2:indice2 -2]
                            indice1 = indice2
                            aprime2 = aprime.split()
                            decision.append(aprime2)
                    sequence.append(decision)
                    decision = []

            c = line[indicesup + 5:-1]
            
            sequence.append(c)          
            output.append(sequence)
            sequence = []
            nb = 0
    return(output)

def listconflitspmf(outputspmf) :
    """
    Return only the sequences concerned by conflicts in spmf
    using the file returned by outputspmf (RuleGrowthAlgorithm)
    """
    res = []
    for k in outputspmf :
        if k[0][-14:] == "conflitlogique" :
            res.append(k)
    return(res)

def objectifspmf(outputspmf) :
    """
    Return only the sequences concerned by the goals reached in spmf
    using the file returned by outputspmf (RuleGrowthAlgorithm)
    """
    res = []
    for k in outputspmf :
        if k[0][-21:] == "objectif(s)atteint(s)" :
            res.append(k)
    return(res)

def listconflitspmf2 (outputspmf2, fin):
    res =[]
    for i in outputspmf2 :
        if i[0][len(i[0])-1] == [fin] :
            res.append(i)
    return(res)

def max_seq (data, index, option):
    """
    using the files of spmf (RuleGrowth or PrefixSpan)
    return the sequences giving the highest confidence or support
    Si support : index = 1, si confidence : index = 2
    Option = 'Yes' if we want as results sections with a length higher than 1, only works for PrefixSpan data
    """
    num = 0
    max = []
    for k in data :
        conf = float(k[index])
        if option == 'Yes':
            if conf == num and (len(k[0])>2 or len(k[0][0])>1):
                max.append(k)
            if conf>num and (len(k[0])>2 or len(k[0][0])>1):
                num = conf
                max.clear()
                max.append(k)
        else :
            if conf == num and len(k[0])>1:
                max.append(k)
            if conf>num and len(k[0])>1:
                num = conf
                max.clear()
                max.append(k)
    return (max, num)

def seqmin (data):
    """
    using the result of max_conf_RG[1] (RuleGrowth algorithm results)
    Retrieve the smallest sequence of the set
    """
    smallest = []
    init = 1
    for k in data :
        indice = 0
        for b in k[0]:
            indice +=1 
            if b== '=':
                liste = str(k[0][:indice-2])
                break

        liste1 = liste.split(",")

        lengthk=len(liste1)
        if init == 1 : 
            lengthmin = lengthk
            init = 2

        if lengthk == lengthmin :
            smallest.append(k)
        if lengthk<lengthmin :
            smallest.clear()
            smallest.append(k)
            lengthmin = lengthk
        
    return(smallest)

def necessaryseq(proba_sup, proba_fin):
    if proba_fin !=0 :
        necessary_seq = proba_sup/proba_fin
    else :
        necessary_seq = 0
    if necessary_seq == 1 :
        return (True)
    else : 
        return(False, necessary_seq)

def set_necessary (data, nb_conflicts):
    set = []
    set2 = []
    for k in data :
        res = necessaryseq(float(k[1]), nb_conflicts)
        if res==True :
            set.append(k)
        else :
            set2.append([k, res[1]])
    if set == [] :
        res2 = max_seq(set2,1, 'No')
        res3 = []
        for k in res2[0]:
            res3.append(k[0])
        return("There are no sets of decisions that is necessary for a conflict to happen",res3, res2[1])
    else :
        return("There are one or more sets of decisions that are necessary for a conflict to happen", set)



def nbscenarios_seq(sequence, scenarios):
    """
    return the number of scenario where we can find this sequence of proba
    sequence : list of list of decisions
    scenarios : list of list of decisions
    """
    index = 0
    for s in scenarios :
        if tools.decisions_in_scenario(sequence, s)==True:
            index +=1
    res = index
    
    return(res)
    
def sufficiencyseq_prefixspan(proba_sup, proba_seq):
    if proba_seq != 0 :
        sufficiency_seq =  proba_sup/proba_seq
    else :
        sufficiency_seq=0
    if sufficiency_seq == 1 :
        return (True)
    else : 
        return(False, sufficiency_seq)   


def set_sufficiency (data, scenarios):
    set = [] 
    set2 = []
    for k in data :
        #print(k[0][:-1])
        nb_scenario_decision = nbscenarios_seq(k[0][:-1], scenarios)
        res = sufficiencyseq_prefixspan(float(k[1]),nb_scenario_decision)
        if res==True :
            set.append(k)
        else :
            set2.append([k, res[1]])
    if set == [] :
        res2 = max_seq(set2,1, 'No')
        res3 = []
        for k in res2[0]:
            res3.append(k[0])
        return("There are no sequences sufficient for a conflict to happen", res3, res2[1])
    else:
        return("There are one or more sequences that are sufficient for a conflict to happen", set)
    
        

    


#def seqnecessaire(seqmin, scenariosliste) :
    """
    sequmin : the sequence we want to analyse to see if it is a necessary condition
    scenariosliste : The list of scenarios ending by an ending criteria
    (conflict, goals...)

    check if the sequence given is included in every scenario of scenariosliste
    used to see if the condition that is seqmin is necessary for something to happen
    """
    
    for k in seqmin :
        indice = 0
        for b in k[0]:
            indice +=1 
            if b== '=':
                liste = str(k[0][:indice-2])
                break
    listeseq = liste.split(",")
    nb = len(listeseq)
    longliste = len(scenariosliste)
    compt2 = 0
    
    for scenario in scenariosliste :
        
        listedec = []
        for noeud in scenario :
            if noeud.mean != {}:
                if type(noeud.mean)==list:
                    
                    for listdecision in list(noeud.mean[2].values()) :
                        for decision in listdecision : 
                            listedec.append(decision.maniere)
                else :
                    
                    l = list(noeud.mean.keys()) #liste des acteurs
                    for acteur in l :
                        for decision in noeud.mean.get(acteur) :
                                listedec.append(decision.maniere)
        compt = 0
        for item in listeseq :
            if item in listedec :
                compt +=1
        if nb == compt :
            compt2 += 1
    if longliste == compt2 :
        return("This set is a necessary condition for a conflict to happen")
    else : 
        return(compt2/longliste,"This set is not a necessary condition for a conflict to happen")

