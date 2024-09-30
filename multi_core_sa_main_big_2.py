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



from SALib.sample import saltelli
from SALib.sample.sobol import sample
from SALib.analyze.sobol import analyze
#import SALib
import sys
import os
import time
import datetime

from multiprocessing import Pool, cpu_count


main_path = "/Users/dominicbuettiker/Library/CloudStorage/OneDrive-Persönlich/Dominic/ETH/2_Master/4. Semester/Masterarbeit/Code/Model/Parametric_LCA_Master_Thesis/"
export_path_SA = "/Users/dominicbuettiker/Library/CloudStorage/OneDrive-Persönlich/Dominic/ETH/2_Master/4. Semester/Masterarbeit/Code/Model/Parametric_LCA_Master_Thesis/Results/SA_Archetypes/"
export_path_SA_Rb = "/Users/dominicbuettiker/Library/CloudStorage/OneDrive-Persönlich/Dominic/ETH/2_Master/4. Semester/Masterarbeit/Code/Model/Parametric_LCA_Master_Thesis/Results/robustness_SA/"


input_db = os.path.join(main_path, 'input_data') #path
DUREE_db = pd.read_excel(f'{input_db}/duree_db.xlsx', 'Data', skiprows=[0],index_col="Code")


sys.path.append(main_path) #To import functions form main folder 
import Setup_Simulation as ss
from multi_core_sa_model_big_2 import process_params_big

#%% IMPORTANT: whole pice must be run at one. 

Results = ss.initalize_emtpy_info_df() #Results DF



if __name__ == '__main__':

#important: all other parameters are fix given in the multi_core_sa_model, check it there! 
    problem_1 = {
        'num_vars':38, #38, 37
        'names':['scenario','original building archetype','window to wall ratio new', 
                 'add storeys new','change footprint area new',
                 'add storeys extension',
                 'insulation type renovation', 'insulation thickness renovation', 'window type renovation','interior renovation at intervention',
                 'insulation type new', 'insulation thickness new', 'window type new','construction type new','construction type add storeys', 
                 'heating system overall','has mechanical ventilation',
                 'thermal bridge add on renovation', 'thermal bridge add on new',
                 'ventilation volume flow','heating setpoint', 
                 'grid decarbonization factor','material decarbonization factor',
                 'windows RSL','insulation RSL','flat roof covering RSL','tilted roof covering RSL', 'facade ventilated finishing RSL','facade plasterd finishing RSL',
                 'internal covering wall RSL','internal flooring RSL',
                 'conversion RSL (heating system)','distribution RSL (hydronic)',' emission system RSL','ventilation system RSL',
                 'account for biogenic carbon','account disposal emissions of existing building','RSP Building'
                 ], 
                                          
                                                
        'groups': ['scenario','original building archetype','window to wall ratio new',
                   'geometry new construction','geometry new construction',
                   'geometry new construction',
                   'insulation type','insulation thickness','window type','interior renovation at intervention',
                   'insulation type','insulation thickness','window type','construction type','construction type',
                   'heating system','mechanical ventilation',
                   'thermal bridge add on','thermal bridge add on',
                   'ventilation volume flow','heating setpoint',
                   'grid decarbonization factor','material decarbonization factor',
                   'RSL envelope','RSL envelope','RSL envelope','RSL envelope','RSL envelope','RSL envelope',
                   'RSL interior finishings','RSL interior finishings',
                   'RSL systems','RSL systems','RSL systems','RSL systems',
                   'LCA methodics','LCA methodics','RSP Building'

                  ],
        
        'bounds':[  [0.5, 3.5], #scenario:                     Group: scenario,  0= BAU (no intervention) 1=renovation, 2=new construction 3=add stories
                    [0.5, 5.5], #original building archetype   Group: original building archetype,  {1:"30s_Kanzleistrasse",2:"Garden_city_herrlig", 3:"60s_Salzweg", 4:"60s_Salzweg_ren", 5:"70_s_Lerchenberg", 6:"eRen4" }
                    [0.2, 0.6], #window_to_wall_ratio_new,     Group: window to wall ratio new
                    
                    #geometry new params
                    [-0.5, 3.5], #add_storeys_new,              Group: geometry new construction,   0, 1, 2, 3
                    [0.0, 0.3],  #change footprint area,        Group: geometry new construction,   0-30%
                    #geometry add storeys
                    [0.5, 2.5],  # add_storeys_top_up,          Group: geometry new construction,       1, 2
                    
                    # Construction params ren
                    [0.5, 4.5],  # insulation_type_ren,         Group: insulation type,             {1:"original", 2:"straw", 3:"rockwool", 4:"xps"}
                    [0.5, 6.5],  # insulation_thickness_ren,    Group: insulation thickness,        {1:'8', 2:'16', 3:'24', 4:'32', 5:'48', 6:'64'}
                    [0.5, 5.5],  # window_type_ren,             Group: window type,                 {1:"original", 2:"window_dbl_1.1_wood_metal_75", 3:"window_trpl_0.6_wood_metal_75", 4:"window_dbl_1.1_wood_75", 5:"window_trpl_0.6_wood_75"}
                    [0.0, 1.0],  # int_finishings_replacement_at_interventionren true/false  Group: interior renovation at intervention  
                
                    # Construction params new
                    [1.5, 4.5],  # insulation_type_new,         Group: insulation type,              {2:"straw", 3:"rockwool", 4:"xps"}
                    [0.5, 6.5],  # insulation_thickness_new,    Group: insulation thickness,        {1:'8', 2:'16', 3:'24', 4:'32', 5:'48', 6:'64'}
                    [1.5, 5.5],  # window_type_new,             Group: window type,                 {1:"original", 2:"window_dbl_1.1_wood_9", 3:"window_dbl_1.1_wood_metal_9", 4:"window_trpl_0.6_wood_9", 5:"window_trpl_0.6_wood_metal_9"} 
                    [0.5, 5.5],  # construction type new,       Group: construction type            {1:'full_concrete_conventional', 2:'full_concrete_lowco2', 3:' wood_armature_classical', 4:'wood_armature_lowco2', 5:'wood_armature_rammed_earth'}
                    [0.5, 2.5],  # construction_type_add_storeys,Group: construction type,          {1:'wood_frame_classical', 2:'wood_frame_lowco2'}
                    
                    #System Params (overall)
                    [0.5, 5.5],  # heating_system_sc            Group: heating system               {1:"ASHP", 2:"GSHP", 3:"district", 4:"electric", 5:"Natural Gas"}
                    [0.0, 1.0],  #has mechanical ventialtion    Group: mechanical ventilation       True/False
                    
                    #Exogenous params 
                    [0.0, 30.0],  # thermal_bridge_add_on_ren,      Group: thermal bridge add on    acc. xxx 15% in mean
                    [0.0, 30.0],  # thermal_bridge_add_on_new,      Group: thermal bridge add on    acc. xxx 15% in mean
                    
                    [0.7, 1.0],   # ventialtion volume flow         Group: ventilation rate         acc. SIA 2021_2024 -> 0.8. Distribution unif. from Galimshina et.al. 2020 
                    [18, 23],     # heating_setpoint,               Group: heating setpoint
                    
                    [0.5,5.5], #[0.5,5.5,0.25],  # [0.5,5.5] , # #grid_decarbonization_factor,     Group: Grid decarbonization factor,  Grid decarbonized until 2040, 2050, 2060, 2070, 2080, distribution triangualr: with peak at 2050
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
                    
                    
                    #Methodical params
                    [0.0,1.0],    # biogenic carbon on / off,      Group: methodics
                    [0.0,1.0],    # disposal emissions on / off,   Group: methodics
                    [DUREE_db.loc['C','meanlog'], DUREE_db.loc['C','sdlog']]            #[59.9,60.0] # # RSP Building                    Group: RSP Building
                    ],
        
        'dists':    ['unif']*21 + ['unif'] + ['lognorm'] + ['lognorm']*12 + ['unif']*2  + ['lognorm'] # ['unif']  ['triang']
                     }
        #log changes:  base config, widespread elegrid 


# #   robustness Analysis   
#     groups_series = pd.Series( problem_1['groups'])
#     unique_groups = groups_series.unique()
#     robustness_results = pd.DataFrame(index=unique_groups)
    
#     Ns = [2**6,2**7,2**8,2**9,2**10,2**11,2**12,2**13]
#     for i in Ns: 
#         Results = ss.initalize_emtpy_info_df() #Results DF
# #
#         N = i #2048
                  
#######   
    N = 2048 #2048 512
    param_values = sample(problem_1, N)
    
    Y_1 = np.zeros([param_values.shape[0]]) #TOTAL EMISSIONS
    Z_1 = np.zeros([param_values.shape[0]]) #HEATING ENERGY DEMAND 
    
    log_dfs = []
    max_workers = cpu_count()
    start_time = time.time()
    with Pool(max_workers) as p:
        results = p.map(process_params_big, param_values)

    # Unpack results
        for i, (total_cummulative_emissions, heating_energy_demand,log_df ) in enumerate(results):
            Y_1[i] = total_cummulative_emissions
            Z_1[i] = heating_energy_demand
            log_dfs.append(log_df)
            #Results.loc[len(Results.index)] = log_df
    #Results = pd.concat(log_dfs, ignore_index=True)
    Results_columns = Results.columns
    Results = pd.DataFrame(log_dfs,columns=[Results_columns])
    
    end_time = time.time()
    print('Total Time to Asses the Model: ', end_time-start_time)  
    
    #Create automatically a new folder to keep track of the results
    current_datetime = datetime.datetime.now()
    timestamp = current_datetime.strftime("%Y-%m-%d %H.%M.%S")
    export_path = export_path_SA + timestamp + '/'
    if not os.path.exists(export_path):
        os.makedirs(export_path)
    #np.savetxt(f'{export_path}/param_values.csv', param_values, delimiter=',', fmt='%s')
    #np.savetxt(f'{export_path}/Y_1.csv', Y_1, delimiter=',', fmt='%s')
    #np.savetxt(f'{export_path}/Z_1.csv', Z_1, delimiter=',', fmt='%s')
    Results.to_csv(f'{export_path}/parametric_results.csv')
    
# # Robustness Anaylsis       
#         Si_1 = analyze(problem_1, Y_1, parallel=True)  #Total emissions
#         ST_indices_results = Si_1.to_df()[0]
#         ST_indices_results['rank'] = ST_indices_results['ST'].rank(method='max')
#         ST_indices_results =  ST_indices_results[['ST', 'rank']]
#         ST_indices_results = ST_indices_results.rename(columns={'rank':'rank_N_'+str(N),'ST':'ST_N_'+str(N)}) #
#         robustness_results = robustness_results.merge(ST_indices_results, left_index = True, right_index = True)
#     current_datetime = datetime.datetime.now()
#     timestamp = current_datetime.strftime("%Y-%m-%d %H.%M.%S")
#     robustness_results.to_csv(f'{export_path_SA_Rb}/Robustness_SA_{timestamp}.csv')
# #           
 
##################### 
    

#%% SOBOL ANALYSIS This cell must be run with selecting the funtion 

    Si_1 = analyze(problem_1, Y_1, parallel=True)  #Total emissions
    Si_2 =  analyze(problem_1, Z_1, parallel=True) #Heating energy demand 
    #save sobol indices as csv
    Si_1.to_df()[0].to_csv(f'{export_path}/ST_sobol_indices_total_emissions.csv')
    Si_1.to_df()[1].to_csv(f'{export_path}/S1_sobol_indices_total_emissions.csv')
    Si_1.to_df()[2].to_csv(f'{export_path}/S2_sobol_indices_total_emissions.csv')
    Si_2.to_df()[0].to_csv(f'{export_path}/ST_sobol_indices_heating_energy_demand.csv')
    Si_2.to_df()[1].to_csv(f'{export_path}/S1_sobol_indices_heating_energy_demand.csv')
    Si_2.to_df()[2].to_csv(f'{export_path}/S2_sobol_indices_heating_energy_demand.csv')
    

#%%
    

    def create_custom_axes():
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Set general settings
    
        ax.yaxis.grid(True, linestyle='dashed', linewidth = 1, color = 'black', alpha = 0.5)
        ax.set_axisbelow(True)
        ax.axes.linewidth = 1.5
        ax.tick_params(axis='both', which='both', width=1.5, length = 5)
        plt.rcParams['font.size'] = 12
        plt.grid(which='major', axis='y', zorder=-1.0)
        #plt.rcParams['font.family'] = 'OCR-B'
        
        
        return fig, ax
    
    #Create colors 
    num_bins = 6 
    colors = plt.cm.cividis.colors#[::-1]
    color_intervals = [colors[int(i * (len(colors) - 1) / (num_bins - 1))] for i in range(num_bins)] 
    
    """INPUT: which assessment and wich params are fix"""
    comment = '1st assessment' # fix parameter:\nscenario = renovation, insulatino type = straw,\nLCA simplified = False, heating system = ASHP' #insulatino type = straw \nconstructino type new = wood_armature_lowco2'
    fig, ax = create_custom_axes()
    
    #define x-axies
    if 'groups' in problem_1:
        groups_list = problem_1['groups']
        groups_series = pd.Series(groups_list)
        unique_groups = groups_series.unique()
        x_values = unique_groups
    else: 
        x_values = problem_1['names'] 
   
    x = np.arange(len(x_values))
    # Define the width of the bars
    width = 0.4
    
    # Plot the first set of bars shifted to the left by half the width
    ax.bar(x - width/2, Si_1['ST'], color=color_intervals[1], edgecolor='#232323ff', linewidth=0.8, width=width, align='center', label='ST total cummulative emissions') #'#bca300ff'
    
    # Plot the second set of bars shifted to the right by half the width
    ax.bar(x + width/2, Si_2['ST'], color=color_intervals[4], edgecolor='#232323ff', linewidth=0.8, width=width, align='center', label='ST heating energy demand') #'#7d7bfcff'

    # Set the x-label, y-label, and title
    ax.set_ylabel("Sobol coefficient ST", fontweight='bold' )
    ax.set_title("Global Sensitivity Analysis for Cummulative GHG Emissions and Heating Energy Demand, N =  " +  str(N),fontweight='bold') 
    ax.set_xlabel("Grouped input paramter"  , fontweight='bold')
    ax.set_xticks(x) 
    # Set the tick labels
    ax.set_xticklabels(x_values, rotation=30, ha='right') 
    legend = ax.legend(loc='upper right', ncol=1)
    legend.get_frame().set_edgecolor('none')  # Remove the frame edge
    legend.get_frame().set_facecolor('white') # Set the background color to white
    legend.get_frame().set_alpha(1.0)  
    
    ax.text( 19,-0.15, comment , ha='right', style='italic')

    #plt.subplots_adjust(bottom=0.22)
    plt.subplots_adjust(bottom=0.25)
    plt.savefig(f'{export_path}/Sobol_coefficients_ST_eREN4_overall.pdf')
    plt.show()

