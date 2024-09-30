#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 22 09:55:59 2024

@author: dominicbuettiker
"""


import numpy as np
import pandas as pd
import os
import sys
import copy
SIA_380_1_directory = "/Users/dominicbuettiker/Library/CloudStorage/OneDrive-Persönlich/Dominic/ETH/2_Master/4. Semester/Masterarbeit/Code/Model/Parametric_LCA_Master_Thesis/SIA_380_1"
sys.path.append(SIA_380_1_directory) #Functions directly used from ITA: Energy Calculation 
import simulation_engine as se # Important: Simulatin Engine refres to data_prep -> Here is also a sys path directory needed need to be ajusted if changed)
import embodied_emissions_calculation as eec
import data_prep as dp
main_path = "/Users/dominicbuettiker/Library/CloudStorage/OneDrive-Persönlich/Dominic/ETH/2_Master/4. Semester/Masterarbeit/Code/Model/Parametric_LCA_Master_Thesis/"
input_db = os.path.join(main_path, 'input_data') #path



#%%


def hardcoded_inputs():
    """Hardcoded_Values"""
    #other Values
    b_floor = 0.4 # lasse ich so, weil nicht direkt beeinflussbar
    set_back_reduction_factor = 1 # für was steht dieser Parameter?
    
    #PV not used
    pv_type= None #"m-Si"
    pv_efficiency = 0
    pv_area = np.array([0],dtype=float)  # m2, can be directly linked with roof size
    pv_performance_ratio = 0
    pv_tilt = np.array([0], dtype=float)  # in degrees
    pv_azimuth = np.array([0], dtype=float) # The north=0 convention applies
    max_electrical_storage_capacity = 0
    
    #currently fix, to be changed!
   
    electricity_factor_source = "KBOB" #scenario['emission source']
    electricity_factor_source_UBP = "KBOB" #scenario['emission source UBP']
    energy_cost_source = 'current' #scenario['energy cost source']
    electricity_factor_type = "annual"
    
    return b_floor, set_back_reduction_factor, pv_type, \
           pv_efficiency,pv_area,pv_performance_ratio,pv_tilt,pv_azimuth,max_electrical_storage_capacity, \
           electricity_factor_source,electricity_factor_source_UBP,energy_cost_source,electricity_factor_type
 

def initalize_emtpy_info_df(): #Must be align with the columns in the function "get_info_to_df". CHECK!!!
    """ To store the Results of the parametric study in a DF"""
    intervention_scenario = ['intervention_scenario','change_energy_reference_area','construction_type_new_name','existing_building']
    new_geometry = ['floors_ag_new','window_to_wall_ratio_new']
    input_ren = ['window_type_ren', 'insulation_type_ren', 'insulation_thickness_ren', 'thermal_bridge_add_on_ren', 'infiltration_volume_flow_ren']
    input_new = ['window_type_new', 'insulation_type_new','insulation_thickness_new', 'thermal_bridge_add_on_new', 'infiltration_volume_flow_new']
    
    input_sys = ['heating_system_new', 'heating_system_dhw_new', 'cooling_system_new', 'has_mechanical_ventilation_new','ventilation_volume_flow']
    input_exogenous = ['heating_setpoint', 'electricity_decarbonization_factor','RSP','energy_reference_area_total', 'embodied_emissions_decarbonization_fraction', 'district_heating_decarbonization_factor']
    methods = ['int_finishings_replacement_at_intervention_ren', 'biogenic_carbon_on', 'disposal_emissions_intervention_on','simplifed_LCA']
    
    intermediates_ren = ['u_windows_ren','u_walls_ag_ren','u_roof_ren', 'u_ceiling_to_basement_ren']
    intermediates_new = ['u_windows_new','u_walls_ag_new','u_roof_new', 'u_ceiling_to_basement_new']
    
    results = ['annualized_electricity_demand_per_area_total','annualized_heat_energy_demand_per_area_total','biogenic_stored_carbon_construction','embodied_emissions_demolished_at_intervention','biogenic_stored_carbon_demolished_at_intervention','annualized_operative_emissions_per_area_total','annualized_embodied_emissions_per_area_total','annualized_cummulative_emissions_per_area_total']
    results_pie = ['GWP_str_prod_upfront','GWP_str_bio_upfront', 'GWP_str_replacement_disp_no_bio','GWP_str_bio_replacement','GWP_sys_prod_upfront','GWP_sys_replacement_disp']
    
    
    df  =  pd.DataFrame(columns= intervention_scenario + new_geometry + input_ren + intermediates_ren + input_new + intermediates_new + input_sys + input_exogenous + methods + results_pie + results)
    return df
    

    
#%% Define Class Scenario

class Scenario(object):
   
    def __init__(self,
                 #Building Geometry Input General
                 window_orientations, #N E S W
                 height_floors,
                 
                 #gebäudegeometrie_old_input
                 window_to_wall_ratio_old,
                 floors_ag_old,
                 floors_bg_old,
                 width_old, #Nord-South Facade 
                 length_old, #East-West Facade
                 heated_fraction_ag_old,
                 
                 
                 #materialisierung_old
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
                 existing_building = None):
                #TODO: Add Partitions Type!
         
         self.window_orientations=window_orientations
         
         self.window_to_wall_ratio_old=window_to_wall_ratio_old
         self.height_floors = height_floors
         self.floors_ag_old=floors_ag_old
         self.floors_bg_old=floors_bg_old
         self.width_old=width_old
         self.length_old=length_old
         self.heated_fraction_ag_old=heated_fraction_ag_old
         
         self.wall_type_ag_old=wall_type_ag_old
         self.wall_type_bg_old=wall_type_bg_old
         self.window_type_old=window_type_old
         self.ceiling_type_old=ceiling_type_old
         self.slab_basement_type_old=slab_basement_type_old
         self.ceiling_to_basement_type_old=ceiling_to_basement_type_old
         self.roof_type_old=roof_type_old
         self.heat_capacity_per_energyreferencearea_old = heat_capacity_per_energyreferencearea_old
         self.infiltration_volume_flow_old = infiltration_volume_flow_old
         self.thermal_bridge_add_on_old = thermal_bridge_add_on_old
         self.partitions_type_old = partitions_type_old
         self.fraction_partitions_old = fraction_partitions_old 
         self.tilted_roof_type_old = tilted_roof_type_old
         self.existing_building = existing_building
         
         
         #Later used attributes, here definded and set to a default value to avoid errors:
         self.energy_reference_area_ren = 0
         self.energy_reference_area_new = 0
         self.nominal_heating_power_stat_ren = 0
         self.nominal_heating_power_stat_new = 0
         self.nominal_cooling_power_stat_ren = 0
         self.nominal_cooling_power_stat_new = 0
         

         self.operational_emissions_per_area_ren = np.zeros(12)
         self.operational_emissions_per_area_new =  np.zeros(12)
         self.annualized_embodied_emissions_envelope_per_area_ren = np.zeros(3) #0
         self.annualized_embodied_emissions_envelope_per_area_new = np.zeros(3) #0
         self.annualized_embodied_emissions_envelope_upfront_per_area_ren = np.zeros(3) #0
         self.annualized_embodied_emissions_envelope_upfront_per_area_new = np.zeros(3) #0
         
         self.heating_energy_demand_ren = np.zeros(12)
         self.heating_energy_demand_new = np.zeros(12)
         self.grid_electricity_emissions_per_area_ren = np.zeros(12)
         self.grid_electricity_emissions_per_area_new = np.zeros(12)
         self.electricity_demand_per_area_ren = np.zeros(12)
         self.electricity_demand_per_area_new = np.zeros(12)
         
         """Fix parameters """
         self.standart_thickness_partitions  =  0.15 # in [m], this value is used to calcualte the linear meter of partitions based on the fraction partitions per ERA
         


       
#%%
    def basic_simulation_setup(self,construction_db,systems_db,regelung,anlagennutzungsgrad_wrg,korrekturfaktor_luftungs_eff_f_v,ventilation_volume_flow,increased_ventilation_volume_flow,area_per_person,combustion_efficiency_factor_new,combustion_efficiency_factor_old):
        """
        TODO: Explanation
        """
        self.construction_db = construction_db
        self.systems_db = systems_db
        self.regelung = regelung
        self.anlagennutzungsgrad_wrg = anlagennutzungsgrad_wrg # SIA 380-1 Tab 23
        self.korrekturfaktor_luftungs_eff_f_v = korrekturfaktor_luftungs_eff_f_v  # zwischen 0.8 und 1.2 gemäss SIA380-1 Tab 24
        self.ventilation_volume_flow = ventilation_volume_flow # give a number in m3/(hm2) or select "SIA" to follow SIA380-1 code
        self.increased_ventilation_volume_flow = increased_ventilation_volume_flow # give a number in m3/hm2, this volume flow is used when cooling with outside air is possible
        self.area_per_person = area_per_person
        self.combustion_efficiency_factor_new = combustion_efficiency_factor_new
        self.combustion_efficiency_factor_old = combustion_efficiency_factor_old
         
    def specific_simulation_setup(self, weatherfile_path, weather_data_sia, hohe_uber_meer, gebaeudekategorie_sia,heating_setpoint,
                                  cooling_setpoint,heat_pump_efficiency,shading_factor_season,RSP,electricity_decarbonization_factor,
                                  biogenic_carbon_on,disposal_emissions_intervention_on,simplifed_LCA,int_finishings_replacement_at_intervention_ren,
                                  embodied_emissions_decarbonization_fraction,district_heating_decarbonization_factor):
        
        """
        TODO: Setup of building and metodical specific parameters, need to be assigned, before running the simulations
        ATTENTION: Weather File path: for different climate scenarios: they have to differ between system sizing and energy demand calculation!
        """
        self.hohe_uber_meer = hohe_uber_meer 
        self.gebaeudekategorie_sia = gebaeudekategorie_sia
        self.heating_setpoint = heating_setpoint  # number in deC or select "SIA" to follow the SIA380-1 code
        self.cooling_setpoint = cooling_setpoint
        self.heat_pump_efficiency = heat_pump_efficiency
        self.shading_factor_season = shading_factor_season
        self.RSP = RSP
        self.weatherfile_path = weatherfile_path
        self.weather_data_sia = weather_data_sia
        self.electricity_decarbonization_factor = electricity_decarbonization_factor
        self.biogenic_carbon_on = biogenic_carbon_on
        self.disposal_emissions_intervention_on = disposal_emissions_intervention_on
        self.simplifed_LCA = simplifed_LCA
        self.int_finishings_replacement_at_intervention_ren = int_finishings_replacement_at_intervention_ren
        self.embodied_emissions_decarbonization_fraction = embodied_emissions_decarbonization_fraction
        self.district_heating_decarbonization_factor = district_heating_decarbonization_factor
       
    
    def calc_geometry_properties_old(self):
        """
        Generates the Geometry porperties for the Simulation of the Original Building, based on the inputgeometry data (Related to CEA)
        TODO: Check comments, if some factors need to be included
        """
        self.height_old = self.floors_ag_old*self.height_floors
        
        self.roof_area_old = self.width_old*self.length_old #Eventually to be changed! 
        self.floor_area_old = self.width_old*self.length_old #Eventually to be changed to a slightly lower value!?
        
        self.energy_reference_area_old = self.floors_ag_old*self.width_old*self.length_old*self.heated_fraction_ag_old #Only heated areas above ground!
        
        wall_area_N_S = self.width_old*self.height_old*(1-self.window_to_wall_ratio_old)
        wall_area_E_W = self.length_old*self.height_old*(1-self.window_to_wall_ratio_old)
        self.wall_areas_ag_old = np.array([wall_area_N_S,wall_area_E_W,wall_area_N_S,wall_area_E_W]) #orientation_N_E_S_W
        
        wall_area_bg_N_S = self.width_old * self.floors_bg_old * self.height_floors 
        wall_area_bg_E_W = self.length_old * self.floors_bg_old * self.height_floors 
        self.wall_areas_bg_old = np.array([wall_area_bg_N_S,wall_area_bg_E_W,wall_area_bg_N_S,wall_area_bg_E_W]) #orientation_N_E_S_W
    
        
        window_areas_N_S = self.width_old*self.height_old*(self.window_to_wall_ratio_old)
        window_areas_E_W = self.length_old*self.height_old*(self.window_to_wall_ratio_old)
        self.window_areas_old = np.array([window_areas_N_S,window_areas_E_W,window_areas_N_S,window_areas_E_W]) #orientation_N_E_S_W
        
        total_floor_area = self.floor_area_old*(self.floors_ag_old+self.floors_bg_old)
        LFM_partitions = total_floor_area * self.fraction_partitions_old/self.standart_thickness_partitions  # self.energy_reference_area_old #A given Area is coverd with partitions, this is represented with the fraction_partitions_old. It is referenced to the total floor area. Based on that the total lengt of all partitions is calculated. 
        self.area_partitions_old = LFM_partitions * self.height_floors #Total length of partitions (for the whole building) multipled with the floor height = m2 partitions. 
     
    
    def calc_uvalues_old(self,database):
        """
        Attention: It is also iterated over Material layery which don't contribute to the u-value; they need a empty entry in the database file (later translated to a infinity)
        TODO: Check comments: R_se for non heated areas and also check the roof 
        """
        R_si = 0.13  #m2K/W According SIA 280/1 2.4.6.
        R_se = 0.04  #m2K/W According SIA 280/1 2.4.6.
        # TODO: Check!
        R_si_unheated = 0.13 #m2K/W, correct 
        
        self.g_windows_old = database['g_value'][self.window_type_old]
        self.u_windows_old = database['u_value'][self.window_type_old] #Question are hi and he not needed? 
        
        u_walls_ag_old = R_si + R_se 
        for i, name in enumerate(self.wall_type_ag_old):
            u_walls_ag_old += 1/database['u_value'][name]
        self.u_walls_ag_old = 1/u_walls_ag_old
        
        
        u_ceiling_to_basement_old =  R_si + R_si_unheated # correct?
        for i, name in enumerate(self.ceiling_to_basement_type_old):
            u_ceiling_to_basement_old += 1/database['u_value'][name]
        self.u_ceiling_to_basement_old = 1/u_ceiling_to_basement_old
     
        u_roof_old =  R_si + R_si_unheated # correct? 
        for i, name in enumerate(self.roof_type_old):
            u_roof_old += 1/database['u_value'][name] #Attetion: For U value roof, materials of the cold roof must have a empty entry in the u-value cell in the spreasheet 
        self.u_roof_old = 1/u_roof_old


    
    def system_properties_old(self,heating_system_old,heating_system_dhw_old,heat_emission_system_old,heat_distribution_old):
        """
        TODO: Explanation
        """
        #Has only heating and dhw system, since typical for swiss residential buildings
        self.heating_system_old = heating_system_old # zb"ASHP"
        self.heating_system_dhw_old = heating_system_dhw_old ## This is currently a limitation of the RC Model. Automatically the same!
        if heating_system_dhw_old == 'same':
            heating_system_dhw_old = heating_system_old
        self.heat_emission_system_old = heat_emission_system_old
        self.heat_distribution_old = heat_distribution_old
        
        
    
    def refurbishment_envelop(self, 
                              window_type_ren, wall_type_ag_ren,roof_type_ren,ceiling_to_basement_type_ren,ceiling_type_ren,
                              wall_type_bg_ren,slab_basement_type_ren,partitions_type_ren,tilted_roof_type_ren,
                              infiltration_volume_flow_ren,roof_area_ren,thermal_bridge_add_on_ren):
        """
        Bla
        TODO: Add Partitions Type!
        """
        #Geometry is the same, except from Roof 
        self.window_to_wall_ratio_ren=self.window_to_wall_ratio_old
        self.window_areas_ren = self.window_areas_old
        self.wall_areas_ag_ren = self.wall_areas_ag_old
        self.wall_areas_bg_ren = self.wall_areas_bg_old
        self.energy_reference_area_ren = self.energy_reference_area_old 
        self.floor_area_ren = self.floor_area_old
        self.area_partitions_ren = self.area_partitions_old
        self.floors_ag_ren = self.floors_ag_old


        self.roof_area_ren = roof_area_ren  #To be zero if Aufstockung
        
        #Construction_types
        self.heat_capacity_per_energyreferencearea_ren = self.heat_capacity_per_energyreferencearea_old #not changed!
        
        self.window_type_ren = window_type_ren
        
        self.wall_type_ag_ren = wall_type_ag_ren
        self.roof_type_ren =  roof_type_ren
        self.ceiling_to_basement_type_ren = ceiling_to_basement_type_ren
        self.ceiling_type_ren = ceiling_type_ren
        self.wall_type_bg_ren = wall_type_bg_ren
        self.slab_basement_type_ren = slab_basement_type_ren 
        self.partitions_type_ren = partitions_type_ren
        self.tilted_roof_type_ren = tilted_roof_type_ren
        
        
        
        #Envelop properties
        self.infiltration_volume_flow_ren = infiltration_volume_flow_ren
        self.thermal_bridge_add_on_ren = thermal_bridge_add_on_ren
        
    def calc_uvalues_renovation(self,database):
        """
        Attention: It is also iterated over Material layery which don't contribute to the u-value; they need a empty entry in the database file (later translated to a infinity)
        TODO: Check comments: R_se for non heated areas and also check the roof 
        """
        R_si = 0.13  #m2K/W According SIA 280/1 2.4.6.
        R_se = 0.04  #m2K/W According SIA 280/1 2.4.6.
        # TODO: Check!
        R_si_unheated = 0.13 #m2K/W, correct???
        
        self.g_windows_ren = database['g_value'][self.window_type_ren]
        self.u_windows_ren = database['u_value'][self.window_type_ren] #Question are hi and he not needed? 
        
        u_walls_ag_ren = R_si + R_se 
        for i, name in enumerate(self.wall_type_ag_ren):
            u_walls_ag_ren += 1/database['u_value'][name]
        self.u_walls_ag_ren = 1/u_walls_ag_ren
        
        
        u_ceiling_to_basement_ren =  R_si + R_si_unheated # correct?
        for i, name in enumerate(self.ceiling_to_basement_type_ren):
            u_ceiling_to_basement_ren += 1/database['u_value'][name]
        self.u_ceiling_to_basement_ren = 1/u_ceiling_to_basement_ren
        
        u_roof_ren =  R_si + R_si_unheated # correct? 
        for i, name in enumerate(self.roof_type_ren):
            u_roof_ren += 1/database['u_value'][name] #Attetion: For U value roof, materials of the cold roof must have a empty entry in the u-value cell in the spreasheet 
        self.u_roof_ren = 1/u_roof_ren
        
        
    
          
    
    def new_systems(self,heating_system_new,heating_system_dhw_new,heat_emission_system_new,heat_distribution_new,
                    cooling_system_new,cold_emission_system_new,has_mechanical_ventilation_new):
        """
        Define the Systems of the Refurbished, New or Extended Building: 
        TODO: Actually it lacks a opportunity to use the exisitng supply and emissions systems for extensions. 
        """
        
        self.heating_system_new = heating_system_new # zb"ASHP"
        self.heating_system_dhw_new = heating_system_dhw_new ## This is currently a limitation of the RC Model. Automatically the same!
        if heating_system_dhw_new == 'same':
            self.heating_system_dhw_new = heating_system_new
        self.heat_emission_system_new = heat_emission_system_new
        self.heat_distribution_new = heat_distribution_new
        self.cooling_system_new = cooling_system_new
        self.cold_emission_system_new = cold_emission_system_new
        self.has_mechanical_ventilation_new = has_mechanical_ventilation_new
        
    def new_construction_geometry(self,window_to_wall_ratio_new,floors_ag_new,
                                  floors_bg_new,width_new,length_new,heated_fraction_ag_new,fraction_partitions_new):
        
        self.floors_ag_new = floors_ag_new 
        self.floors_bg_new = floors_bg_new
        self.width_new = width_new
        self.length_new = length_new
        self.heated_fraction_ag_new = heated_fraction_ag_new
        self.window_to_wall_ratio_new = window_to_wall_ratio_new
        self.fraction_partitions_new = fraction_partitions_new
        
        self.height_new = self.floors_ag_new*self.height_floors #same Floor hight for all Buildings 
        self.roof_area_new = self.width_new*self.length_new #Flat projection for tilted roof! -> not useful for PV or heated tilted roofs, Eventually to be changed! 
        self.floor_area_new  = self.width_new*self.length_new #Eventually to be changed to a slightly lower value!?
        self.energy_reference_area_new = self.floors_ag_new*self.width_new*self.length_new*self.heated_fraction_ag_new #Only heated areas above ground!
        
        wall_area_N_S = self.width_new*self.height_new*(1-self.window_to_wall_ratio_new)
        wall_area_E_W = self.length_new*self.height_new*(1-self.window_to_wall_ratio_new)
        self.wall_areas_ag_new = np.array([wall_area_N_S,wall_area_E_W,wall_area_N_S,wall_area_E_W]) #orientation_N_E_S_W
        
        wall_area_bg_N_S = self.width_new * self.floors_bg_new * self.height_floors 
        wall_area_bg_E_W = self.length_new * self.floors_bg_new * self.height_floors 
        self.wall_areas_bg_new = np.array([wall_area_bg_N_S,wall_area_bg_E_W,wall_area_bg_N_S,wall_area_bg_E_W])
        
        window_areas_N_S = self.width_new*self.height_new*(self.window_to_wall_ratio_new)
        window_areas_E_W = self.length_new*self.height_new*(self.window_to_wall_ratio_new)
        self.window_areas_new = np.array([window_areas_N_S,window_areas_E_W,window_areas_N_S,window_areas_E_W]) #orientation_N_E_S_W
        
        total_floor_area = self.floor_area_new*(self.floors_ag_new+self.floors_bg_new)
        LFM_partitions = total_floor_area*self.fraction_partitions_new/self.standart_thickness_partitions #self.energy_reference_area_new
        self.area_partitions_new = LFM_partitions * self.height_floors 

         
    def new_construction_envelop(self, window_type_new, wall_type_ag_new,roof_type_new,ceiling_to_basement_type_new,ceiling_type_new,
                              wall_type_bg_new,slab_basement_type_new,partitions_type_new,tilted_roof_type_new,
                              infiltration_volume_flow_new,thermal_bridge_add_on_new,heat_capacity_per_energyreferencearea_new):
        """
        Assign the construction of the new parts to the object
        """
        self.window_type_new = window_type_new
        self.wall_type_ag_new = wall_type_ag_new
        self.roof_type_new = roof_type_new
        self.ceiling_to_basement_type_new = ceiling_to_basement_type_new
        self.ceiling_type_new = ceiling_type_new
        self.wall_type_bg_new = wall_type_bg_new
        self.slab_basement_type_new = slab_basement_type_new
        self.partitions_type_new = partitions_type_new #None # partitions_type_new
        self.tilted_roof_type_new = tilted_roof_type_new #None #tilted_roof_type_new
                
        self.infiltration_volume_flow_new = infiltration_volume_flow_new
        self.thermal_bridge_add_on_new = thermal_bridge_add_on_new
        self.heat_capacity_per_energyreferencearea_new = heat_capacity_per_energyreferencearea_new
        
        
        
        
    
    def new_construction_uvalues(self,database):
        """
        Attention: It is also iterated over Material layery which don't contribute to the u-value; they need a empty entry in the database file (later translated to a infinity u value)
        TODO: Check comments: R_se for non heated areas and also check the roof 
        """
        R_si = 0.13  #m2K/W According SIA 280/1 2.4.6.
        R_se = 0.04  #m2K/W According SIA 280/1 2.4.6.
        # TODO: Check!
        R_si_unheated = 0.13 #m2K/W, correct???
        
        self.g_windows_new = database['g_value'][self.window_type_new]
        self.u_windows_new = database['u_value'][self.window_type_new] #Question are hi and he not needed? 
        
        u_walls_ag_new = R_si + R_se 
        for i, name in enumerate(self.wall_type_ag_new):
            u_walls_ag_new += 1/database['u_value'][name]
        self.u_walls_ag_new = 1/u_walls_ag_new
        
        
        u_ceiling_to_basement_new =  R_si + R_si_unheated # correct?
        for i, name in enumerate(self.ceiling_to_basement_type_new):
            u_ceiling_to_basement_new += 1/database['u_value'][name]
        self.u_ceiling_to_basement_new = 1/u_ceiling_to_basement_new
        
        u_roof_new =  R_si + R_si_unheated # correct? 
        for i, name in enumerate(self.roof_type_new):
            u_roof_new += 1/database['u_value'][name] #Attetion: For U value roof, materials of the cold roof must have a empty entry in the u-value cell in the spreasheet 
        self.u_roof_new = 1/u_roof_new
        
    
   
        
    def demolished_envelop(self, window_type_demo, wall_type_ag_demo,roof_type_demo,
                           ceiling_to_basement_type_demo,ceiling_type_demo,
                           wall_type_bg_demo,slab_basement_type_demo,
                           partitions_type_demo,tilted_roof_type_demo):
        """Stores the demolished material layers at the Intervention, used to calculated disposal GHG's later, 
        combined with the geometrical properties of the old Building"""
        
        self.window_type_demo = window_type_demo
        self.wall_type_ag_demo = wall_type_ag_demo
        self.roof_type_demo = roof_type_demo
        self.ceiling_to_basement_type_demo = ceiling_to_basement_type_demo
        self.ceiling_type_demo = ceiling_type_demo
        self.wall_type_bg_demo = wall_type_bg_demo
        self.slab_basement_type_demo = slab_basement_type_demo
        self.partitions_type_demo = partitions_type_demo
        self.tilted_roof_type_demo = tilted_roof_type_demo
        
        
        
    def demolished_systems(self,heating_system_demo,heating_system_dhw_demo,
                           heat_emission_system_demo,heat_distribution_demo):
        """Stores types of demolished systems at the Intervention, used to calculated disposal GHG's later, 
        combined with the geometrical and capacity properties of the old Building. 
        BUT: so far no disposal emissions of the system included, since sizeing would be needed (computationally not worth)"""
        
        self.heating_system_demo = heating_system_demo
        self.heating_system_dhw_demo = heating_system_dhw_demo
        self.heat_emission_system_demo = heat_emission_system_demo
        self.heat_distribution_demo = heat_distribution_demo
            
    def whole_building_featues(self):
        self.energy_reference_area_total = self.energy_reference_area_ren + self.energy_reference_area_new
        self.change_energy_reference_area = 100*(self.energy_reference_area_total-self.energy_reference_area_old)/self.energy_reference_area_old #in %
        
    def invalid_combination(self):
        """Is called if the parametric Intput is invalid; Based on that the simiulation starts or not """
        self.invalid_scenario = True
    
    def sum_up_whole_building_sys_capacity(self):
        
        # Capacities sum up (relevant in case of extension of building)
        self.nominal_heating_power_stat_total = self.nominal_heating_power_stat_ren + self.nominal_heating_power_stat_new
        self.nominal_cooling_power_stat_total = self.nominal_cooling_power_stat_ren  + self.nominal_cooling_power_stat_new
        
    def modify_u_values_due_to_extension(self):
        self.u_roof_ren = 0
        self.u_ceiling_to_basement_new = 0 
        
    def define_scenario(self,Intervention_scenario,insulation_type_ren, insulation_thickness_ren,
                             construction_type_new_name,insulation_type_new,insulation_thickness_new):
        self.intervention_scenario = Intervention_scenario
        
        self.insulation_type_ren = insulation_type_ren
        self.insulation_thickness_ren = insulation_thickness_ren
        self.insulation_type_new = insulation_type_new
        self.insulation_thickness_new = insulation_thickness_new
        self.construction_type_new_name  = construction_type_new_name
        
    
    def print_sanitiy_checks(self): 
        print('tobedone ')
        
        
    def data_collector(self):
        
        #To get a propper value per energy reference area (ERA) seperate results from the renovated building and new parts are summed up and scaled with their corresponding ERA
        #Operational Energy Demands
        self.annualized_heat_energy_demand_per_area_total = (self.heating_energy_demand_ren.sum()* self.energy_reference_area_ren \
                                                             + self.heating_energy_demand_new.sum()* self.energy_reference_area_new) / self.energy_reference_area_total
        #self.annualized_cooling_energy_demand_per_area_total = 
        self.annualized_electricity_demand_per_area_total = (self.electricity_demand_per_area_ren.sum()* self.energy_reference_area_ren \
                                                             + self.electricity_demand_per_area_new.sum()* self.energy_reference_area_new) / self.energy_reference_area_total
        #electricity_demand_per_area_new
       
        #Operational Emissions
        self.annualized_operative_emissions_per_area_total = (self.operational_emissions_per_area_ren.sum() * self.energy_reference_area_ren \
                                                        + self.operational_emissions_per_area_new.sum() * self.energy_reference_area_new)/ self.energy_reference_area_total
        #Embodied Emissions Envelop (System is calculated for all together)
        self.annualized_embodied_emnissions_envelope_per_area_total = (self.annualized_embodied_emissions_envelope_per_area_ren *self.energy_reference_area_ren \
                                                                       + self.annualized_embodied_emissions_envelope_per_area_new * self.energy_reference_area_new)/ self.energy_reference_area_total
        
        #Embodied Emissions
        #Demolishment 
        # TODO: Add the disposal of systems 
        self.embodied_emissions_disp_demolished = self.annualized_embodied_emsissions_envelope_per_area_dem[1]
        
        if self.biogenic_carbon_on == True: 
            self.biogenic_stored_carbon_demolished = self.annualized_embodied_emsissions_envelope_per_area_dem[2]
        else: 
            self.biogenic_stored_carbon_demolished = 0
       
        #Total embodied emissions demolished
        if self.disposal_emissions_intervention_on == True: 
            self.total_embodied_emissions_demolished  =  self.embodied_emissions_disp_demolished  + self.biogenic_stored_carbon_demolished 
        else:
            self.total_embodied_emissions_demolished = 0 
        
        #Embodied emissions renovation/new construction  
        #Systems
        self.embodied_emissions_prod_disp_systems = self.annualized_embodied_impact_systems_per_area_total.sum()
       
        #Construction 
        self.embodied_emissions_prod_disp_construction = self.annualized_embodied_emnissions_envelope_per_area_total[0] + self.annualized_embodied_emnissions_envelope_per_area_total[1]
        if self.biogenic_carbon_on == True: 
            self.biogenic_stored_carbon_construction = self.annualized_embodied_emnissions_envelope_per_area_total[2]
        else:
            self.biogenic_stored_carbon_construction = 0 
        #Total
        self.total_embodied_emissions_construction  = self.embodied_emissions_prod_disp_construction +  self.biogenic_stored_carbon_construction + self.embodied_emissions_prod_disp_systems
        
        #TOTAL OVER ALL: all demolishment emissions, all emissions of new construction/systems and biogenic carbon
        self.annualized_embodied_emissions_per_area_total =  self.total_embodied_emissions_demolished + self.total_embodied_emissions_construction 
        self.annualized_cummulative_emissions_per_area_total = self.annualized_embodied_emissions_per_area_total +  self.annualized_operative_emissions_per_area_total
        
        
        #UPFRONT EMISSIONS: 
        self.annualized_embodied_emissions_upfront_envelope_per_area_total = (self.annualized_embodied_emissions_envelope_upfront_per_area_ren *self.energy_reference_area_ren \
                                                                       + self.annualized_embodied_emissions_envelope_upfront_per_area_new * self.energy_reference_area_new)/ self.energy_reference_area_total
           
        self.GWP_str_prod_upfront = self.annualized_embodied_emissions_upfront_envelope_per_area_total[0]
        self.GWP_str_disp_upfront = self.annualized_embodied_emissions_upfront_envelope_per_area_total[1]
        if self.biogenic_carbon_on == True: 
            self.GWP_str_bio_upfront = self.annualized_embodied_emissions_upfront_envelope_per_area_total[2]
        else: 
            self.GWP_str_bio_upfront = 0
         
        self.GWP_sys_prod_upfront = self.annualized_embodied_impact_systems_upfront_per_area_total[0]
        self.GWP_sys_disp_upfront = self.annualized_embodied_impact_systems_upfront_per_area_total[1]
        
        self.GWP_sys_replacement_disp = self.embodied_emissions_prod_disp_systems - self.GWP_sys_prod_upfront 
        self.GWP_str_replacement_disp_no_bio = self.embodied_emissions_prod_disp_construction - self.GWP_str_prod_upfront 
        self.GWP_str_bio_replacement = self.biogenic_stored_carbon_construction - self.GWP_str_bio_upfront 
        
    
        #Some sanity checks: 
        # print('annualized_heat_energy_demand_per_area_total: ', self.annualized_heat_energy_demand_per_area_total)
        # print('annualized embodied_emissions_prod_disp_systems per area: ',self.embodied_emissions_prod_disp_systems)
        # print('embodied_emissions_prod_disp_construction: ', self.embodied_emissions_prod_disp_construction)
        # print('biogenic_stored_carbon_construction: ', self.biogenic_stored_carbon_construction)
        # print('annualized_embodied_emissions_per_area_total: ',self.annualized_embodied_emissions_per_area_total)
        # print('annualized_operative_emissions_per_area_total: ', self.annualized_operative_emissions_per_area_total)
        # print('annualized_cummulative_emissions_per_area_total: ',self.annualized_cummulative_emissions_per_area_total )
   
      
    def get_info_to_df(self):
        
        
        if self.intervention_scenario in [0,1]:
            input_ren = [self.window_type_ren, self.insulation_type_ren,self.insulation_thickness_ren, self.thermal_bridge_add_on_ren, self.infiltration_volume_flow_ren]
            input_new = [None]*5
            intermediates_ren = [self.u_windows_ren,self.u_walls_ag_ren,self.u_roof_ren, self.u_ceiling_to_basement_ren]
            intermediates_new = [None]*4
        elif self.intervention_scenario in [2]:
            input_ren = [None]*5
            input_new = [self.window_type_new, self.insulation_type_new,self.insulation_thickness_new, self.thermal_bridge_add_on_new, self.infiltration_volume_flow_new]
            intermediates_ren = [None]*4
            intermediates_new = [self.u_windows_new, self.u_walls_ag_new,self.u_roof_new, self.u_ceiling_to_basement_new]
        
        elif self.intervention_scenario in [3]:
            input_ren = [self.window_type_ren, self.insulation_type_ren,self.insulation_thickness_ren, self.thermal_bridge_add_on_ren, self.infiltration_volume_flow_ren]
            input_new = [self.window_type_new, self.insulation_type_new,self.insulation_thickness_new, self.thermal_bridge_add_on_new, self.infiltration_volume_flow_new]
            intermediates_ren = [self.u_windows_ren,self.u_walls_ag_ren,self.u_roof_ren, self.u_ceiling_to_basement_ren]
            intermediates_new = [self.u_windows_new, self.u_walls_ag_new,self.u_roof_new, self.u_ceiling_to_basement_new]
        else: 
            input_ren = [None]*5
            input_new = [None]*5
            intermediates_ren = [None]*3
            intermediates_new = [None]*3
        if self.intervention_scenario in [2,3]:
            new_geometry = [self.floors_ag_new,self.window_to_wall_ratio_new]
        else:
            new_geometry = [None]*2
        
        input_sys = [self.heating_system_new, self.heating_system_dhw_new, self.cooling_system_new, self.has_mechanical_ventilation_new, self.ventilation_volume_flow]
        input_exogenous = [self.heating_setpoint, self.electricity_decarbonization_factor,self.RSP, self.energy_reference_area_total, self.embodied_emissions_decarbonization_fraction, self.district_heating_decarbonization_factor]
        methods = [self.int_finishings_replacement_at_intervention_ren, self.biogenic_carbon_on, self.disposal_emissions_intervention_on,self.simplifed_LCA]
        
        results = [self.annualized_electricity_demand_per_area_total,self.annualized_heat_energy_demand_per_area_total,self.biogenic_stored_carbon_construction, self.total_embodied_emissions_demolished, self.biogenic_stored_carbon_demolished, self.annualized_operative_emissions_per_area_total,self.annualized_embodied_emissions_per_area_total, self.annualized_cummulative_emissions_per_area_total]
        results_pie = [self.GWP_str_prod_upfront,self.GWP_str_bio_upfront, self.GWP_str_replacement_disp_no_bio,self.GWP_str_bio_replacement,self.GWP_sys_prod_upfront,self.GWP_sys_replacement_disp]
        
        return [self.intervention_scenario,self.change_energy_reference_area,self.construction_type_new_name,self.existing_building] + new_geometry + input_ren + intermediates_ren + input_new + intermediates_new + input_sys + input_exogenous + methods + results_pie + results
        #print('To be done, a function that extracts all relevant values and store it in a df')
     
        

    """ Setup Simulation: Beside the Energy Systems embodied emissions, this have to be done twice """

#%% Op emissions and e demans
    def operational_energy_demand_and_emissions_new_areas(self):
        """
        Function calculates the Energy demads (Heating, Domestic Hot Water, Cooling, Ventilation, Electricity) and the Emissions
        Bevorhand the "intervention_scenario" function in the file "scenario_configurator_helper" must needed to be called to define
        all Building Properties. 
        
        """
        
        """Hardcoded_Values, assumes cold basement!"""
        b_floor, set_back_reduction_factor, pv_type, \
        pv_efficiency,pv_area,pv_performance_ratio,pv_tilt,pv_azimuth,max_electrical_storage_capacity, \
        electricity_factor_source,electricity_factor_source_UBP,energy_cost_source,electricity_factor_type \
        = hardcoded_inputs()
        
        
        
        """Setup Energy simulationd detailed"""
        ## Introduce thermal bridge factor 
        # the thermal bridge factor leads to an overall increase in transmittance losses. It is implemented here
        # because that is the easiest way. For result analysis the input file u-values need to be used.
        thermal_bridge_factor = 1.0 + (self.thermal_bridge_add_on_new / 100.0)
        u_windows = self.u_windows_new * thermal_bridge_factor
        u_walls = self.u_walls_ag_new * thermal_bridge_factor
        u_roof = self.u_roof_new * thermal_bridge_factor
        u_floor = self.u_ceiling_to_basement_new * thermal_bridge_factor
        ## Bauteile:
        # Windows: [[Orientation],[Areas],[U-value],[g-value]]
        windows = np.array([self.window_orientations,
                            self.window_areas_new,
                            np.repeat(u_windows, len(self.window_orientations)),
                            np.repeat(self.g_windows_new, len(self.window_orientations))],
                           dtype=object)  # dtype=object is necessary because there are different data types
        walls = np.array([self.wall_areas_ag_new,
                          np.repeat(u_walls, len(self.wall_areas_ag_new))])
        roof = np.array([[self.roof_area_new], [u_roof]])  # roof: [[Areas], [U-values]]
        floor = np.array([[self.floor_area_new], [u_floor], [b_floor]]) # floor to ground (for now) [[Areas],[U-values],[b-values]]
        #sanitiy checks: 
        #print('windows: ',windows, 'walls: ', walls, 'roof: ', roof, 'cieling_basement: ', floor )
        
        
        ##Shading
        shading_factor_monthly = dp.factor_season_to_month(self.shading_factor_season)
        
        """Define Building For Energy Simulation"""
        Gebaude_new_static = se.Building(self.gebaeudekategorie_sia, self.regelung, windows, walls, roof, floor, self.energy_reference_area_new,
                                          self.anlagennutzungsgrad_wrg, self.infiltration_volume_flow_new, self.ventilation_volume_flow,
                                          self.increased_ventilation_volume_flow, self.heat_capacity_per_energyreferencearea_new,
                                          self.heat_pump_efficiency, self.combustion_efficiency_factor_new, self.electricity_decarbonization_factor,
                                          self.korrekturfaktor_luftungs_eff_f_v, self.hohe_uber_meer, shading_factor_monthly, self.heating_system_new, self.heating_system_dhw_new,
                                          self.cooling_system_new, self.heat_emission_system_new, self.cold_emission_system_new, self.heating_setpoint,
                                          self.cooling_setpoint, self.area_per_person, self.has_mechanical_ventilation_new, set_back_reduction_factor,
                                          max_electrical_storage_capacity,self.district_heating_decarbonization_factor)
    
        """PV is excluded"""
        # pv_yield_hourly = np.zeros(8760)
        # for pv_number in range(len(pv_area)):
        #      pv_yield_hourly += dp.photovoltaic_yield_hourly(pv_azimuth[pv_number], pv_tilt[pv_number], pv_efficiency,
        #                                                     pv_performance_ratio, pv_area[pv_number],
        #                                                      weather_file_dict_headers[weatherfile_path],
        #                                                      weather_file_dict_bodies[weatherfile_path],
        #                                                      solar_zenith_dict[weatherfile_path],
        #                                                      solar_azimuth_dict[weatherfile_path])
        # Gebaude_New_static.pv_production = pv_yield_hourly
        # Gebaude_New_static.pv_peak_power = pv_area.sum() * pv_efficiency  # in kW (required for simplified Eigenverbrauchsabschätzung)
    
        Gebaude_new_static.run_SIA_380_1(self.weather_data_sia)
        Gebaude_new_static.run_ISO_52016_monthly(self.weather_data_sia)
        Gebaude_new_static.run_dhw_demand()
        
        """Electicity demand detailed, according weekly and monthly occupancy shedules: They are missing, Needs to be checked, does not work!
        Generally questionable if reasonalbe, since SIA 2024 Bestandeswerte. """
        # unique_use_types = 1.1  #  Hardcoded scenarios['building use type'].unique() 
        # occupancy_schedules_dic = {}
        # for use_type in unique_use_types:
        #     occupancy_path = translations[translations['building use type'] == use_type]['occupancy schedule'].to_numpy()[0]
        #     occupancy_schedules_dic[use_type] = pd.read_csv(occupancy_path)
        # Gebaeude_static.run_SIA_electricity_demand(occupancy_schedules_dic[gebaeudekategorie_sia])
        """Simplyfied electrictiy demand for MFH according to sia 380/1 Tab. 12 (= SIA Bestandeswerte 2024)"""
        #TODO: Check if reasonable and eventually change it. (also couple to building usage)
        Gebaude_new_static.run_SIA_electricity_demand_simplifed()
        
        """Sizeing The Heating System, Always on Actual Weather data!"""
        weatherfile_path = f'{input_db}/weather_data/Zürich-hour_historic.epw'
        Gebaude_new_static.run_heating_sizing_384_201(weatherfile_path)
        self.nominal_heating_power_stat_new = Gebaude_new_static.nominal_heating_power  # in W 
        """AJUST to total Sum! (existing Building and Add on)"""
    
        Gebaude_new_static.run_cooling_sizing()
        self.nominal_cooling_power_stat_new = Gebaude_new_static.nominal_cooling_power # in W
        
        """Operational GHG"""
        Gebaude_new_static.run_SIA_380_emissions(emission_factor_source=electricity_factor_source,
                                              emission_factor_source_UBP=electricity_factor_source_UBP,
                                              emission_factor_type=electricity_factor_type,
                                              weather_data_sia=self.weather_data_sia,
                                              energy_cost_source=energy_cost_source,
                                              country="KBOB") #config['country'] 
        
        # print('ueberpruefung Heat Electricity demand kWh/m2year', Gebaeude_static.heating_elec.sum())
        #TODO: Expand here the push back of informations
        
        self.heating_energy_demand_new = Gebaude_new_static.heizwarmebedarf 
        self.grid_electricity_emissions_per_area_new = Gebaude_new_static.grid_electricity_emissions #Only of electricity
        self.operational_emissions_per_area_new = Gebaude_new_static.operational_emissions 
        self.heating_electricity_demand_per_area_new = Gebaude_new_static.heating_elec
        self.electricity_demand_per_area_new = Gebaude_new_static.net_electricity_demand

        self.Gebaude_new_static = Gebaude_new_static #All infos/methods of energy cacluclations can be accessed directly via self.Gebaude_new_static.variable/method 

        #del Gebaude_New_static
        return 
        
       

    def operational_energy_demand_and_emissions_renovated_areas(self):
        """
        Function calculates the Energy demads (Heating, Domestic Hot Water, Cooling, Ventilation, Electricity) and the Emissions
        Bevorhand the "intervention_scenario" function in the file "scenario_configurator_helper" must needed to be called to define
        all Building Properties. 
        
        """
        
        """Hardcoded_Values, assumes cold basement!"""
        b_floor, set_back_reduction_factor, pv_type, \
        pv_efficiency,pv_area,pv_performance_ratio,pv_tilt,pv_azimuth,max_electrical_storage_capacity, \
        electricity_factor_source,electricity_factor_source_UBP,energy_cost_source,electricity_factor_type \
        = hardcoded_inputs()
        

     
        """Setup Energy simulationd detailed"""
        ## Introduce thermal bridge factor 
        # the thermal bridge factor leads to an overall increase in transmittance losses. It is implemented here
        # because that is the easiest way. For result analysis the input file u-values need to be used.
        thermal_bridge_factor = 1.0 + (self.thermal_bridge_add_on_ren / 100.0)
        u_windows = self.u_windows_ren * thermal_bridge_factor
        u_walls = self.u_walls_ag_ren * thermal_bridge_factor
        u_roof = self.u_roof_ren* thermal_bridge_factor
        u_floor = self.u_ceiling_to_basement_ren * thermal_bridge_factor
    
        ## Bauteile:
        # Windows: [[Orientation],[Areas],[U-value],[g-value]]
        windows = np.array([self.window_orientations,
                            self.window_areas_ren,
                            np.repeat(u_windows, len(self.window_orientations)),
                            np.repeat(self.g_windows_ren, len(self.window_orientations))],
                           dtype=object)  # dtype=object is necessary because there are different data types
        walls = np.array([self.wall_areas_ag_ren,
                          np.repeat(u_walls, len(self.wall_areas_ag_ren))])
        roof = np.array([[self.roof_area_ren], [u_roof]])  # roof: [[Areas], [U-values]]
        floor = np.array([[self.floor_area_ren], [u_floor], [b_floor]]) # floor to ground (for now) [[Areas],[U-values],[b-values]]
        
        ##Shading
        shading_factor_monthly = dp.factor_season_to_month(self.shading_factor_season)
        
        """Define Building For Energy Simulation"""
        # Since  in the renovation case it is possible to keep the heating system: e.g. "old" but this has non influcene on the operational demands; 
        # therefore it is translated into the normal fossile based heating systems 
        if self.heating_system_new == 'Natural Gas old':
            heating_system_new = 'Natural Gas'
        elif self.heating_system_new == 'Oil old':
            heating_system_new = 'Oil'
        else: 
            heating_system_new =  self.heating_system_new 
            
        Gebaeude_ren_static = se.Building(self.gebaeudekategorie_sia, self.regelung, windows, walls, roof, floor, self.energy_reference_area_ren,
                                          self.anlagennutzungsgrad_wrg, self.infiltration_volume_flow_ren, self.ventilation_volume_flow,
                                          self.increased_ventilation_volume_flow, self.heat_capacity_per_energyreferencearea_ren,
                                          self.heat_pump_efficiency, self.combustion_efficiency_factor_new, self.electricity_decarbonization_factor,
                                          self.korrekturfaktor_luftungs_eff_f_v, self.hohe_uber_meer, shading_factor_monthly, heating_system_new, self.heating_system_dhw_new,
                                          self.cooling_system_new, self.heat_emission_system_new, self.cold_emission_system_new, self.heating_setpoint,
                                          self.cooling_setpoint, self.area_per_person, self.has_mechanical_ventilation_new, set_back_reduction_factor,
                                          max_electrical_storage_capacity,self.district_heating_decarbonization_factor)
    
        """PV is excluded"""
        # pv_yield_hourly = np.zeros(8760)
        # for pv_number in range(len(pv_area)):
        #      pv_yield_hourly += dp.photovoltaic_yield_hourly(pv_azimuth[pv_number], pv_tilt[pv_number], pv_efficiency,
        #                                                     pv_performance_ratio, pv_area[pv_number],
        #                                                      weather_file_dict_headers[weatherfile_path],
        #                                                      weather_file_dict_bodies[weatherfile_path],
        #                                                      solar_zenith_dict[weatherfile_path],
        #                                                      solar_azimuth_dict[weatherfile_path])
        # Gebaeude_static.pv_production = pv_yield_hourly
        # Gebaeude_static.pv_peak_power = pv_area.sum() * pv_efficiency  # in kW (required for simplified Eigenverbrauchsabschätzung)
    
        Gebaeude_ren_static.run_SIA_380_1(self.weather_data_sia)
        Gebaeude_ren_static.run_ISO_52016_monthly(self.weather_data_sia)
        Gebaeude_ren_static.run_dhw_demand()
        
        """Electicity demand detailed, according weekly and monthly occupancy shedules: They are missing, Needs to be checked, does not work!
        Generally questionable if reasonalbe, since SIA 2024 Bestandeswerte. """
        # unique_use_types = 1.1  #  Hardcoded scenarios['building use type'].unique() 
        # occupancy_schedules_dic = {}
        # for use_type in unique_use_types:
        #     occupancy_path = translations[translations['building use type'] == use_type]['occupancy schedule'].to_numpy()[0]
        #     occupancy_schedules_dic[use_type] = pd.read_csv(occupancy_path)
        # Gebaeude_static.run_SIA_electricity_demand(occupancy_schedules_dic[gebaeudekategorie_sia])
        """Simplyfied electrictiy demand for MFH according to sia 380/1 Tab. 12 (= SIA Bestandeswerte 2024)"""
        #TODO: Check if reasonable and eventually change it. (also couple to building usage)
        Gebaeude_ren_static.run_SIA_electricity_demand_simplifed()
        
        """Sizeing The Heating System, Always on Actual Weather data!"""
        weatherfile_path = f'{input_db}/weather_data/Zürich-hour_historic.epw'
        Gebaeude_ren_static.run_heating_sizing_384_201(weatherfile_path)
        self.nominal_heating_power_stat_ren = Gebaeude_ren_static.nominal_heating_power  # in W 
        """AJUST to total Sum! (existing Building and Add on)"""
    
        Gebaeude_ren_static.run_cooling_sizing()
        self.nominal_cooling_power_stat_ren = Gebaeude_ren_static.nominal_cooling_power # in W
        
        """Operational GHG, Needs to be ajusted!, BUG! -> Turn OFF PV!"""
        Gebaeude_ren_static.run_SIA_380_emissions(emission_factor_source=electricity_factor_source,
                                              emission_factor_source_UBP=electricity_factor_source_UBP,
                                              emission_factor_type=electricity_factor_type,
                                              weather_data_sia=self.weather_data_sia,
                                              energy_cost_source=energy_cost_source,
                                              country="KBOB") #config['country'] 
        
        # print('ueberpruefung Heat Electricity demand kWh/m2year', Gebaeude_static.heating_elec.sum())
       #TODO: Expand here the push back of informations
        self.heating_energy_demand_ren = Gebaeude_ren_static.heizwarmebedarf 
        self.grid_electricity_emissions_per_area_ren = Gebaeude_ren_static.grid_electricity_emissions
        self.operational_emissions_per_area_ren = Gebaeude_ren_static.operational_emissions
        self.heating_electricity_demand_per_area_ren = Gebaeude_ren_static.heating_elec
        self.electricity_demand_per_area_ren = Gebaeude_ren_static.net_electricity_demand

        self.Gebaeude_ren_static = Gebaeude_ren_static #All infos/methods of energy cacluclations can be accessed directly via self.Gebaeude_ren_static.variable/method

        # print('transmissionsverluste ', Gebaeude_ren_static.transmissionsverluste.sum())
        # print('lüftungsverluste ', Gebaeude_ren_static.luftungsverlust.sum())
        # print('interne_eintrage ', Gebaeude_ren_static.interne_eintrage.sum())
        # print('solare_eintrage ', Gebaeude_ren_static.solare_eintrage.sum())
        # print('monthly heizwärmebedarf: ', self.heating_energy_demand_ren)
        

        return 
       
        
    
#%% Embodied Emissions  
  
    def embodied_emissions_envelop_new(self):
        
        """Hardcoded_Values"""
        b_floor, set_back_reduction_factor, pv_type, \
        pv_efficiency,pv_area,pv_performance_ratio,pv_tilt,pv_azimuth,max_electrical_storage_capacity, \
        electricity_factor_source,electricity_factor_source_UBP,energy_cost_source,electricity_factor_type \
        = hardcoded_inputs()
        
        self.annualized_embodied_emissions_envelope_per_area_new,\
        self.annualized_embodied_emissions_envelope_upfront_per_area_new = eec.calculate_envelope_emissions(
                                              database=self.construction_db,
                                              RSP = self.RSP, 
                                              energy_reference_area=self.energy_reference_area_new,
                                              floors_ag = self.floors_ag_new,
                                              window_type = self.window_type_new , 
                                              total_window_area = self.window_areas_new.sum(), 
                                              wall_type_ag = self.wall_type_ag_new,
                                              total_wall_area_ag = self.wall_areas_ag_new.sum(), 
                                              roof_type = self.roof_type_new,
                                              total_roof_area = self.roof_area_new, 
                                              ceiling_to_basement_type = self.ceiling_to_basement_type_new, 
                                              floor_area = self.floor_area_new, 
                                              ceiling_type = self.ceiling_type_new,
                                              wall_type_bg = self.wall_type_bg_new,
                                              total_wall_area_bg = self.wall_areas_bg_new.sum(), 
                                              slab_basement = self.slab_basement_type_new,
                                              partitions_type = self.partitions_type_new,
                                              total_area_partitions = self.area_partitions_new,
                                              tilted_roof_type = self.tilted_roof_type_new,
                                              simplifed_LCA = self.simplifed_LCA,
                                              decarbonization_frac_2050 = self.embodied_emissions_decarbonization_fraction,
                                              int_finishings_replacement_at_intervention = True)
    
    
        
    def embodied_emissions_envelop_ren(self):
         
         """Hardcoded_Values"""
         b_floor, set_back_reduction_factor, pv_type, \
         pv_efficiency,pv_area,pv_performance_ratio,pv_tilt,pv_azimuth,max_electrical_storage_capacity, \
         electricity_factor_source,electricity_factor_source_UBP,energy_cost_source,electricity_factor_type \
         = hardcoded_inputs()
         
         self.annualized_embodied_emissions_envelope_per_area_ren,\
         self.annualized_embodied_emissions_envelope_upfront_per_area_ren = eec.calculate_envelope_emissions(
                                               database=self.construction_db,
                                               RSP = self.RSP, 
                                               energy_reference_area=self.energy_reference_area_ren,
                                               floors_ag = self.floors_ag_ren,
                                               window_type = self.window_type_ren , 
                                               total_window_area = self.window_areas_ren.sum(), 
                                               wall_type_ag = self.wall_type_ag_ren,
                                               total_wall_area_ag = self.wall_areas_ag_ren.sum(), 
                                               roof_type = self.roof_type_ren,
                                               total_roof_area = self.roof_area_ren, 
                                               ceiling_to_basement_type = self.ceiling_to_basement_type_ren, 
                                               floor_area = self.floor_area_ren, 
                                               ceiling_type = self.ceiling_type_ren,
                                               wall_type_bg = self.wall_type_bg_ren,
                                               total_wall_area_bg = self.wall_areas_bg_ren.sum(), 
                                               slab_basement = self.slab_basement_type_ren,
                                               partitions_type = self.partitions_type_ren,
                                               total_area_partitions = self.area_partitions_ren,
                                               tilted_roof_type = self.tilted_roof_type_ren,
                                               simplifed_LCA = self.simplifed_LCA,
                                               decarbonization_frac_2050 = self.embodied_emissions_decarbonization_fraction,
                                               int_finishings_replacement_at_intervention = self.int_finishings_replacement_at_intervention_ren)
         
    def embodied_emissions_envelop_demolished(self):
        """
        Calculates the Embodied emissions of the demolished building construction elements due to the intervention
        """
        
        """Hardcoded_Values"""
        b_floor, set_back_reduction_factor, pv_type, \
        pv_efficiency,pv_area,pv_performance_ratio,pv_tilt,pv_azimuth,max_electrical_storage_capacity, \
        electricity_factor_source,electricity_factor_source_UBP,energy_cost_source,electricity_factor_type \
        = hardcoded_inputs()
        
        self.annualized_embodied_emsissions_envelope_per_area_dem = eec.calculate_envelope_emissions_demolished(
                                              database=self.construction_db,
                                              RSP = self.RSP, 
                                              energy_reference_area=self.energy_reference_area_total,
                                              floors_ag = self.floors_ag_old,
                                              window_type = self.window_type_demo, 
                                              total_window_area = self.window_areas_old.sum(), 
                                              wall_type_ag = self.wall_type_ag_demo,
                                              total_wall_area_ag = self.wall_areas_ag_old.sum(), 
                                              roof_type = self.roof_type_demo,
                                              total_roof_area = self.roof_area_old, 
                                              ceiling_to_basement_type = self.ceiling_to_basement_type_demo, 
                                              floor_area = self.floor_area_old, 
                                              ceiling_type = self.ceiling_type_demo,
                                              wall_type_bg = self.wall_type_bg_demo,
                                              total_wall_area_bg = self.wall_areas_bg_old.sum(), 
                                              slab_basement = self.slab_basement_type_demo,
                                              partitions_type = self.partitions_type_demo,
                                              total_area_partitions = self.area_partitions_old,
                                              tilted_roof_type = self.tilted_roof_type_demo,
                                              simplifed_LCA = self.simplifed_LCA)
        
        
        
    
    
    def embodied_emissions_system_total(self):
        """Hardcoded_Values"""
        b_floor, set_back_reduction_factor, pv_type, \
        pv_efficiency,pv_area,pv_performance_ratio,pv_tilt,pv_azimuth,max_electrical_storage_capacity, \
        electricity_factor_source,electricity_factor_source_UBP,energy_cost_source,electricity_factor_type \
        = hardcoded_inputs()
        
        #relevant_volume_flow = max(self.ventilation_volume_flow, self.increased_ventilation_volume_flow) #TODO:vent flow SIA must be translated into a number, via datapreper? 
        relevant_volume_flow = self.increased_ventilation_volume_flow # TODO: AJUST HERE to the max criteria; SIA must be translated. 

        self.sum_up_whole_building_sys_capacity() #Call function to compute total size of systems
        
        self.annualized_embodied_impact_systems_per_area_total = eec.calculate_system_related_embodied_emissions_new(ee_database=self.systems_db,
                                                            gebaeudekategorie=self.gebaeudekategorie_sia,
                                                            energy_reference_area=self.energy_reference_area_total,
                                                            RSP = self.RSP ,
                                                            heizsystem=self.heating_system_new,
                                                            heat_emission_system=self.heat_emission_system_new,
                                                            heat_distribution=self.heat_distribution_new,
                                                            nominal_heating_power=self.nominal_heating_power_stat_total,
                                                            dhw_heizsystem=self.heating_system_dhw_new,
                                                            cooling_system = self.cooling_system_new,
                                                            cold_emission_system = self.cold_emission_system_new,
                                                            nominal_cooling_power=self.nominal_cooling_power_stat_total, #here changed form self.nominal_heating_power_stat_total  13.7. 
                                                            pv_area=pv_area,
                                                            pv_type=pv_type,
                                                            pv_efficiency=pv_efficiency,
                                                            has_mechanical_ventilation=self.has_mechanical_ventilation_new,
                                                            max_aussenluft_volumenstrom=relevant_volume_flow,
                                                            battery_capacity=max_electrical_storage_capacity,
                                                            decarbonization_frac_2050 = self.embodied_emissions_decarbonization_fraction)
        
        self.annualized_embodied_impact_systems_upfront_per_area_total = eec.calculate_system_related_embodied_emissions_upfront_new(ee_database=self.systems_db,
                                                            gebaeudekategorie=self.gebaeudekategorie_sia,
                                                            energy_reference_area=self.energy_reference_area_total,
                                                            RSP = self.RSP ,
                                                            heizsystem=self.heating_system_new,
                                                            heat_emission_system=self.heat_emission_system_new,
                                                            heat_distribution=self.heat_distribution_new,
                                                            nominal_heating_power=self.nominal_heating_power_stat_total,
                                                            dhw_heizsystem=self.heating_system_dhw_new,
                                                            cooling_system = self.cooling_system_new,
                                                            cold_emission_system = self.cold_emission_system_new,
                                                            nominal_cooling_power=self.nominal_cooling_power_stat_total, #here changed form self.nominal_heating_power_stat_total  13.7. 
                                                            pv_area=pv_area,
                                                            pv_type=pv_type,
                                                            pv_efficiency=pv_efficiency,
                                                            has_mechanical_ventilation=self.has_mechanical_ventilation_new,
                                                            max_aussenluft_volumenstrom=relevant_volume_flow,
                                                            battery_capacity=max_electrical_storage_capacity,
                                                            decarbonization_frac_2050 = self.embodied_emissions_decarbonization_fraction)
        
        
   
        
