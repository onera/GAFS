# -*- coding: utf-8 -*-
"""
Created on Tue Sep 28 10:21:25 2021

@author: cablanch
"""
import pandas as pd
import numpy as np
from bokeh.io import show
from bokeh.plotting import figure
from bokeh.models import HoverTool, Column, TableColumn, DataTable, Row, ColumnDataSource
from bokeh.models import Range1d
import tools
import matplotlib.pyplot as plt
from matplotlib import animation
import copy
#######################################################
# general statistics
#######################################################

def statistiques(scenarios,dict_etat,opinions):
    """
    Returns
    -------
    statistics (scenarios number, number of reached states/total states number, loop number, conflict number, number of scenarios where goals are reached))
    """
    nb_scenarios = len(scenarios)
    nb_etat_atteint = len(dict_etat)
    obj = 0
    conf = 0
    boucle = 0
    k = 0
    z = []
    total_etat = 1
    for i in opinions.index.get_level_values("Variable"):
        z.append(i)
        if z[len(z)-2]==i :
            k=k+1
        else : 
            total_etat = total_etat*k
            k=1
    total_etat = total_etat*k

    for i in scenarios:
        noeud_final = i[len(i)-1]
        if noeud_final.final == "objectif(s) atteint(s)":
            obj +=1
        if noeud_final.final == "conflit logique" or noeud_final.final == "conflit moral":
            conf +=1
        if noeud_final.final == "boucle":
            boucle +=1    

    pourcentage_reussi = (100*obj)/nb_scenarios
    
    return("Scenarios : "+str(nb_scenarios), "Reached states : "+str(nb_etat_atteint)+" over "+str(total_etat), 
           "Loop : "+str(boucle),"Conflicts : "+str(conf), "Goals reached :"+str(obj)+"("+str(pourcentage_reussi)+"%)")

def statconflit(scenariosconflit):
    """
    Return the statistics on the variables and decisions responsible for conflict situations

    Parameters : list of scenarios ending by a conflict
    """
    dictvar = {} #dict variable and percentage to appear in a conflict situation
    dictdecision = {} #dict decision and percentage to appear in a conflict situation
    listeconflit = [] #list of node with conflicts
    for i in scenariosconflit :
        listeconflit.append(i[len(i)-1]) #list of all the conflicts
    
    nbconflit1 = len(listeconflit)
    nbconflit2=0
    var_key = list(dictvar.keys())
    dec_key = list(dictdecision.keys())
    for noeud in listeconflit :
        all_list = noeud.mean[1]
        for minilist in all_list :
            nbconflit2 +=1
            for var in minilist :
                if var in var_key :
                    perc = dictvar.get(var)
                    dictvar.update({var :(perc + 1)})
                    
                else :
                    dictvar.update({var:1})
                    var_key = list(dictvar.keys())

        for listdec in list(noeud.mean[2].values()):
            for dec in listdec :
                all_varlist = noeud.mean[1]
                for varlist in all_varlist :
                    if dec.variable in varlist :
                        if dec.maniere in dec_key :
                            perc = dictdecision.get(dec.maniere)
                            dictdecision.update({dec.maniere:(perc+1)})
                        else:
                            dictdecision.update({dec.maniere:1})
                            dec_key = list(dictdecision.keys())

    for i in dictvar :
        nb = dictvar.get(i)
        dictvar.update({i:(nb/nbconflit2)})
    
    for i in dictdecision :
        nb = dictdecision.get(i)
        dictdecision.update({i:(nb/nbconflit1)})

    
    return(dictvar,dictdecision)

def var_vs_var_conflict(scenariosconflict):
    res_dict = {}
    listnodeconflict = []
    for scenario in scenariosconflict :
            listnodeconflict.append(scenario[len(scenario)-1])
    
    for nodeconflict in listnodeconflict :
        list_allvar = nodeconflict.mean[1]
        for list_var in list_allvar :
            keylist = res_dict.keys()
            for var in list_var :
                if var not in keylist :
                    res_dict.update({var : {}})
                list_var2 = copy.deepcopy(list_var)
                list_var2.remove(var)
                for var2 in list_var2 :
                    var_dict = res_dict.get(var)
                    keylist2 = var_dict.keys()
                    if var2 not in keylist2 :
                        var_dict.update({var2 : 1})
                    else :
                        var_dict[var2] +=1
    return (res_dict)


def statgoals(scenariosgoals):
    """
    Return the statistics on the variables and decisions responsible for conflict situations

    Parameters : list of scenarios ending by a conflict
    """
    
    dictdecision = {} #dict decision and percentage to appear in a conflict situation
    listegoal = [] #list of node with conflicts
    for i in scenariosgoals :
        listegoal.append(i[len(i)-1]) #list of all the conflicts
    
    nbgoal = len(listegoal)
    
    dec_key = list(dictdecision.keys())
    for node in listegoal :  
        for listdec in list(node.mean.values()):
            for dec in listdec :
                if dec.maniere in dec_key :
                    perc = dictdecision.get(dec.maniere)
                    dictdecision.update({dec.maniere:(perc+1)})
                else:
                    dictdecision.update({dec.maniere:1})
                    dec_key = list(dictdecision.keys())

    
    for i in dictdecision :
        nb = dictdecision.get(i)
        dictdecision.update({i:(nb/nbgoal)})

    
    return(dictdecision)


#######################################################
# graphical representation
#######################################################

def info_decision(scenarios, system, state_dict, principles, data_goal, data_positions, data_opinions):
    """
    return a dict = {pp1:[[favorable_decisions], [unfavorable_decisions], [nb_goals_reached]], pp2:...}
    """
    dct = {}
    for i in principles:
        dct[i]=[]
        dct.get(i).append(np.array([]))
        dct.get(i).append(np.array([]))
        dct.get(i).append(np.array([]))

    for scenario in scenarios:
        tot = tools.nbdecisiontotalact(scenario, system, 'VolFacile' )
        for i in principles :
            decision_nb = tools.nbdecisionnuance(system,scenario,state_dict,i,data_positions,data_opinions)
            lastnode = scenario[len(scenario)-1]
            obj_nb = goalsnumber(lastnode.data, state_dict, data_goal, 'Objectif')
            dct.get(i)[0] = np.append(dct.get(i)[0],decision_nb[0]/tot)
            dct.get(i)[1] = np.append(dct.get(i)[1],decision_nb[1]/tot)
            dct.get(i)[2] = np.append(dct.get(i)[2],obj_nb)
    return(dct)

def info_decision_mean1(scenarios, system, state_dict, principles, data_goal, data_positions, data_opinions):
    """
    return a dict = {pp1:{index:mean, index2:mean}, pp2:...}
    """
    dct = {}
    for i in principles:
        dct[i]={}

    for index in range (len(scenarios)-1):
        scenario = scenarios[index]
        #tot = tools.nbdecisiontotalact(scenario, system, 'EasyFlight' )
        for i in principles :
            decision_nb = tools.nbdecisionnuance(system,scenario,state_dict,i,data_positions,data_opinions)
            if decision_nb[1]==0 :
                mean = decision_nb[0]
            else :
                mean = decision_nb[0]/decision_nb[1]
            dct.get(i).update({index:mean})
    return(dct)

def info_decision_mean2(scenarios, system, state_dict, principles, data_goal, data_positions, data_opinions):
    """
    return a dict = {pp1:{index:mean, index2:mean}, pp2:...}
    index : index of a scenario in the list of all generated scenario
    mean : mean of how the pp is respected in the scenario 
    """
    dct = {}
    for i in principles:
        dct[i]={}

    for index in range (len(scenarios)-1):
        scenario = scenarios[index]
        #tot = tools.nbdecisiontotalact(scenario, system, 'EasyFlight' )
        for i in principles :
            decision_nb = tools.nbdecisionnuance(system,scenario,state_dict,i,data_positions,data_opinions)
            mean = decision_nb[0]-decision_nb[1]
            dct.get(i).update({index:mean})
    return(dct)

def Newgraphettppe(scenarios,system,state_dict, data_positions,data_opinions):
    x=np.array([])
    y=np.array([])
    c=np.array([])
    b=np.array([])
    g=np.array([])
    h=np.array([])
    for scenario in scenarios :
        a = tools.nbdecisiontotalact(scenario, system, 'VolFacile' )
        nb1 = tools.nbdecisionnuance(system,scenario,state_dict,"CreationRichesse",data_positions,data_opinions)
        x = np.append(x,nb1[0]/a)
        y = np.append(y,nb1[1]/a)
        nb2 = tools.nbdecisionnuance(system,scenario,state_dict,"MinimisationImpactEnvironnement",data_positions,data_opinions)
        c = np.append(c,nb2[0]/a)
        b = np.append(b,nb2[1]/a)
        nb3 = tools.nbdecisionnuance(system,scenario,state_dict,"SatisfactionClient",data_positions,data_opinions)
        g = np.append(g,nb3[0]/a)
        h = np.append(h,nb3[1]/a)
    
    fig = figure(width=400, height=400, tools="pan, hover, reset, save")
    fig.circle(c, b, color="green", size=15, legend_label = 'MinimisationImpactEnvironnement')
    fig.square(g, h, color="lightskyblue", size=10, alpha=0.5, legend_label = 'SatisfactionClient')
    fig.cross(x, y, color="deeppink", size=18, line_alpha=1.5 , legend_label = 'CréationRichesse')
    fig.output_backend="svg"
    fig.y_range = Range1d(-0.04, 0.5)
    fig.xaxis.axis_label = "Ratio de décisions favorables à l'utilisateur"
    fig.yaxis.axis_label = "Ratio de décisions défavorables à l'utilisateur"
    fig.legend.click_policy="hide"
    fig.legend.location = "top_right"
    show(fig)
    
def Linkinggraphettppe(scenarios,system,state_dict, data_positions,data_opinions):
    x=np.array([])
    y=np.array([])
    c=np.array([])
    b=np.array([])
    g=np.array([])
    h=np.array([])
    for scenario in scenarios :
        a = tools.nbdecisiontotalact(scenario, system, 'VolFacile' )
        nb1 = tools.nbdecisionnuance(system,scenario,state_dict,"CreationRichesse",data_positions,data_opinions)
        x = np.append(x,nb1[0]/a)
        y = np.append(y,nb1[1]/a)
        nb2 = tools.nbdecisionnuance(system,scenario,state_dict,"MinimisationImpactEnvironnement",data_positions,data_opinions)
        c = np.append(c,nb2[0]/a)
        b = np.append(b,nb2[1]/a)
        nb3 = tools.nbdecisionnuance(system,scenario,state_dict,"SatisfactionClient",data_positions,data_opinions)
        g = np.append(g,nb3[0]/a)
        h = np.append(h,nb3[1]/a)
    
    source = ColumnDataSource(data=dict(x=x, y=y, c=c , b=b, g=g, h=h))
    hover = HoverTool(tooltips = [("index","$index"),("(x,y)","($x,$y)"),("desc","@desc")])
    fig = figure(width=400, height=400, tools="pan, tap, box_zoom,wheel_zoom, hover, reset, box_select, save")#, title="Plot 2"
    rendu = fig.circle('c', 'b', selection_color="red", nonselection_fill_alpha=0, nonselection_line_alpha=0.5, size=15, source = source, legend_label = 'EnvironmentalProtection')
    fig.output_backend="svg"

    fig1 = figure(width=400, height=400, tools="pan, tap, box_zoom,wheel_zoom, hover, reset, box_select,  save")
    rendu1 = fig1.square('g', 'h', selection_color="blue", nonselection_fill_alpha=0, nonselection_line_alpha=0.5, size=10, alpha=0.5, source = source, legend_label = 'CustomerSatisfaction')
    fig1.output_backend="svg"
    
    fig2 = figure(width=400, height=400, tools="pan, tap, box_zoom,wheel_zoom, hover, reset, box_select, save")
    rendu2 = fig2.cross('x', 'y', selection_color="green", nonselection_fill_alpha=0, nonselection_line_alpha=0, size=14, source = source, legend_label = 'WealthCreation')
    fig2.output_backend="svg"
    
    # nonselected_circle = Circle(fill_alpha = 0.01)
    # selected_circle = Circle(fill_alpha=1)
    # rendu.nonselection_glyph = nonselected_circle
    # rendu1.nonselection_glyph = nonselected_circle
    # rendu2.nonselection_glyph = nonselected_circle
    # rendu.selection_glyph = selected_circle
    # rendu1.selection_glyph = selected_circle
    # rendu2.selection_glyph = selected_circle
    columns = [
        TableColumn(field="x", title="x"),
        TableColumn(field="y", title="y"),
        TableColumn(field="c", title="c"),
        TableColumn(field="b", title="b"),
        TableColumn(field="g", title="g"),
        TableColumn(field="h", title="h"),
    ]
    datatable = DataTable(source=source, columns = columns, width = 400, height = 400)
    #ax.scatter(c,b, s=14, c='r', marker='x',label = 'EnvironmentalProtection')
    #ax.scatter(g,h, s=10, c='g', marker='v',label = 'CustomerSatisfaction')
    #ax.scatter(x,y, s=10, c='c',marker='o', label = 'WealthCreation') , tools=[hover]

    #plt.legend(loc = 'upper left') #; ??
    #plt.xlabel("nb de décisions favorables à l'utilisateur")
    #plt.ylabel("nb de décisions défavorables à l'utilisateur")
    fig.xaxis.axis_label = "Ratio de décisions favorables"
    fig.yaxis.axis_label = "Ratio de décisions défavorables"
    fig.legend.click_policy="hide"
    fig.legend.location = "top_right"
    fig2.legend.click_policy="hide"
    fig2.legend.location = "top_right"

    #p = gridplot([[datatable, fig, fig1, fig2]])
    show(Column(Row(fig, fig1), Row(fig2, datatable)))

def graph_objppe(scenarios, system, state_dict, data_positions,data_opinions, data_goal, principles):
    """
    principles: list of str of the principles
    """
    fig = plt.figure()#figsize=plt.figaspect(0.5))
    ax = fig.add_subplot(projection='3d')
    dct = info_decision(scenarios, system, state_dict, principles, data_goal, data_positions, data_opinions)
    
    clrs=['indianred','steelblue','g','c','m','y','k']
    shpe=['o','*', 'v', 's', 'X','h', 'd' ]
    for i in range(len(principles)) :
        ppe = principles[i]
        scat = ax.scatter(dct.get(ppe)[0],dct.get(ppe)[1],dct.get(ppe)[2], s=40,facecolors='none', edgecolors=clrs[i], marker=shpe[i],label = ppe)
    ax.set_xlabel("Ratio de décisions favorables (x)")
    ax.set_ylabel("Ratio de décisions défavorables (z)")
    ax.set_zlabel("Nombre d'objectifs atteints (y)")
    plt.legend(loc = 'upper left')
    ax.view_init(elev=10., azim=70)
    plt.savefig('fig_gif.png',dpi=800)
    plt.show()
    def init():
        ax.view_init(elev=10., azim=0)
        return [scat]


    def animate(i):
        ax.view_init(elev=10., azim=i)
        return [scat]
    # Animate
    anim = animation.FuncAnimation(fig, animate, init_func=init,
                               frames=90, interval=20, blit=True)

#plt.show()
# Save
    writervideo=animation.PillowWriter(fps=30)
    anim.save('basic_animation.gif', writer = writervideo)#extra_args=['-vcodec', 'libx264'])


#######################################################
# goal reaching
#######################################################

def objnonrealisable(valeursnonatteintes,data_objetrupture): 
    """
    Deduct if values have never been reached in the scenarios and therefore if goals are not achievable
    """
    index1 = 0
    d = {}
    objnul = {}
    #dict of the variables and values that are the goals
    for k in data_objetrupture["Objectif"]:
        if pd.isnull(k)==False:
            variable = data_objetrupture["Variable"][index1]
            valeur = data_objetrupture["Valeur"][index1]
            if variable in list(d.keys()) :
                a = d.get(variable)
                a.append(valeur)
                d.update({variable:a})
            else :
                d.update({variable : [valeur]})
        index1 += 1
    
    for i in d :
        for valeur in valeursnonatteintes.get(i) :
            listobjectif = d.get(i)
            if valeur in listobjectif:
                if i in list(objnul.keys()):  
                    k = objnul.get(variable)
                    k.append(valeur)
                    objnul.update({variable:k})
                else :
                    objnul.update({i:[valeur]})
                
    return(objnul)

def goalsnumber(datanode, dict_etat, data_objetrupture, goal):    
    """
return the number of goals reached in a node
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
    interet2 = 0
    for i in d :       
        if data.get(i) == d.get(i):  
            interet2 += 1
    return(interet2)

def scenariosmaxgoalscut(scenarios, state_dict, data_goal, goal):
    """
    Stop the scenarios when they have reached there maximum of goals achieved
    """
    scenariosgoals = []
    for scenario in scenarios:
        goal_max = [0,0]
        index = 0
        for node in scenario:
            goals_nb = goalsnumber(node.data, state_dict, data_goal, goal)
            if goals_nb > goal_max[0]:
                goal_max = [goals_nb, index]
            index += 1
        if goal_max[0]==0 or goal_max[1] == (len(scenario)-1):
            scenariosgoals.append(scenario)
        else :      
            scenariosgoals.append(scenario[:(goal_max[1]+1)])
    return(scenariosgoals)

def ppcompromised_goal(scenarios, system):
    """
    return the principles the user has to compromised to achieve its goals
    if existing, return the dict of scenarios allowing to reach the goals without compromising any principles
    """
    utilisateur = tools.utilisateurqui(system).name
    res = {}
    zerotransg = {}
    indice = 0
    statpp = {}
    for pp in system.pp :
        statpp.update({pp:0})
    for scenario in scenarios :
        listepp = []
        for noeud in scenario : 
            if type(noeud.mean) != list and noeud.mean != {}:    
                for decision in noeud.mean.get(utilisateur) :
                    if decision.transgresseppe != []:
                        for pp in decision.transgresseppe :
                            if pp not in listepp :
                                listepp.append(pp)
            else :
                if noeud.mean !={} and type(noeud.mean) == list:
                    for decision in noeud.mean[2].get(utilisateur) :
                        if decision.transgresseppe != []:
                            for pp in decision.transgresseppe :
                                if pp not in listepp :
                                    listepp.append(pp)

        if listepp == []:
            zerotransg.update({indice:len(scenario)})
        else :
            res.update({indice:[len(scenario),listepp]})
            for k in listepp :
                statpp.update({k:statpp.get(k)+1})
        indice += 1 
    
    for i in statpp :
        statpp.update({i:statpp.get(i)/len(scenarios)})
    
    if zerotransg == {} :
        return("One or more principles have to be compromised for the goals to be achieved", statpp, res)
    else :
        return("Some scenarios don't require the user to compromise its principles to achieve its goals", statpp, zerotransg, res)

#######################################################
# grouping by respected principle
#######################################################
def respected_pp(scenarios, principle, n,system,state_dict, data_positions, data_opinions) :
    """
    return all the scenarios that go n time against the principle 
    """
    res = []
    for scenario in scenarios :
        number = tools.nbdecisionnuance(system,scenario, state_dict, principle, data_positions, data_opinions)
        if number[1]<=n :
            res.append(scenario)
    return(res)

def respected_pp_allact(scenarios, principle, n,system,state_dict, data_positions, data_opinions) :
    """
    return all the scenarios that go n time against the principle 
    """
    res = []
    for scenario in scenarios :
        number = tools.nbdecisionnuance_allact(system,scenario, state_dict, principle, data_positions, data_opinions)
        if number[1]<=n :
            res.append(scenario)
    return(res)

#######################################################
# best scenario(s)
#######################################################

#after using the function ppcompromised_goal if there is no ideal scenario not compromising
#any principle, look for the best trade-off
def bestscenario(scenarios, principles, system, state_dict, data_goal, data_positions, data_opinions):
    """
    retourne une liste des meilleurs scénarios par principes et un dict avec leur indice dans la liste initiale
    """
    dct = info_decision_mean1(scenarios, system, state_dict, principles, data_goal, data_positions, data_opinions)

    bestoptionfinalliste = {}
    bestoptionfinaldict={}
    top = 0
    nb = []
    for ppe in principles : 
        i = dct.get(ppe)
        values= list(i.values())
        bestoption =[]
        for index in range (len(values)-1):
            a = values[index] 
            if a>top:
                top=a
                nb.clear()
                nb.append(index)
            if a == top:
                nb.append(index)
        for k in nb :
            bestoption.append(scenarios[k])
        bestoptionppe=copy.deepcopy(bestoption)
        bestoptionfinalliste[ppe]=bestoptionppe
        bestoption.clear()
        top = 0
        nb = []
    return(bestoptionfinalliste, bestoptionfinaldict)