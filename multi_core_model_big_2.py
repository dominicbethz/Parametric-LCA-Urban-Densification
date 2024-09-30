#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 14:15:26 2024

@author: dominicbuettiker
"""

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
from multiprocessing import Pool

#
main_path = "/Users/dominicbuettiker/Library/CloudStorage/OneDrive-Persönlich/Dominic/ETH/2_Master/4. Semester/Masterarbeit/Code/Model/Parametric_LCA_Master_Thesis/"
export_path_SA = "/Users/dominicbuettiker/Library/CloudStorage/OneDrive-Persönlich/Dominic/ETH/2_Master/4. Semester/Masterarbeit/Code/Model/Parametric_LCA_Master_Thesis/Results/"

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

construction_configurations_db = pd.read_excel(f'{input_db}/envelope_assignement.xlsx', skiprows=[1]) #Database of all possible configurations

systems_db = pd.read_excel(f'{input_db}/Systems_db_new.xlsx', index_col="ID_system", dtype={'RSL': 'float64'})
systems_db.index = systems_db.index.map(lambda x: 'None' if pd.isna(x) else str(x)) # convert wront nan entry to None


GWP_bio_factors = pd.read_excel(f'{input_db}/GWP_bio_values.xlsx', index_col="Rotation",skiprows=[1])

#Case studeis configuration 
case_study_configurations = pd.read_excel(f'{input_db}/Case_study_for_validation.xlsx','Input_data_casestudy_examples', index_col="Casestudy") 

#%% General Setup

"""BASIC CONFIGURATION PARAMETERS (can be overwritten afterwords, e.g in evaluate model )"""
regelung,anlagennutzungsgrad_wrg,korrekturfaktor_luftungs_eff_f_v,ventilation_volume_flow,increased_ventilation_volume_flow,area_per_person,\
combustion_efficiency_factor_new,combustion_efficiency_factor_old,window_orientations,height_floors,hohe_uber_meer,gebaeudekategorie_sia,\
heating_setpoint,cooling_setpoint,heat_pump_efficiency,shading_factor_season,RSP, electricity_decarbonization_factor,weatherfile_path, weather_data_sia \
= gh.basic_setup_params(input_db)


#Merge different componet databases 
construction_db = gh.read_materials(construction_db,f'{input_db}/Case_study_for_validation.xlsx',['mat_composition_casestudy_4','mat_composition_old_generic'])
construction_db = gh.read_materials(construction_db,f'{input_db}/renovation_construction_db.xlsx',
                                    ['xps','rockwool','straw','windows','constructions_ag','constructions_bg','constructions_ag_wood','roof','interior_finishings','partitions'])

#Assign GWP_bio, based ond RSL and rotation_time_bio (are overwriten afterwords) 
construction_db = gh.assign_gwp_bio_factor(RSP,construction_db,GWP_bio_factors)

#Log File for results
Results = ss.initalize_emtpy_info_df()

#%% Building specific setup

"""EXISTING_BUILDING PARAMETERS"""

"""HERE the casestudy building form eRen is imported""" #in SA included!
# infiltration_volume_flow_old,thermal_bridge_add_on_old,height_floors,window_orientations,window_to_wall_ratio_old,floors_ag_old, \
# floors_bg_old,width_old,length_old,heated_fraction_ag_old,fraction_partitions_old,\
# window_type_old,wall_type_ag_old,roof_type_old,ceiling_to_basement_type_old,\
# ceiling_type_old,wall_type_bg_old,slab_basement_type_old,partitions_type_old,tilted_roof_type_old,\
# heat_capacity_per_energyreferencearea_old, heating_system_old,heating_system_dhw_old,heat_emission_system_old,heat_distribution_old \
# = gh.casestudy_setup(case_study_configurations,'eRen4')

"""SCENARIO PARAMETERS (can be overwritten invaluate model)"""


# Intervention_scenario = 1

#Geometry info
# add_stories = 1
# change_footprint_area = 0.0 # 0=no change, enter here a value between 0 and 1 (1 = + 100%)
# change_orientation = 0 #scales length and width respectifly: X>0 -> N/S increases, X<0 N/S decreases. 0=Same width to length ratio
# window_to_wall_ratio_new = 0.5

#Refurbishment_info
# insulation_type_ren = 'xps'
# insulation_thickness_ren = '32'
# window_type_ren = 'original' #'window_trpl_0.6'
# thermal_bridge_add_on_ren =  20  #in percent! 
# infiltration_volume_flow_ren = 0.15

#New_Areas_info 
# construction_type_new = construction_type_new_test 
# insulation_type_new = 'xps'
# insulation_thickness_new = '24'
# window_type_new = 'window_trpl_0.6_wood_metal_75'
#thermal_bridge_add_on_new = 'default' # if default is used, the value of the construction dict is used. 

#System related Parameters 
# heating_system_sc = 'GSHP'
# heating_system_dhw_sc = 'same'
# heat_emission_system_sc = 'floor heating'
# heat_distribution_system_sc = 'hydronic'
# cooling_system_sc = 'None'
# cold_emission_system_sc = 'None'
# has_mechanical_ventilation_sc = False


# biogenic_carbon_on = True
# disposal_emissions_intervention_on = True 
# simplifed_LCA = False         

# int_finishings_replacement_at_intervention_ren = True # if False, nor replacement of flooring and wall finishings in case of a renovation at the intervention itselfe
# embodied_emissions_decarbonization_fraction = 1 #if 1, no decarbonization unti 2050



""" Here begins the model used in the Senstivity Analysis! Alle not used Prameters form above are overwritten!"""

def evaluate_model(*X):
    
    [scenario_group,label,scenario,original_building_archetype,window_to_wall_ratio_new,add_storeys_new,change_footprint_area_new,add_storeys_extension,\
                   insulation_type_renovation,insulation_thickness_renovation,window_type_renovation,interior_renovation_at_intervention,\
                   insulation_type_new, insulation_thickness_new, window_type_new,construction_type_new,construction_type_add_storeys,\
                   heating_system_overall, has_mechanical_ventilation,\
                   heating_system_dhw_sc,heat_emission_system_sc,heat_distribution_system_sc,\
                   account_for_biogenic_carbon,account_disposal_emissions_of_existing_building,\
                   cooling_system_sc,cold_emission_system_sc,simplifed_LCA,change_orientation,infiltration_volume_flow_ren,\
                       
                   thermal_bridge_add_on_ren,thermal_bridge_add_on_new,\
                   ventilation_volume_flow,heating_setpoint,\
                   electricity_decarbonization_factor_helper,embodied_emissions_decarbonization_fraction,\
                   windows_RSL,insulation_RSL,flat_roof_covering_RSL,sloping_roof_covering_RSL, facade_ventilated_finishing_RSL,facade_plasterd_finishing_RSL,\
                   internal_covering_wall_RSL,internal_flooring_RSL,\
                   conversion_RSL_heating_system , distribution_RSL_hydronic, emission_system_RSL, ventilation_system_RSL] = X
    
    #print(X)
    
    
    """SETUP PARAMETERS FORM SAMPLING ACCORDING TO NAMING"""
    
    #IDEAL CONCEPT: linear decrease to 10g GWP/ kWh, according to according to  Zappa et. al. 2018, Is a 100% renewable European power system feasible by 2050
    number_to_electricity_decarbonization_factor = {1:[2040,0.032], #0.01
                                                    2:[2050,0.032],
                                                    3:[2060,0.032],
                                                    4:[2070,0.032],
                                                    5:[2080,0.032],}
    
    #SPREAD IN LITERATURE 
    # number_to_electricity_decarbonization_factor = {1:[2050,0.004], #plessman et al 2016 Tech max. feasable. 
    #                                                 2:[2050,0.01],  #Zappa et. al. 2018
    #                                                 3:[2050,0.080],  #Alina Best Winter 90, summer 60, weighting 2/3 winter, 1/3 summer 
    #                                                 4:[2050,0.131],  #Alina Worst Winter 130, summer 60, weighting 2/3 winter, 1/3 summer 
    #                                                 5:[2050,0.184],} #Rüdisüli et al 2022, Worst case scenario 
    
    
    """Set variable parameters"""
    
    RSP = 60 
    Intervention_scenario = scenario  #1=renovation, 2=new construction 3=add stories #0 
    
    #Old Building (Based on configuration in excel)
    existing_building = original_building_archetype
    
    infiltration_volume_flow_old,thermal_bridge_add_on_old,height_floors,window_orientations,window_to_wall_ratio_old,floors_ag_old, \
    floors_bg_old,width_old,length_old,heated_fraction_ag_old,fraction_partitions_old,\
    window_type_old,wall_type_ag_old,roof_type_old,ceiling_to_basement_type_old,\
    ceiling_type_old,wall_type_bg_old,slab_basement_type_old,partitions_type_old,tilted_roof_type_old,\
    heat_capacity_per_energyreferencearea_old, heating_system_old,heating_system_dhw_old,heat_emission_system_old,heat_distribution_old \
    = gh.casestudy_setup(case_study_configurations,existing_building)

    #geometry new params
    window_to_wall_ratio_new = window_to_wall_ratio_new
    add_storeys_new =  add_storeys_new #add stories for replacement constructino 0,1,2,3
    change_footprint_area = change_footprint_area_new
    #geometry add storeys
    add_storeys_top_up =  add_storeys_extension
    
    # Construction params ren
    insulation_type_ren = insulation_type_renovation
    insulation_thickness_ren = insulation_thickness_renovation
    window_type_ren = window_type_renovation
    int_finishings_replacement_at_intervention_ren = interior_renovation_at_intervention
    
    
    # Construction params new
    insulation_type_new = insulation_type_new
    insulation_thickness_new = insulation_thickness_new
    window_type_new = window_type_new
    # consturction types new
    construction_type_new_name = construction_type_new
    construction_type_new =  gh.new_constructions_configurations(construction_type_new_name)
    
    construction_type_add_storeys_name = construction_type_add_storeys
    construction_type_add_storeys = gh.new_constructions_configurations(construction_type_add_storeys_name)
    
    #System Params (overall) --------------------------------------
    heating_system_sc = heating_system_overall
    has_mechanical_ventilation_sc = has_mechanical_ventilation
    anlagennutzungsgrad_wrg = 0
    if has_mechanical_ventilation_sc:
        anlagennutzungsgrad_wrg = 0.7
        
    heating_system_dhw_sc = heating_system_dhw_sc
    heat_emission_system_sc = heat_emission_system_sc
    heat_distribution_system_sc = heat_distribution_system_sc
    cooling_system_sc = cooling_system_sc
    cold_emission_system_sc = cold_emission_system_sc  

    #Methodical params and other params
    biogenic_carbon_on = account_for_biogenic_carbon
    disposal_emissions_intervention_on = account_disposal_emissions_of_existing_building
    simplifed_LCA = simplifed_LCA
    change_orientation = change_orientation
    infiltration_volume_flow_ren = infiltration_volume_flow_ren
    
    #Exogenous params ---------------------------------------------

    thermal_bridge_add_on_ren = thermal_bridge_add_on_ren
    thermal_bridge_add_on_new = thermal_bridge_add_on_new
    
    ventilation_volume_flow = ventilation_volume_flow
    heating_setpoint = heating_setpoint
    
    # Grid decarbonization: electricity and district. 
    electricity_decarbonization_factor_helper =  np.round(electricity_decarbonization_factor_helper,0)
    Year_of_decarbonization = number_to_electricity_decarbonization_factor[electricity_decarbonization_factor_helper][0]
    GWP_ele_min = number_to_electricity_decarbonization_factor[electricity_decarbonization_factor_helper][1]
    #GWP_ele_min = 0.01 #according to  Zappa et. al. 2018, Is a 100% renewable European power system feasible by 2050?
    electricity_decarbonization_factor =  gh.decarbonization_factor(dp.build_country_yearly_emission_factors('KBOB').mean(),RSP,Year_of_decarbonization, E_min = GWP_ele_min)
    
    
    GWP_distric_reduction_factor = 2 #Since a distric network has more losses it is assumed, that only 1/2 of the decarbonizatino of the district happens, further this factor also taking into account the mismatch of the heat supply temperatures.
    GWP_district_min = (GWP_ele_min/dp.build_country_yearly_emission_factors('KBOB').mean()) *  0.0666 * GWP_distric_reduction_factor  #Assumptino same decarbonizatino like elecricity grid
    district_heating_decarbonization_factor = gh.decarbonization_factor(dp.fossil_emission_factors('district', "KBOB", combustion_efficiency_factor_new).mean(),RSP,Year_of_decarbonization,E_min = GWP_district_min)
    
    # embodied emissions decarbonization 
    embodied_emissions_decarbonization_fraction = embodied_emissions_decarbonization_fraction
    
    #uncertainty in RSL of construction elements to the exterior -------------------------------------
    
    construction_db_RSL = construction_db.copy()
    construction_db_RSL = gh.change_RSL_construction('window', windows_RSL, construction_db_RSL)
    construction_db_RSL = gh.change_RSL_construction('insulation', insulation_RSL, construction_db_RSL)
    construction_db_RSL = gh.change_RSL_construction('flat_roof_ext_surface', flat_roof_covering_RSL, construction_db_RSL)
    construction_db_RSL = gh.change_RSL_construction('tilted_roof_exterior', sloping_roof_covering_RSL, construction_db_RSL)
    construction_db_RSL = gh.change_RSL_construction('facade_ventilated', facade_ventilated_finishing_RSL, construction_db_RSL)
    construction_db_RSL = gh.change_RSL_construction('facade_plasterd', facade_plasterd_finishing_RSL, construction_db_RSL)
    #uncertainty in RSL of construction elements to the interior 
    construction_db_RSL = gh.change_RSL_construction('int_finishing', internal_covering_wall_RSL, construction_db_RSL)
    construction_db_RSL = gh.change_RSL_construction('int_flooring', internal_flooring_RSL, construction_db_RSL)
    
    #Dynamic calculation of construction db (based on uncertainties) -> GWP bio factors need to be reassigned based on RSL!
    construction_db_RSL = gh.assign_gwp_bio_factor(RSP,construction_db_RSL,GWP_bio_factors)
   
    #uncertainty of RSL systems: 
    systems_db_RSL = systems_db.copy()
    systems_db_RSL = gh.change_RSL_system('Conversion', conversion_RSL_heating_system, systems_db_RSL)
    systems_db_RSL = gh.change_RSL_system('Distribution', distribution_RSL_hydronic, systems_db_RSL)
    systems_db_RSL = gh.change_RSL_system('Emission', emission_system_RSL, systems_db_RSL)
    systems_db_RSL = gh.change_RSL_system('Ventilation', ventilation_system_RSL, systems_db_RSL)
    
    
  

    
    """START SIMULATION """
    
    """Existing Building """
    #Geometry & Envelop definition
    Building = ss.Scenario(
                window_orientations, 
                height_floors,
                window_to_wall_ratio_old, 
                floors_ag_old, 
                floors_bg_old, 
                width_old, # walls_N_S
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
    #System Definition existing Building 
    Building.system_properties_old(heating_system_old, heating_system_dhw_old, 
                                        heat_emission_system_old, heat_distribution_old)
    #Run geometry & uvalue calcualtions existing building 
    Building.calc_geometry_properties_old()
    Building.calc_uvalues_old(construction_db_RSL)
    # TODO: Calculate E-Demand of original building once + capacites of the system and store it seperatly "for the demoliton calculations." 
    
    """
    DEFINE SCENARIO 
    
    """
    scch.intervention_scenario (    Building, 
                                    Intervention_scenario, 
                                    construction_db,
                                    construction_configurations_db,
                                    simplifed_LCA,
                                    
                                    #Geometry info new construction/add storeys general 
                                    window_to_wall_ratio_new,
           
                                    #Geometry info new construction
                                    add_storeys_new,
                                    change_footprint_area,
                                    change_orientation,  #scales length and width respectifly: e.g. more N/S  or E/W facades. 0 -> no scaling!
                                   
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
    Building.basic_simulation_setup(construction_db_RSL,systems_db_RSL,regelung,anlagennutzungsgrad_wrg, korrekturfaktor_luftungs_eff_f_v, ventilation_volume_flow, increased_ventilation_volume_flow, area_per_person,combustion_efficiency_factor_new,combustion_efficiency_factor_old)
    Building.specific_simulation_setup(weatherfile_path,weather_data_sia,hohe_uber_meer, gebaeudekategorie_sia, heating_setpoint, cooling_setpoint, heat_pump_efficiency,shading_factor_season,RSP,electricity_decarbonization_factor,
                                       biogenic_carbon_on,disposal_emissions_intervention_on,simplifed_LCA,int_finishings_replacement_at_intervention_ren, embodied_emissions_decarbonization_fraction,
                                       district_heating_decarbonization_factor)
    
    
    """Call Simulation Based on scenario"""
    scch.call_simulations(Building,Intervention_scenario)
    
    """Store Simulation Results"""
    log_df = Building.get_info_to_df()
    
    total_cummulative_emissions = Building.annualized_cummulative_emissions_per_area_total
    heating_energy_demand = Building.annualized_heat_energy_demand_per_area_total
    #print('test')

    return  log_df


def process_params(*X):
    log_df  = evaluate_model(*X)
    return  log_df


