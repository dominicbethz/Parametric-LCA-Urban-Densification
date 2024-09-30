#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 14:18:03 2024

@author: dominicbuettiker
"""

#Main py


import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import sys
import os
import time
import datetime
from matplotlib.ticker import MaxNLocator
import itertools


from multiprocessing import Pool, cpu_count


main_path = "/Users/dominicbuettiker/Library/CloudStorage/OneDrive-Persönlich/Dominic/ETH/2_Master/4. Semester/Masterarbeit/Code/Model/Parametric_LCA_Master_Thesis/"
export_path_robust = "/Users/dominicbuettiker/Library/CloudStorage/OneDrive-Persönlich/Dominic/ETH/2_Master/4. Semester/Masterarbeit/Code/Model/Parametric_LCA_Master_Thesis/Results/robust_evaluation/"
export_path_UA_robustness =  "/Users/dominicbuettiker/Library/CloudStorage/OneDrive-Persönlich/Dominic/ETH/2_Master/4. Semester/Masterarbeit/Code/Model/Parametric_LCA_Master_Thesis/Results/UA_robustness/"

input_db = os.path.join(main_path, 'input_data') #path
DUREE_db = pd.read_excel(f'{input_db}/duree_db.xlsx', 'Data', skiprows=[0],index_col="Code")
intervention_designs = pd.read_excel(f'{input_db}/intervention_designs.xlsx', 'interventions_1', skiprows=[1])


sys.path.append(main_path) #To import functions form main folder 
import Setup_Simulation as ss
from multi_core_model_big_2 import process_params
from qmc_sampling import sample
import Evaluation.functions_plotting as fp
import Functions.general_helper as gh


#%% IMPORTANT: whole pice must be run at one. 


N = 2**11 #2**9 #2048 512 #Number of samples, must be 2**n for sobol sampling!  2**11 ist the minimal sample size, based on the robustness study
sampling_technique = 'sobol' #'montecarlo',#'sobol',

evaluation = 'multiple_scenario' #'one_scenario' 'robust_assessment, 'multiple_scenario'

scenario_group_multi = ['same_interventions_on_all_2']#, same_interventions_on_all_2 ['same_interventions_on_all_1'] test_mechanical_ventilation_2  # MUST BE IN LIST FORMAT!!!  #This param is neede for the multiple_scenario assessment, else not!, it filters the column scenario_group on selected group 
scenario_group_multi_exportname = 'same_interventions_on_all_2'# same_interventions_on_all_2, 'same_interventions_on_all_1' test_mechanical_ventilation_2
#%% DESIGN PARAMS TO BE EDITED for one_scenario and robust_assessment
scenario_group = 'kanzleistrasse'
label = 'kanzleistrasse_1_test'                  # labeling of the scenario 
scenario = 3                                         # 0= BAU (no intervention) 1=renovation, 2=new construction 3=add stories
original_building_archetype =  '30s_Kanzleistrasse'     #{1:"30s_Kanzleistrasse",2:"Garden_city_herrlig", 3:"60s_Salzweg", 4:"60s_Salzweg_ren", 5:"70_s_Lerchenberg", 6:"eRen4" }
window_to_wall_ratio_new = 0.3                          # 0.2 to 0.6 reasonable 
add_storeys_new = 3                                     # 0,1,2,3,reasonable 
change_footprint_area_new = 0.2                         # 0 - 0.3 reasonable
add_storeys_extension = 2                               # 1,2 reasonalble 

insulation_type_renovation = 'straw'                    #{1:"original", 2:"straw", 3:"rockwool", 4:"xps"}
insulation_thickness_renovation = '48'                  #{1:'8', 2:'16', 3:'24', 4:'32', 5:'48', 6:'64'}
window_type_renovation = 'original'                     #{1:"original", 2:"window_dbl_1.1_wood_9", 3:"window_dbl_1.1_wood_metal_9", 4:"window_trpl_0.6_wood_9", 5:"window_trpl_0.6_wood_metal_9"} 
interior_renovation_at_intervention = False             #False/True


insulation_type_new = 'straw'                           #{ 2:"straw", 3:"rockwool", 4:"xps"}
insulation_thickness_new = '48'                         #{1:'8', 2:'16', 3:'24', 4:'32', 5:'48', 6:'64'}
window_type_new = "window_dbl_1.1_wood_9"               #{2:"window_dbl_1.1_wood_9", 3:"window_dbl_1.1_wood_metal_9", 4:"window_trpl_0.6_wood_9", 5:"window_trpl_0.6_wood_metal_9"} 
construction_type_new = 'full_concrete_conventional'    #{1:'full_concrete_conventional', 2:'full_concrete_lowco2', 3:' wood_armature_classical', 4:'wood_armature_lowco2', 5:'wood_armature_rammed_earth'}
construction_type_add_storeys = 'wood_frame_classical'  #{1:'wood_frame_classical', 2:'wood_frame_lowco2'}

heating_system_overall = 'ASHP'                         #{1:"ASHP", 2:"GSHP", 3:"district", 4:"electric", 5:"Natural Gas"}
has_mechanical_ventilation = False                      #False/True


#FIX DESIGN PARAMS 1.0
heating_system_dhw_sc = 'same'                          #other options possible, but does not make sense
heat_emission_system_sc = 'floor heating'               #'floor heating' or 'radiator' 
heat_distribution_system_sc = 'hydronic'                #other options possible, but does not make sense

account_for_biogenic_carbon = True                      #False/True
account_disposal_emissions_of_existing_building = True  #False/True

#FIX DESIGN PARAMS 2.0
cooling_system_sc = 'None'
cold_emission_system_sc = 'None'
simplifed_LCA = False
change_orientation = 0 #scales length and width respectifly: X>0 -> N/S increases, X<0 N/S decreases. 0=Same width to length ratio
infiltration_volume_flow_ren = 0.15



#TODO: Create function to read configruations form 
    
#%% UNCERTAIN PARAMS SAMPLING TECHNIQUE, ATTENTION SOME AJUSTMENS ARE MADE AFTERWORDS IN THE MODEL FUNCTION! e.g. grid decarbonization

"""
DOCUMENTATION QUASI MONTECARLO SAMPLING TECHNIQUES
SOBOL SAMPLING: 
must be 2**n for convergence


"""

problem ={
    'sampling_technique': sampling_technique, #'montecarlo',#'sobol',
    
    'names': [ 'thermal_bridge_add_on_ren','thermal_bridge_add_on_new',
                 'ventilation_volume_flow','heating_setpoint',
                 'electricity_decarbonization_factor_helper','embodied_emissions_decarbonization_fraction',
                 'windows_RSL','insulation_RSL','flat_roof_covering_RSL','sloping_roof_covering_RSL', 'facade_ventilated_finishing_RSL','facade_plasterd_finishing_RSL',
                 'internal_covering_wall_RSL','internal_flooring_RSL',
                 'conversion_RSL_heating_system' , 'distribution_RSL_hydronic', 'emission_system_RSL', 'ventilation_system_RSL'],    
    'bounds':[  
                #Exogenous params 
                [0.0, 30.0],  # thermal_bridge_add_on_ren,      Group: thermal bridge add on    acc. xxx 15% in mean
                [0.0, 30.0],  # thermal_bridge_add_on_new,      Group: thermal bridge add on    acc. xxx 15% in mean
                
                [0.7, 1.0],   # ventialtion volume flow         Group: ventilation rate         acc. SIA 2021_2024 -> 0.8. Distribution unif. from Galimshina et.al. 2020 
                [18, 23],     # heating_setpoint,               Group: heating setpoint
                
                [0.5,5.5,0.25],  #[0.5,5.5], # #grid_decarbonization_factor,     Group: Grid decarbonization factor,  Grid decarbonized until 2040, 2050, 2060, 2070, 2080, distribution triangualr: with peak at 2050
                [np.log(0.75),(-np.log(0.6)+np.log(1))/(2*1.645)], #materials decarbonization factor Group: material decarbonization factor -> fraction of GHG in 2050, afterwords constant. triangualr distribution with tendency to optimal decaronization. 
                
                #RSL exogenous params (lognormal distributed)
                [DUREE_db.loc['E 3.1','meanlog'], DUREE_db.loc['E 3.1','sdlog']],   # Windows RSL                      Group: RSL envelop
                [DUREE_db.loc['E 2.2a','meanlog'], DUREE_db.loc['E 2.2a','sdlog']], # Insulation RSL                   Group: RSL envelop
                [DUREE_db.loc['F 1.2','meanlog'], DUREE_db.loc['F 1.2','sdlog']],   # Flat roof covering RSL           Group: RSL envelop
                [DUREE_db.loc['F 1.3','meanlog'], DUREE_db.loc['F 1.3','sdlog']],   # Sloping roof covering RSL        Group: RSL envelop
                [DUREE_db.loc['E 2.3b','meanlog'], DUREE_db.loc['E 2.3b','sdlog']], # Facade ventilated finishing RSL, Group: RSL envelop
                [DUREE_db.loc['E 2.2b','meanlog'], DUREE_db.loc['E 2.2b','sdlog']], # Facade plasterd finishing RSL,   Group: RSL envelop
                
                [DUREE_db.loc['G 3.2','meanlog'], DUREE_db.loc['G 3.2','sdlog']],   # int covering wall RSL            Group: RSL interior finishings
                [DUREE_db.loc['G 2.2','meanlog'], DUREE_db.loc['G 2.2','sdlog']],   # int flooring RSL                 Group: RSL interior finishings
               
                [DUREE_db.loc['D 5.2','meanlog'], DUREE_db.loc['D 5.2','sdlog']],    # conversion RSL,                 Group: RSL systems, (heat productio, assumption the same RSL for all systems!)
                [DUREE_db.loc['D 5.3','meanlog'], DUREE_db.loc['D 5.3','sdlog']],    # distribution RSL (hydronic),    Group: RSL systems,
                [DUREE_db.loc['D 5.4','meanlog'], DUREE_db.loc['D 5.4','sdlog']],    # emission system RSL,            Group: RSL systems,
                [DUREE_db.loc['D 7','meanlog'], DUREE_db.loc['D 7','sdlog']],        # ventilation system RSL,         Group: RSL systems   or better: D 7.3 Air central distribution !?
              
             ],
    'dists':  ['unif']*4 + ['triang'] + ['lognorm'] + ['lognorm']*12
    }



#%% Join to one df and feed into model. 

design_params = [scenario_group,label,scenario,original_building_archetype,window_to_wall_ratio_new,add_storeys_new,change_footprint_area_new,add_storeys_extension,\
                insulation_type_renovation,insulation_thickness_renovation,window_type_renovation,interior_renovation_at_intervention,\
                insulation_type_new, insulation_thickness_new, window_type_new,construction_type_new,construction_type_add_storeys,\
                heating_system_overall, has_mechanical_ventilation,\
                heating_system_dhw_sc,heat_emission_system_sc,heat_distribution_system_sc,\
                account_for_biogenic_carbon,account_disposal_emissions_of_existing_building,\
                cooling_system_sc,cold_emission_system_sc,simplifed_LCA,change_orientation,infiltration_volume_flow_ren] #order must be the same!
param_names = ['scenario_group','label','scenario','original_building_archetype','window_to_wall_ratio_new','add_storeys_new','change_footprint_area_new','add_storeys_extension',\
                'insulation_type_renovation','insulation_thickness_renovation','window_type_renovation','interior_renovation_at_intervention',\
                'insulation_type_new', 'insulation_thickness_new', 'window_type_new','construction_type_new','construction_type_add_storeys',\
                'heating_system_overall', 'has_mechanical_ventilation',\
                'heating_system_dhw_sc','heat_emission_system_sc','heat_distribution_system_sc',\
                'account_for_biogenic_carbon','account_disposal_emissions_of_existing_building',\
                'cooling_system_sc','cold_emission_system_sc','simplifed_LCA','change_orientation','infiltration_volume_flow_ren']  #order must be the same!


    
if __name__ == '__main__':    

#%% ONE ASSESSMENT CALL
    if evaluation =='one_scenario':
        #First Part of the Vector: Design Params
        param_values_df = pd.DataFrame(columns=param_names)
        for i, (name, value) in enumerate(zip(param_names, design_params)):
            param_values_df[name] = [value] * N
        #Second Part of the Vector Uncertain Params 
        uncertain_param_values = sample(problem, N)
        #join to one df 
        param_values_df = pd.concat([param_values_df, pd.DataFrame(uncertain_param_values, columns=[problem['names'][i] for i in range(uncertain_param_values.shape[1])])], axis=1)
        
        
        
       # **** Call MODEL ****
        Results = ss.initalize_emtpy_info_df() #Results DF
        log_dfs = []
        max_workers = cpu_count()
        start_time = time.time()
        with Pool(max_workers) as p:
            results = p.starmap(process_params, param_values_df.itertuples(index=False, name=None))
        
        # Unpack results
            # Collect the results
            for log_df in results:
                log_dfs.append(log_df)
        Results_columns = Results.columns
        Results = pd.DataFrame(log_dfs, columns=Results_columns)
        #Results = pd.DataFrame(log_dfs,columns=[Results_columns])
        
        end_time = time.time()
        print('Total Time to Asses the Model: ', end_time-start_time)  
        
    
    
        input_columns = param_values_df.columns
        input_columns_updated = [f'{value}_input' for value in input_columns]
        rename_dict = dict(zip(input_columns, input_columns_updated)) # Create a dictionary for renaming columns
        # Rename the columns in the DataFrame
        param_values_df.rename(columns=rename_dict, inplace=True)
        
        Results = Results.merge(param_values_df,right_index=True, left_index=True,)
        
        #Create automatically a new folder to keep track of the results
        current_datetime = datetime.datetime.now()
        timestamp = current_datetime.strftime("%Y-%m-%d %H.%M.%S")
        export_path = export_path_robust + timestamp + '/'
        if not os.path.exists(export_path):
            os.makedirs(export_path)
        Results.to_csv(f'{export_path}/parametric_results.csv')


#%% MULTIPLE CALL ASSESSMENT (based on excel input)

    if evaluation =='multiple_scenario':
        all_results = pd.DataFrame()
        
        for groups in scenario_group_multi:
            designs = intervention_designs[intervention_designs['scenario_group']==groups] #choose relevant designs (based on scenario_group)
            unique_designs_index = designs.index
            
          
            for design in unique_designs_index: #iterate over all designs
                design_params = gh.multiple_scenario_configurator(intervention_designs, design) #ATTENTION: ensure that the shape is correct!
                #print(design_params)
                #First Part of the Vector: Design Params
                param_values_df = pd.DataFrame(columns=param_names)
                for i, (name, value) in enumerate(zip(param_names, design_params)):
                    param_values_df[name] = [value] * N
                #Second Part of the Vector Uncertain Params 
                uncertain_param_values = sample(problem, N)
                #join input paramter matrix and exogenous parameter matrix to one df 
                param_values_df = pd.concat([param_values_df, pd.DataFrame(uncertain_param_values, columns=[problem['names'][i] for i in range(uncertain_param_values.shape[1])])], axis=1)
                
                
                
               # **** Call MODEL ****
                Results = ss.initalize_emtpy_info_df() #Results DF
                log_dfs = []
                max_workers = cpu_count()
                start_time = time.time()
                with Pool(max_workers) as p:
                    results = p.starmap(process_params, param_values_df.itertuples(index=False, name=None))
                
                # Unpack results
                    # Collect the results
                    for log_df in results:
                        log_dfs.append(log_df)
                Results_columns = Results.columns
                Results = pd.DataFrame(log_dfs, columns=Results_columns)
                #Results = pd.DataFrame(log_dfs,columns=[Results_columns])
                
                end_time = time.time()
                print('Total Time to Asses the Model: ', end_time-start_time)  
    
                input_columns = param_values_df.columns
                input_columns_updated = [f'{value}_input' for value in input_columns]
                rename_dict = dict(zip(input_columns, input_columns_updated)) # Create a dictionary for renaming columns
                # Rename the columns in the DataFrame
                param_values_df.rename(columns=rename_dict, inplace=True)
                
                Results = Results.merge(param_values_df,right_index=True, left_index=True,)
                all_results = pd.concat([all_results, Results], ignore_index=True)
            
        #Create automatically a new folder to keep track of the results
        current_datetime = datetime.datetime.now()
        timestamp = current_datetime.strftime("%Y-%m-%d %H.%M.%S")
        export_path = export_path_robust + timestamp + '_' + scenario_group_multi_exportname + '/'
        if not os.path.exists(export_path):
            os.makedirs(export_path)
        all_results.to_csv(f'{export_path}/parametric_results.csv')



#%% ROBUST ASSESSMENT CALL
    if evaluation == 'robust_assessment':
        R = 10  #if 1 only one evaluation round
        Ns = [2**i for i in [4,5,6,7,8,9,10,11,12]] #,7,8,9,10,11,12,13,14
        sampling_tech = ['sobol','montecarlo']
        
        column_names = ['GWP_mean','GWP_sd','GWP_05th_percentil','GWP_95th_percentil','Qh_mean','Qh_sd','Qh_05th_percentil','Qh_95th_percentil']
        all_column_names = ['r','sample_size']
        for tech in sampling_tech:
            for columns in column_names: 
                all_column_names.append(tech + '_' + columns)
        
        Robustness_uncertainty_results = pd.DataFrame(columns=all_column_names)
        for r in range(R):
            for j,N in enumerate(Ns):
                for tech in sampling_tech:    
                
                
                    #First Part of the Vector: Design Params
                    param_values_df = pd.DataFrame(columns=param_names)
                    for i, (name, value) in enumerate(zip(param_names, design_params)):
                        param_values_df[name] = [value] * N
                    
                    #Second Part of the Vector Uncertain Params 
                    uncertain_param_values = sample(problem, N)
                    
                    #join to one df 
                    param_values_df = pd.concat([param_values_df, pd.DataFrame(uncertain_param_values, columns=[problem['names'][i] for i in range(uncertain_param_values.shape[1])])], axis=1)
                    
                        
                    
                    # CALL MODEL
                    Results = ss.initalize_emtpy_info_df() #Results DF
                    log_dfs = []
                    max_workers = cpu_count()
                    start_time = time.time()
                    with Pool(max_workers) as p:
                        results = p.starmap(process_params, param_values_df.itertuples(index=False, name=None))
                    
                    # Unpack results
                        # Collect the results
                        for log_df in results:
                            log_dfs.append(log_df)
                    Results_columns = Results.columns
                    Results = pd.DataFrame(log_dfs, columns=Results_columns)
                    #Results = pd.DataFrame(log_dfs,columns=[Results_columns])
                    
                    end_time = time.time()
                    print('Total Time to Asses the Model: ', end_time-start_time)  
                    k = r*len(Ns) + j
                    
                    Robustness_uncertainty_results.loc[k,'r'] = r
                    Robustness_uncertainty_results.loc[k,'sample_size'] = N
                    
                    Robustness_uncertainty_results.loc[k,tech + '_' + 'GWP_mean'] = Results['annualized_cummulative_emissions_per_area_total'].mean()
                    Robustness_uncertainty_results.loc[k,tech + '_' + 'GWP_sd'] = Results['annualized_cummulative_emissions_per_area_total'].std()
                    Robustness_uncertainty_results.loc[k,tech + '_' + 'GWP_95th_percentil'] = Results['annualized_cummulative_emissions_per_area_total'].quantile([0.05, 0.95])[0.95]
                    Robustness_uncertainty_results.loc[k,tech + '_' + 'GWP_05th_percentil'] = Results['annualized_cummulative_emissions_per_area_total'].quantile([0.05, 0.95])[0.05]
        
                    Robustness_uncertainty_results.loc[k,tech + '_' + 'Qh_mean'] = Results['annualized_heat_energy_demand_per_area_total'].mean()
                    Robustness_uncertainty_results.loc[k,tech + '_' + 'Qh_sd'] = Results['annualized_heat_energy_demand_per_area_total'].std()
                    Robustness_uncertainty_results.loc[k,tech + '_' + 'Qh_95th_percentil'] = Results['annualized_heat_energy_demand_per_area_total'].quantile([0.05, 0.95])[0.95]
                    Robustness_uncertainty_results.loc[k,tech + '_' + 'Qh_05th_percentil'] = Results['annualized_heat_energy_demand_per_area_total'].quantile([0.05, 0.95])[0.05]
                

        #Create automatically a new folder to keep track of the results
        current_datetime = datetime.datetime.now()
        timestamp = current_datetime.strftime("%Y-%m-%d %H.%M.%S")
        export_path = export_path_UA_robustness + timestamp + '/'
        if not os.path.exists(export_path):
            os.makedirs(export_path)
        Robustness_uncertainty_results.to_csv(f'{export_path}/Robustness_uncertainty_propagation_add_storeys_kanzleistrasse_1.csv')





#%% check uncertain distributions visually

    # labels = problem['names']
    # facecolors = ['lightgrey']* (len(labels)-1)
    # facecolors.append('lemonchiffon')
    
    # fig, ax = fp.create_custom_axes_1()
    
    # #First Plot
    
    # flierprops = dict(marker='d', markerfacecolor='none', markersize=8,
    #                   markeredgecolor=[0.15]*3, markeredgewidth=1.0)
    # medianprops = dict(linestyle='-', linewidth=3, color=[0.05]*3)
    # boxprops =  dict(linestyle='-', linewidth=1, color=[0.05]*3, facecolor = 'grey' )
    # whiskerprops = capprops= dict(linestyle='-', linewidth=1.5, color=[0.05]*3)
    
    # bplot = ax.boxplot(uncertain_param_values, patch_artist=True, flierprops = flierprops,medianprops = medianprops,
    #                       boxprops = boxprops,whiskerprops= whiskerprops,capprops = capprops, widths = 0.45 , showfliers= False,whis=[5, 95]) 
    
    # for patch, color in zip(bplot['boxes'], facecolors):
    #     patch.set_facecolor(color)
    
    # ax.set_xticklabels(labels, rotation=35, ha='right')
    # ax.set_ylabel('Parameter') 
    # ax.set_title('Parameter Distributin after Sampling', loc='left', fontweight='semibold')
    
    
    # ax.set_ylim([0,6])
    # ax.yaxis.set_major_locator(MaxNLocator(nbins=8))
    # ax.text(0 , -2,'The whiskers represent the 5th and 95th percentiles' , ha='left', fontsize=12, fontstyle = 'italic')
    
    # plt.subplots_adjust(bottom=0.33)
    # plt.savefig(f'{export_path_robust}/Parameter_Distributin_after_Sampling-2.pdf')
    # plt.show()
    
#%% Deterministic parametric assessment -> does not work! 
    if evaluation == 'parametric':
        scenario_group = ['deterministic_parametric']
        label = [None]                                         # labeling of the scenario 
        scenario = [1,2,3]                                         # 0= BAU (no intervention) 1=renovation, 2=new construction 3=add stories
        original_building_archetype =  ['30s_Kanzleistrasse',"Garden_city_herrlig", "60s_Salzweg", "60s_Salzweg_ren", "70_s_Lerchenberg"]    #{1:"30s_Kanzleistrasse",2:"Garden_city_herrlig", 3:"60s_Salzweg", 4:"60s_Salzweg_ren", 5:"70_s_Lerchenberg", 6:"eRen4" }
        window_to_wall_ratio_new = [0.2,0.3,0.4]                          # 0.2 to 0.6 reasonable 
        add_storeys_new = [0,1,2,3]                                     # 0,1,2,3,reasonable 
        change_footprint_area_new = [0,0.1,0.2,0.3]                         # 0 - 0.3 reasonable
        add_storeys_extension = [1,2]                              # 1,2 reasonalble 
    
        insulation_type_renovation = ['straw','xps','rockwool','original']  #{1:"original", 2:"straw", 3:"rockwool", 4:"xps"}
        insulation_thickness_renovation = ['8','16','24','32','48','64']                 #{1:'8', 2:'16', 3:'24', 4:'32', 5:'48', 6:'64'}
        window_type_renovation = ["original","window_dbl_1.1_wood_9","window_dbl_1.1_wood_metal_9", "window_trpl_0.6_wood_9", "window_trpl_0.6_wood_metal_9"]                    #{1:"original", 2:"window_dbl_1.1_wood_9", 3:"window_dbl_1.1_wood_metal_9", 4:"window_trpl_0.6_wood_9", 5:"window_trpl_0.6_wood_metal_9"} 
        interior_renovation_at_intervention = [True,False]             #False/True
    
    
        insulation_type_new = ['xps','rockwool','original']                          #{ 2:"straw", 3:"rockwool", 4:"xps"}
        insulation_thickness_new = ['8','16','24','32','48','64']                         #{1:'8', 2:'16', 3:'24', 4:'32', 5:'48', 6:'64'}
        window_type_new = ["window_dbl_1.1_wood_9","window_dbl_1.1_wood_metal_9", "window_trpl_0.6_wood_9", "window_trpl_0.6_wood_metal_9"]               #{2:"window_dbl_1.1_wood_9", 3:"window_dbl_1.1_wood_metal_9", 4:"window_trpl_0.6_wood_9", 5:"window_trpl_0.6_wood_metal_9"} 
        construction_type_new = ['full_concrete_conventional','full_concrete_lowco2',' wood_armature_classical','wood_armature_lowco2','wood_armature_rammed_earth']    #{1:'full_concrete_conventional', 2:'full_concrete_lowco2', 3:' wood_armature_classical', 4:'wood_armature_lowco2', 5:'wood_armature_rammed_earth'}
        construction_type_add_storeys = ['wood_frame_classical','wood_frame_lowco2']  #{1:'wood_frame_classical', 2:'wood_frame_lowco2'}
    
        heating_system_overall = ["ASHP", "GSHP", "district", "electric"]                        #{1:"ASHP", 2:"GSHP", 3:"district", 4:"electric", 5:"Natural Gas"}
        has_mechanical_ventilation = [True,False]                     #False/True
    
    
        #FIX DESIGN PARAMS 1.0
        heating_system_dhw_sc = ['same']                        #other options possible, but does not make sense
        heat_emission_system_sc = ['floor heating' ]              #'floor heating' or 'radiator' 
        heat_distribution_system_sc = ['hydronic']                #other options possible, but does not make sense
    
        account_for_biogenic_carbon = [True ]                     #False/True
        account_disposal_emissions_of_existing_building =[ True]  #False/True
    
        #FIX DESIGN PARAMS 2.0
        cooling_system_sc = ['None']
        cold_emission_system_sc = ['None']
        simplifed_LCA = [False]
        change_orientation = [0]#scales length and width respectifly: X>0 -> N/S increases, X<0 N/S decreases. 0=Same width to length ratio
        infiltration_volume_flow_ren = [0.15]
    
    
        # test = list(itertools.product(scenario_group,label,scenario,original_building_archetype,window_to_wall_ratio_new,add_storeys_new,change_footprint_area_new,add_storeys_extension,\
        #                 insulation_type_renovation,insulation_thickness_renovation,window_type_renovation,interior_renovation_at_intervention,\
        #                 insulation_type_new, insulation_thickness_new, window_type_new,construction_type_new,construction_type_add_storeys,\
        #                 heating_system_overall, has_mechanical_ventilation,\
        #                 heating_system_dhw_sc,heat_emission_system_sc,heat_distribution_system_sc,\
        #                 account_for_biogenic_carbon,account_disposal_emissions_of_existing_building,\
        #                 cooling_system_sc,cold_emission_system_sc,simplifed_LCA,change_orientation,infiltration_volume_flow_ren))
