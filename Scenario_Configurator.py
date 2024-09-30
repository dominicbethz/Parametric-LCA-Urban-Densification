#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 27 18:09:44 2024

@author: dominicbuettiker

Configrurator 
"""


import numpy as np
import pandas as pd
import time
import os
import sys
from random import sample 

main_path = "/Users/dominicbuettiker/Library/CloudStorage/OneDrive-Persönlich/Dominic/ETH/2_Master/4. Semester/Masterarbeit/Code/Model/Parametric_LCA_Master_Thesis/"

sys.path.append(f"{main_path}/SIA_380_1") #Functions directly used from ITA: Energy Calculation 
import data_prep as dp
sys.path.append(main_path) #To import functions form main folder 
import Setup_Simulation as ss
sys.path.append(f"{main_path}/Functions") #To import functions form functions folder
import scenario_configruator_helper as scch 
import general_helper as gh

#%% INPUT DATABASES
input_db = os.path.join(main_path, 'input_data') #path

#configurations = pd.read_excel(f'{input_db}/configurations.xlsx',index_col="Configuration", skiprows=[1]) Not used any more

construction_db = pd.read_excel(f'{input_db}/Construcion_db.xlsx', skiprows=[1],index_col="ID_construction")
construction_db['u_value'].fillna(np.inf, inplace=True) #Replace empty u value columns with ininite, to ensure propere u-value calculation. 
construction_db = construction_db[construction_db.index.notna()]

construction_configurations_db = pd.read_excel(f'{input_db}/envelope_assignement.xlsx', skiprows=[1])

systems_db = pd.read_excel(f'{input_db}/Systems_db_new.xlsx', index_col="ID_system", dtype={'RSL': 'float64'})
systems_db.index = systems_db.index.map(lambda x: 'None' if pd.isna(x) else str(x)) # convert wront nan entry to None

GWP_bio_factors = pd.read_excel(f'{input_db}/GWP_bio_values.xlsx', index_col="Rotation",skiprows=[1])


#Case studeis configuration 
case_study_configurations = pd.read_excel(f'{input_db}/Case_study_for_validation.xlsx','Input_data_casestudy_examples', index_col="Casestudy") 

#%% General Setup

#Merge different componet databases 
construction_db = gh.read_materials(construction_db,f'{input_db}/Case_study_for_validation.xlsx',['mat_composition_old_generic','mat_composition_casestudy_4']) #'Material_composition_casestudy',
construction_db = gh.read_materials(construction_db,f'{input_db}/renovation_construction_db.xlsx',['xps','rockwool','straw','windows','constructions_ag','constructions_bg','constructions_ag_wood','roof','interior_finishings','partitions'])

#Assign GWP_bio, based ond RSL and rotation_time_bio 
RSP = 60 #Default reference service periode building (can be changed later, here important to calculate the GWP_Bio values)
construction_db = gh.assign_gwp_bio_factor(RSP,construction_db,GWP_bio_factors)

#Log File for results
Results = ss.initalize_emtpy_info_df()

"""BASIC CONFIGURATION PARAMETERS (can be overwritten afterwords)"""
regelung,anlagennutzungsgrad_wrg,korrekturfaktor_luftungs_eff_f_v,ventilation_volume_flow,increased_ventilation_volume_flow,area_per_person,\
combustion_efficiency_factor_new,combustion_efficiency_factor_old,window_orientations,height_floors,hohe_uber_meer,gebaeudekategorie_sia,\
heating_setpoint,cooling_setpoint,heat_pump_efficiency,shading_factor_season,RSP, electricity_decarbonization_factor,weatherfile_path, weather_data_sia \
= gh.basic_setup_params(input_db)



#%% Basic input parameters not used anymore

# weatherfile_path = f'{input_db}/weather_data/Zürich-hour_historic.epw'

# epw_labels = ['year', 'month', 'day', 'hour', 'minute', 'datasource', 'drybulb_C', 'dewpoint_C', 'relhum_percent',
#                   'atmos_Pa', 'exthorrad_Whm2', 'extdirrad_Whm2', 'horirsky_Whm2', 'glohorrad_Whm2',
#                   'dirnorrad_Whm2', 'difhorrad_Whm2', 'glohorillum_lux', 'dirnorillum_lux', 'difhorillum_lux',
#                   'zenlum_lux', 'winddir_deg', 'windspd_ms', 'totskycvr_tenths', 'opaqskycvr_tenths', 'visibility_km',
#                   'ceiling_hgt_m', 'presweathobs', 'presweathcodes', 'precip_wtr_mm', 'aerosol_opt_thousandths',
#                   'snowdepth_cm', 'days_last_snow', 'Albedo', 'liq_precip_depth_mm', 'liq_precip_rate_Hour']
# weather_file_dict_headers = {}
# weather_file_dict_bodies = {}
# weather_sia_dict = {}
# unique_weather_paths = [weatherfile_path] #Create here list with all weather files (scenarios)


# for unique_path in unique_weather_paths:
#     weather_file_dict_headers[unique_path] = pd.read_csv(unique_path, header=None, nrows=1)
#     weather_file_dict_bodies[unique_path] = pd.read_csv(unique_path, skiprows=8, header=None, names=epw_labels)
#     weather_sia_dict[unique_path] = dp.epw_to_sia_irrad(weather_file_dict_headers[unique_path],
#                                                         weather_file_dict_bodies[unique_path])

# #Selecthion of the historic scenario for sizing the heating system: zurich Historic
# weather_data_sia = weather_sia_dict[weatherfile_path]



# """Fix Parameters General"""
# regelung = "andere"  # oder "Referenzraum" oder "andere"
# anlagennutzungsgrad_wrg = 0.0  # SIA 380-1 Tab 23  Rückgewinnung Wärme (Lüftung). DEFAULT: 0, keine Wärmerückgewinnung
# korrekturfaktor_luftungs_eff_f_v = 1.0  # zwischen 0.8 und 1.2 gemäss SIA380-1 Tab 24 (Lüftungseffektivität ), DEFAULT: 1, Lüftung ungeregelt/ Fensterlüftung
# ventilation_volume_flow = 0.15 # give a number in m3/(hm2) or select "SIA" to follow SIA380-1 code. ATTENTION: IF SIA: INFILTRATION IS NOT TAKEN INTO ACCOUNT!
# increased_ventilation_volume_flow = 1.5 # give a number in m3/hm2, this volume flow is used when cooling with outside air is possible
# area_per_person = "SIA"  # give a number or select "SIA" to follow the SIA380-1 code (typical for MFH 40)
# combustion_efficiency_factor_new = 1 # To ajust Combustion efficency, if DEFAULT = 1, standart efficency values (in data_prep.py) are used. like 0.88 for gasboiler 
# combustion_efficiency_factor_old = 0.8 #Never used acutally, should be lower than 1, since assuming that the old boilers are not condensing

# #THIS TWO PARAMETERS ARE OVERWRITTEN BY THE CASESTUDIES!
# window_orientations = np.array(["N", "E", "S", "W"], dtype = str) # or np.array(["NE", "SE", "SW", "NW"], dtype = str)
# height_floors = 3 #in meters


# """Fix Parameters Building_Location"""
# hohe_uber_meer = 500 # Eingabe
# gebaeudekategorie_sia = 1.1 #MFH


#%% INPUT PARAMETERS 
"""Exogenous_Parameters_Building"""

heating_setpoint = 20  # number in deC or select "SIA" to follow the SIA380-1 code
cooling_setpoint = 26 
#heat_pump_efficiency = 0.35 #Exergy efficency of Heatpump 
shading_factor_season = np.array([0.8, 0.8, 0.8, 0.8],dtype=float) #from 0 to 1, 1 no shading, Question how to implement!
RSP = 60 #Attention, this is a redefinitino, be aware of chaning, than also change above, for GWP bio 


"""Exogenous_Parameters_Environement"""
#electricity_decarbonization_factor = 0.5 #1 = no change. 1.5= +50%
Year_of_decarbonization = 2050 #In thiy year the electiricty grid is decarbonized, that means it reaches its "physical minimal level of emissions" 
electricity_decarbonization_factor = gh.decarbonization_factor(dp.build_country_yearly_emission_factors('KBOB').mean(),RSP,Year_of_decarbonization,E_min = 0.01 )
GWP_district_min = 0.066*(1/6.5) #KBOB = 0.066 
district_heating_decarbonization_factor = gh.decarbonization_factor(dp.fossil_emission_factors('district', "KBOB", combustion_efficiency_factor_new).mean(),RSP,Year_of_decarbonization,E_min = GWP_district_min)
#electricity_decarbonization_factor = 1
biogenic_carbon_on = True
disposal_emissions_intervention_on = True
simplifed_LCA = False

int_finishings_replacement_at_intervention_ren = False # if False, nor replacement of flooring and wall finishings in case of a renovation at the intervention itselfe
embodied_emissions_decarbonization_fraction = 0.75 #0.75 #if 1, no decarbonization until 2050, choose values between 0 (fully decarbonized) and 1 (no decarbonization)

#anlagennutzungsgrad_wrg = 0.7 #wärme rückgewinnung. Achtung, dieser faktor ist nicht an das lüftungssystem gekoppelt. Wenn mech_fent= False MUSS dieser = 0 gesetzt werden! 


"""EXISTING_BUILDING PARAMETERS"""

#Can be specified manually or imported form excel 
existing_building = '30s_Kanzleistrasse' #eRen4 30s_Kanzleistrasse Garden_city_herrlig 30s_Kanzleistrasse 60s_Salzweg 60s_Salzweg_ren 70_s_Lerchenberg Generic_1 Generic_2 Generic_3
 
"""HERE the casestudy building form eRen is imported"""
infiltration_volume_flow_old,thermal_bridge_add_on_old,height_floors,window_orientations,window_to_wall_ratio_old,floors_ag_old, \
floors_bg_old,width_old,length_old,heated_fraction_ag_old,fraction_partitions_old,\
window_type_old,wall_type_ag_old,roof_type_old,ceiling_to_basement_type_old,\
ceiling_type_old,wall_type_bg_old,slab_basement_type_old,partitions_type_old,tilted_roof_type_old,\
heat_capacity_per_energyreferencearea_old, heating_system_old,heating_system_dhw_old,heat_emission_system_old,heat_distribution_old \
= gh.casestudy_setup(case_study_configurations,existing_building) 


"""SCENARIO PARAMETERS"""

#For the new construction only some fix configurations are made! Infiltratino and thermal birdge add on are constant, since "predictable, because new construction"
#IDEA: For frame constructions: use thermal bridge add on instead of a propper u value calculation: Here can be the question, if it should ony work on the  wall elements and not on windows. 


Intervention_scenario = 1
#Geometry update new construction / add storeys general: 
window_to_wall_ratio_new = 0.3

#Geometry update new constructino  
add_storeys_new = 3
change_footprint_area = 0.0 # 0=no change, enter here a value between 0 and 1 (1 = + 100%)
change_orientation = 0 #scales length and width respectifly: X>0 -> N/S increases, X<0 N/S decreases. 0=Same width to length ratio

#Geometry update addition of storeys 
add_storeys_top_up = 2

#Refurbishment_info
insulation_type_ren = 'original'#'straw'
insulation_thickness_ren = '48'
window_type_ren = 'window_dbl_1.1_wood_9' #window_trpl_0.6_wood_9' #'original' #'window_dbl_1.1_wood_75'  #'original' #'window_dbl_1.1_wood_75' 
thermal_bridge_add_on_ren =  15  #in percent! 
infiltration_volume_flow_ren = 0.3 #Gemäss SIA 380-1 2016 3.5.5 soll 0.15m3/(hm2) verwendet werden

#New_Areas_info 
construction_type_add_storeys =  gh.new_constructions_configurations('wood_frame_lowco2')
construction_type_new = gh.new_constructions_configurations('full_concrete_conventional')
insulation_type_new = 'xps'
insulation_thickness_new = '32'
window_type_new = 'window_dbl_1.1_wood_9' #'window_dbl_1.1_wood_9' #window_trpl_0.6_wood_9
thermal_bridge_add_on_new = 'default'

#System related Parameters 
heating_system_sc = 'ASHP'
heating_system_dhw_sc = 'same'
heat_emission_system_sc = 'floor heating'
heat_distribution_system_sc = 'hydronic' #in the deterministic case, a replacement of the emission an distributino system is = 0.13 kgCO2/m2a
cooling_system_sc = 'None'
cold_emission_system_sc = 'None'
has_mechanical_ventilation_sc = True #True change also a_wrg if true!
anlagennutzungsgrad_wrg = 0.7#0.7 #0.7


"""
KNOWN ERRORS: 
    - in cenario 2 and 3, if system components are 'original'

"""

#%% TEST BUILDING
start_time = time.time()
    

"""Existing Building """

#construction_db = gh.assign_gwp_bio_factor(RSP,construction_db,GWP_bio_factors)


#Geometry & Envelop definition
Building = ss.Scenario(
            window_orientations, 
            height_floors,
            window_to_wall_ratio_old, 
            floors_ag_old, 
            floors_bg_old, 
            width_old,  # walls_N_S
            length_old, # walls_W_E
            heated_fraction_ag_old, 
            wall_type_ag_old,
            wall_type_bg_old,
            window_type_old, 
            ceiling_type_old,
            slab_basement_type_old, 
            ceiling_to_basement_type_old, 
            roof_type_old, 
            heat_capacity_per_energyreferencearea_old,
            infiltration_volume_flow_old,
            thermal_bridge_add_on_old,
            partitions_type_old,
            fraction_partitions_old, 
            tilted_roof_type_old,
            existing_building
            )
#System Definition
Building.system_properties_old(heating_system_old, heating_system_dhw_old, 
                                    heat_emission_system_old, heat_distribution_old)
#Run geometry & uvalue calcualtions
Building.calc_geometry_properties_old()
Building.calc_uvalues_old(construction_db)

# Todo: Calculate E-Demand of original building once + capacites of the system and store it seperatly "for the demoliton calculations." 

"""
DEFINE SCENARIO 

"""
scch.intervention_scenario (     Building, 
                                 Intervention_scenario, 
                                 construction_db,
                                 construction_configurations_db,
                                 simplifed_LCA,
                                 
                                 #Geometry info new construction/add storeys general 
                                 window_to_wall_ratio_new,
        
                                 #Geometry info new construction
                                 add_storeys_new,
                                 change_footprint_area,
                                 change_orientation, #scales length and width respectifly: e.g. more N/S  or E/W facades. 0 -> no scaling!
                                
                                 #Geometry update addition of storeys 
                                 add_storeys_top_up,
                                 
                                 #Refurbishment_info
                                 insulation_type_ren,
                                 insulation_thickness_ren,
                                 window_type_ren,
                                 thermal_bridge_add_on_ren,
                                 infiltration_volume_flow_ren,
                                 
                                 #New_Areas_info 
                                 construction_type_add_storeys,
                                 construction_type_new,
                                 insulation_type_new,
                                 insulation_thickness_new,
                                 window_type_new,
                                 thermal_bridge_add_on_new,
                                 
                                 #System related Parameters 
                                 heating_system_sc,
                                 heating_system_dhw_sc,
                                 heat_emission_system_sc,
                                 heat_distribution_system_sc,
                                 cooling_system_sc,
                                 cold_emission_system_sc,
                                 has_mechanical_ventilation_sc,
                                 int_finishings_replacement_at_intervention_ren
                                 )

"""Genreral_Simulation_Setup"""
Building.basic_simulation_setup(construction_db,systems_db,regelung,anlagennutzungsgrad_wrg, korrekturfaktor_luftungs_eff_f_v, ventilation_volume_flow, increased_ventilation_volume_flow, area_per_person,combustion_efficiency_factor_new,combustion_efficiency_factor_old)
Building.specific_simulation_setup(weatherfile_path,weather_data_sia,hohe_uber_meer, gebaeudekategorie_sia, heating_setpoint, cooling_setpoint, heat_pump_efficiency,shading_factor_season,RSP,electricity_decarbonization_factor,
                                   biogenic_carbon_on,disposal_emissions_intervention_on,simplifed_LCA,int_finishings_replacement_at_intervention_ren, embodied_emissions_decarbonization_fraction,
                                   district_heating_decarbonization_factor)

mid_time = time.time()
"""Call Simulation Based on scenario"""
scch.call_simulations(Building,Intervention_scenario)

"""Store Simulation Results"""
Results.loc[len(Results.index)] = Building.get_info_to_df()


end_time = time.time()
print('simulation_time_one_iteration',end_time-start_time )
#print('setup_time_one_iteration',mid_time-start_time )
print('annualized_cummulative_emissions_per_area_total: ',  Results['annualized_cummulative_emissions_per_area_total'][0])
print('annualized_embodied_emissions_per_area_total: ',  Results['annualized_embodied_emissions_per_area_total'][0])
print('annualized_heat_energy_demand_per_area_total: ',  Results['annualized_heat_energy_demand_per_area_total'][0])
#%%

"""IDEA: hand over the database always for this main fiel: so unique entries of the database can be modified in a robust optmizaion or a SA. """





