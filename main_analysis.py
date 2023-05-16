import tools
import analyse_bdd_general
import analyse_spmf
import TraitementDataconflit


a = TraitementDataconflit.tablecreation("usecase_initialdata.xlsx")
data_decision = a[3]
data_opinions = a[0]
data_positions = a[1]
data_user = a[2]
data_initialstate = a[6]
data_logicalconstraint = a[4]
data_pplconstraint = a[5]
data_goals = a[7]


D = tools.dataload('stockage_d.pkl')
state_dict = tools.dataload('stockagedict_etat.pkl')
scenarios = tools.dataload('stockage_scenarios.pkl')
system = tools.dataload('stockage_systeme.pkl')

scenariosconflict = tools.scenarioobjatteint(scenarios, "conflit logique")
scenariosgoals = tools.scenarioobjatteint(scenarios, "objectif(s) atteint(s)")

################ Statistics##################################
print(analyse_bdd_general.statistiques(scenarios, state_dict, data_opinions))

print("The following values of variables are never reached in the scenarios:")

never_reached_values = tools.valeursNonAtteintes(state_dict,system)
print(never_reached_values)

print("so we will never been able to achieve the following goals:")
print(analyse_bdd_general.objnonrealisable(never_reached_values,data_goals))

#############################################################
################ Goals achievements #########################

#Launch this function if the goals are achieved in at least one scenario
obj = analyse_bdd_general.ppcompromised_goal(scenariosgoals,system)
print(obj[0])
print(obj[1])

#print the graph representing the number of goals achieved as a function of the decisions taken
scenariosmaxgoals = analyse_bdd_general.scenariosmaxgoalscut(scenarios, state_dict, data_goals, 'Objectif')
scenariosgoals_final = tools.removeduplicate(scenariosmaxgoals)
analyse_bdd_general.graph_objppe(scenariosgoals_final, system, state_dict, data_positions,data_opinions, data_goals, ["WealthCreation", "EnvironmentalProtection","CustomerSatisfaction"])

#############################################################
################ Stat conflict ##############################
statconflit = analyse_bdd_general.statconflit(scenariosconflict)
print("\nStatistics on the variables responsible for conflicts")
print(statconflit[0])
print("\nStatistics on the decisions responsible for conflicts")
print(statconflit[1])


#############################################################
################ Scenarios representation ###################

print(analyse_bdd_general.Newgraphettppe(scenarios,system, state_dict, data_positions, data_opinions))

#############################################################
################ Sequence analysis ######################

#-------------------- Sequential Rule Mining ---------------------#

#prepare the files that are going to be analyse by Data mining algorithms
analyse_spmf.inputBDDspmf(scenarios, D, state_dict)
analyse_spmf.inputspmfprincipe(scenarios, system)
print("Database generated")

#Generate the file using the algorithm RuleGrowth with the file inputBDD
dataoutputspmf = analyse_spmf.outputspmf('output_miniusecase1_usereasyflight.txt')
listconflitspmf = analyse_spmf.listconflitspmf(dataoutputspmf)
listobjectifspmf = analyse_spmf.objectifspmf(dataoutputspmf)

print("The set of decisions giving conflicts with the highest confidence/sufficiency: ")
maxconf = analyse_spmf.max_seq(listconflitspmf, 2, 'No')
print(maxconf[0])

if maxconf[1] == 1 :
        print("There is one or more set of decisions that are sufficient for a conflict to happen", max[0])
else:    
    print("There is no set of decisions that is sufficient for a conflict to happen.")

print ("The smallest set of decision with the maximum probability for a conflict to happen is: ")
sequencemin = analyse_spmf.seqmin(maxconf[0])
print(sequencemin)
#to know if the smallest sequence with the highest sufficiency is necessary
necessary = analyse_spmf.set_necessary(sequencemin, len(scenariosconflict))
print(necessary)

#to look for the most necessary sequences
necessary2 = analyse_spmf.set_necessary(listconflitspmf, len(scenariosconflict))
print(necessary2)



# #--------------------------Sequential Pattern mining------------
#Generate the file using PrefixSpan with the file inputBDD
dataoutputspmf2 = analyse_spmf.outputspmf2('output_miniusecase_usereasyflight_prefixspan.txt')
listconflitspmf2 = analyse_spmf.listconflitspmf2(dataoutputspmf2, "conflitlogique") #end : "objectif(s)atteint(s)", "conflitlogique"
maxsup = analyse_spmf.max_seq(listconflitspmf2, 1, 'No')
necessary_PS = analyse_spmf.set_necessary(maxsup[0], len(scenariosconflict))
print(necessary_PS)
listedecisionscenarios = tools.listedecisionscenario1(scenarios)
sufficiency_PS = analyse_spmf.set_sufficiency(necessary_PS[1], listedecisionscenarios)
print(sufficiency_PS)

sufficiency_PS2 = analyse_spmf.set_sufficiency(listconflitspmf2, listedecisionscenarios)
print(sufficiency_PS2)

#############################################################
################ Best scenarios #############################

best = analyse_bdd_general.bestscenario(scenariosgoals, ["WealthCreation", "EnvironmentalProtection","CustomerSatisfaction"], system, state_dict, data_goals, data_positions, data_opinions)
print(best)
tools.allscenariostoreadbetter("bestscenarios_output.txt", best[0].get("WealthCreation"), state_dict)