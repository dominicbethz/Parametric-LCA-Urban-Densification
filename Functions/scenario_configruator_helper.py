#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 29 09:41:44 2024

@author: dominicbuettiker
"""

import numpy as np
import pandas as pd
import time
import os
import sys
import copy
import site 
import time

def envelope_assignement(construction_configurations_db,category, core, insulation):
    
    """This function assignes the outer moste layer, based on the insulation type"""
    
    if len(construction_configurations_db[(construction_configurations_db['core']==core)]) == 0: #No special entry for this core  #here was 1!
        #Standart configruation, specified in construction_configurations_db
        construction = construction_configurations_db[(construction_configurations_db['Class']=='default') & (construction_configurations_db['Category']==category) & (construction_configurations_db['insulation']==insulation)]
      
    
    elif len(construction_configurations_db[(construction_configurations_db['core']==core) & (construction_configurations_db['insulation'].isna())])== 1 : #replace NONE
        #Special configuration, independant of insulatino type
        construction = construction_configurations_db[(construction_configurations_db['core']==core) & (construction_configurations_db['Category']==category)]
        #print('test1')
    elif len(construction_configurations_db[(construction_configurations_db['core']==core) & (construction_configurations_db['insulation']==insulation)])==1:  
        #Special configuration, dependant of insulatino type
        construction = construction_configurations_db[(construction_configurations_db['core']==core) & (construction_configurations_db['insulation']==insulation) & (construction_configurations_db['Category']==category)]
        #print('test2')
    elif len(construction_configurations_db[(construction_configurations_db['core']==core) & (construction_configurations_db['insulation']==insulation)])==0:  
        #There is no special configruation for this specific material with the insulation type of the input -> take default configuration, since default will fit this insulation material
        construction = construction_configurations_db[(construction_configurations_db['Class']=='default') & (construction_configurations_db['Category']==category) & (construction_configurations_db['insulation']==insulation)]
        #print('test3')
    else: 
        sys.exit('invalid assignemen to exterior materials')
    
    exterior_layer = construction['exterior_layer'].tolist()
    
    if len(exterior_layer) == 0 :
        sys.exit('for the core and insulation no exterior layer (e.g. facade / roof, ...) could have been assiged')
    if len(exterior_layer) > 1:
        print('exterior_layer: ',exterior_layer)
        print('category, core, insulation: ',category, core, insulation)
        sys.exit('no assignement for exterior layer possible, more than one combination avaliable')

    return exterior_layer[0]
    


def intervention_scenario(       Building, 
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
                                 
                                 #later intruduced prameters: 
                                 int_finishings_replacement_at_intervention_ren = False, 
                                 ): 
   

    """
    Function that configrurates the detailed Intervention scenario, which are use in the energy demand simulation and 
    emissions Calculations. All System and Envelope properties are assigned here. 
    """
    
    
    #All envelop lists are sorted like "old_envelop" 
    envelop_old = [Building.window_type_old,Building.wall_type_ag_old,
                   Building.roof_type_old,Building.ceiling_to_basement_type_old, 
                   Building.ceiling_type_old, Building.wall_type_bg_old, Building.slab_basement_type_old, 
                   Building.partitions_type_old, Building.tilted_roof_type_old] 
                  
    
    envelop_demolished = [['empty_layer']*4 for _ in range(len(envelop_old))] #Important all Materials must contain 3 Layers: Core, Exterior and Interior; 
    envelop_demolished[0] = 'empty_layer' # Windows have only one layer
    envelop_new = [['empty_layer']*4 for _ in range(len(envelop_old))] #
    envelop_new[0] = 'empty_layer' # Windows have only one layer
    envelop_renovated = [['empty_layer']*4 for _ in range(len(envelop_old))] #
    envelop_renovated[0] = 'empty_layer' # Windows have only one layer
    
    iterator_envelop_ren = [1,2,3] #iterates over the changed envelop constructions due to insulation in case of a retrofit: walls_ag, roof, ceiling_to_basement
    iterator_extension_old_part = [1,3] #iterates over exterior walls and ceiling to basement 
    iterator_extension_new_part = [1,2] #iterates over exterior walls and roof
    iterator_categorys = [None,'wall_type_ag','roof_type','ceiling_to_basement_type']
    iterator_interior_ren = [4,7] #only for internal ceilings and partitions

    
    system_old = [Building.heating_system_old,
                  Building.heating_system_dhw_old,
                  Building.heat_emission_system_old,
                  Building.heat_distribution_old]
    #Order of the system list: 
    #Heating_system_new,heating_system_dhw_new,heat_emission_system_new,heat_distribution_new,cooling_system_new,cold_emission_system_new,has_mechanical_ventilation_new
    system_total = [None]*7 # attention hartcoded, need to be changed, if system vector gets larger!
    system_demolished = [None]*len(system_old) #heating system, dhw system, heat_emission_system, heat_distribution_old
    
    construction_type_new_name = None 
    if Intervention_scenario == 2:
        construction_type_new_name = construction_type_new['construction_name']
    if Intervention_scenario == 3:
        construction_type_new_name = construction_type_add_storeys['construction_name']
    
        
    Building.define_scenario(Intervention_scenario,insulation_type_ren, insulation_thickness_ren,
                             construction_type_new_name,insulation_type_new,insulation_thickness_new) 
    #This functino mainly writes infomations to the object building, which is later extracted for documentation (e.g. Insulation_thisness and type)
                        
    """
    TODO's: 
    
    
    """
    
    if Intervention_scenario == 0:
        
        
        ######## Return to Simulation_Setup ##########
        #IMPORTANT: since the scenario no retrofit is similar to the retrofit scenario, it is simulated with the same functions of the retrofit sceanrio
       
        # Envelop propierties of old Building
        args = envelop_old + [Building.infiltration_volume_flow_old, Building.roof_area_old, Building.thermal_bridge_add_on_old]
        Building.refurbishment_envelop(*args)
        
        # System properties of old Building
        args = system_old + ['None', 'None', False] #original building could not hav a cooling system and no mechanical ventilation
        Building.new_systems(*args)
        
        #Demolished Envelop parts: 
        Building.demolished_envelop(*envelop_demolished)
        #Demolished System parts: 
        Building.demolished_systems(*system_demolished)
        
        ######### CALCULATE U-VALUES #############
        Building.calc_uvalues_renovation(construction_db)
        ######### Further Basic Setup#############
        Building.whole_building_featues()
    
   
#################################################################   
    
    
    if Intervention_scenario == 1: #Renovation of Envelop: Only includes Insulation and change of Windows + system 
        
        envelop_renovated = copy.deepcopy(envelop_old) # Take old envelope as the Basis of the renovated Building
        roof_area_ren = Building.roof_area_old
        
        #TODO: How to handle the original scenario: after a first service life. 
            
        ############## ENVELOP##################
        #insulation_scenario -> Add isulation
        if insulation_type_ren != 'original':
            insulation_name = 'insulation_' + insulation_type_ren + '_' + insulation_thickness_ren
            for i in iterator_envelop_ren: 
                envelop_renovated[i][2] = insulation_name # Change the insulation 
                demolished = envelop_old[i][2]
                envelop_demolished[i][2] = demolished# Add the demolished layer to the demolished part
                #Add the outer most layer of the envelop (based on the core and the insulation type, specifyed in the construction_configurations_db)
                if simplifed_LCA==False: 
                    envelop_renovated[i][3] = envelope_assignement(construction_configurations_db, iterator_categorys[i],envelop_renovated[i][1],insulation_type_ren)
                    demolished = envelop_old[i][3]
                    envelop_demolished[i][3] = demolished
        
        #Window scenario -> Change window
        if window_type_ren != 'original':
            envelop_renovated[0] = window_type_ren
            envelop_demolished[0] = envelop_old[0] 
            
        #if there is interior renovation at the intervention, the refurbished layers are assined to the demolished building
        if int_finishings_replacement_at_intervention_ren == True:
            for i in iterator_envelop_ren: #wall ag, ceiling to basement, roof
                demolished = envelop_old[i][0]
                envelop_demolished[i][0] = demolished
            for i in iterator_interior_ren: #internal ceilings, partition walls
                for j in [0,3]: #here both internal layers are replaced! 
                    demolished = envelop_old[i][j]
                    envelop_demolished[i][j] = demolished
                 
        
        ################# SYSTEMS #############
        #Replacement heating_system 
        if heating_system_sc != 'original':
            system_total[0] = heating_system_sc
            system_demolished[0] = system_old[0]
        else: 
            system_total[0] = system_old[0]
        #Repalcment heating dhw
        if heating_system_dhw_sc != 'original':
            system_total[1] = heating_system_dhw_sc
            system_demolished[1] = system_old[1]
        else: 
            system_total[1] = system_old[1]
        #Replacement Heat emissions system
        if heat_emission_system_sc != 'original': 
            system_total[2] = heat_emission_system_sc
            system_demolished[2] = system_old[2]
        else: 
            system_total[2] = system_old[2]
        #Replacement Heat distribution system
        if heat_distribution_system_sc != 'original': #Heat distribution system
            system_total[3] = heat_distribution_system_sc
            system_demolished[3] = system_old[3]
        else: 
            system_total[3] = system_old[3]
        
        #Cooling and mechanical ventilation have no base scenario
        system_total[4] = cooling_system_sc
        system_total[5] = cold_emission_system_sc
        system_total[6] = has_mechanical_ventilation_sc
        
        
        
        ######## Return to Simulation_Setup ##########
        # Envelop propierties of Renovated Building
        args = envelop_renovated + [infiltration_volume_flow_ren, roof_area_ren, thermal_bridge_add_on_ren]
        Building.refurbishment_envelop(*args)
        # System properties of Renovated Building
        Building.new_systems(*system_total)
        
        #Demolished Envelop parts: 
        Building.demolished_envelop(*envelop_demolished)
        #Demolished System parts: 
        Building.demolished_systems(*system_demolished)
        
        ######### CALCULATE U-VALUES #############
        Building.calc_uvalues_renovation(construction_db)
        ######### Further Basic Setup#############
        Building.whole_building_featues()

        
#################################################################      
        

    if Intervention_scenario == 2: #Replacement Construction
        # TODO: Introduce invalide combinatinos: e.g 
       
        # Demolishment of Envelop and system 
        envelop_demolished = envelop_old
        system_demolished = system_old
        
        ########### Geometry #############
        floors_ag_new = Building.floors_ag_old + add_storeys_new
        l_w_scale = np.sqrt(1+change_footprint_area)# calculates the general stretch factor of width and length 
        width_new = Building.width_old  * l_w_scale * (1+change_orientation)
        length_new = Building.length_old * l_w_scale / (1+change_orientation)
        floors_bg_new = Building.floors_bg_old #NO CHANGE OF FLOORS BG!
        heated_fraction_ag_new = Building.heated_fraction_ag_old #NO CHANGE OF FRACTION HEATED AREA!
        fraction_partitions_new = construction_type_new['fraction_partitions']
        
        
        ############## ENVELOP##################
        envelop_new[0] =  window_type_new #Add Window to envelop_new definition 
        keys = list(construction_type_new.keys())[:8] # All envelop types
        for i, key in enumerate(keys): #Add the construction to the envelop_new definition 
            envelop_new[i+1] = construction_type_new[key]
        
        insulation_name = 'insulation_' + insulation_type_new + '_' + insulation_thickness_new
        for i in iterator_envelop_ren:  # Add the Insulatino according to the input (type and thickness)
            envelop_new[i][2] = insulation_name
            #Add the outer most layer of the envelop (based on the core and the insulation type, specifyed in the construction_configurations_db)
            #TODO: Frage ob es für neubauten sinn macht, spezielle konfigruationen zu ermöglichen, dann dürfen diese nicht "überschreiben werden". D.h. bevor die überschreibung statt findet, muss überprüft werden ob die konfiguration ok is (mit seperatem excel)
            if simplifed_LCA==False: 
                envelop_new[i][3] = envelope_assignement(construction_configurations_db, iterator_categorys[i],envelop_new[i][1],insulation_type_new)
            
        
        #Other envelop properties 
        infiltration_volume_flow_new = construction_type_new['infiltration_volume_flow']
        if thermal_bridge_add_on_new == 'default': #if not thermal bridge add no is specified, than the value form the standart value from the construction is used 
            thermal_bridge_add_on_new = construction_type_new['thermal_bridge_add_on']
        heat_capacity_per_energyreferencearea_new = construction_type_new['heat_capacity_per_energyreferencearea']
       
        
        ################# SYSTEMS #############
        #Filters invalid Combination
        if 'original' in [heating_system_sc,heating_system_dhw_sc,heat_emission_system_sc,heat_distribution_system_sc,cooling_system_sc,cold_emission_system_sc,has_mechanical_ventilation_sc]:
            Building.invalid_combination()
            print('invalid system combination new construction: ORIGINAL was tried to be assessed')
            return 
        
        
        system_total[0] = heating_system_sc
        system_total[1] = heating_system_dhw_sc
        system_total[2] = heat_emission_system_sc
        system_total[3] = heat_distribution_system_sc
        system_total[4] = cooling_system_sc
        system_total[5] = cold_emission_system_sc
        system_total[6] = has_mechanical_ventilation_sc

        

        
        ######## Return to Simulation_Setup ##########
        #Geometry:
        Building.new_construction_geometry(window_to_wall_ratio_new,floors_ag_new,floors_bg_new,width_new,length_new,heated_fraction_ag_new,fraction_partitions_new)  
        #Demolished Envelop parts: 
        Building.demolished_envelop(*envelop_demolished)
        #Demolished System parts: 
        Building.demolished_systems(*system_demolished)
        # Envelop propierties of New Building
        args = envelop_new + [infiltration_volume_flow_new,thermal_bridge_add_on_new,heat_capacity_per_energyreferencearea_new]
        Building.new_construction_envelop(*args)
        # System properties of Renovated Building
        Building.new_systems(*system_total)
        
        ######### CALCULATE U-VALUES #############
        Building.new_construction_uvalues(construction_db)
        ######### Further Basic Setup#############
        Building.whole_building_featues()
        

#################################################################   
    

    if Intervention_scenario == 3: #Extension: Add stories
    
    #TODO: Question how to handel the change in the Energy reference area, since in this case it is directly coupled to the amount of stories
        
    ########## INVALID CONFIGURATIONS DETECTION ##########
        if construction_type_add_storeys['construction_type'] =='heavy_weight':
            sys.exit("ivalid construction for add stories: heavy_weight was choosen")
            # to be changed later: set result to nan for sensitivity analysis
            return
        if add_storeys_top_up < 1:
            sys.exit("invalid geometry for the sceanrio add stories: floor added < 1!")
            # to be changed later: set result to nan for sensitivity analysis
            return
    
        ########### Geometry AREA EXPANSION #############
        floors_ag_new = add_storeys_top_up
        width_new = Building.width_old
        length_new = Building.length_old
        floors_bg_new = 0 #NO BG Floor, since adding stories
        heated_fraction_ag_new = Building.heated_fraction_ag_old #NO CHANGE OF FRACTION HEATED AREA!
        fraction_partitions_new = construction_type_add_storeys['fraction_partitions']
        #TODO: overwrite energy reference area!
        
        
        
        ############## ENVELOP RENOVATED ##################
        envelop_renovated = copy.deepcopy(envelop_old) # Take old envelope as the Basis of the renovated Building
        roof_area_ren = Building.roof_area_old
        
        #insulation_scenario: replacement 
        if insulation_type_ren != 'original':
            insulation_name = 'insulation_' + insulation_type_ren + '_' + insulation_thickness_ren
            for i in iterator_extension_old_part: 
                envelop_renovated[i][2] = insulation_name # Change the insulation 
                demolished = envelop_old[i][2]
                envelop_demolished[i][2] = demolished #Add the demolished layer to the demolished part
                #Add the outer most layer of the envelop (based on the core and the insulation type, specifyed in the construction_configurations_db)
                if simplifed_LCA==False: 
                    envelop_renovated[i][3] = envelope_assignement(construction_configurations_db, iterator_categorys[i],envelop_renovated[i][1],insulation_type_ren)
                    demolished = envelop_old[i][3]
                    envelop_demolished[i][3] = demolished
        
        #Window scenario: replacement
        if window_type_ren != 'original':
            envelop_renovated[0] = window_type_ren
            envelop_demolished[0] = envelop_old[0] 
            
        #Roof demolishment of the existing building for the extension: 
        #Layer 3 and 4 of roof_type are removed. (insulation and boards / Flat roof finishing) 
        #Layer 1 & 2 (finishing and ceiling) is kept. 
        for i in [2,3]:
            envelop_renovated[2][i] = 'empty_layer' # Remove original insulation and roof finishing
            envelop_demolished[2][i] = envelop_old[2][i] #Add the demolished layer to the demolished part
       
        #Removement of tilted roof (if there is one): 
        if envelop_renovated[8]!= None:

            for i in range(len(envelop_renovated[8])):
                envelop_renovated[8][i] = 'empty_layer' # Remove original insulation and roof finishing
                envelop_demolished[8][i] = envelop_old[8][i] #Add the demolished layer to the demolished part
        
        #if there is interior renovation at the intervention, the refurbished layers are assined to the demolished building
        if int_finishings_replacement_at_intervention_ren == True:
            for i in iterator_envelop_ren: #wall ag, ceiling to basement, roof
                demolished = envelop_old[i][0]
                envelop_demolished[i][0] = demolished
            for i in iterator_interior_ren: #internal ceilings, partition walls
                for j in [0,3]: #here both internal layers are replaced! 
                    demolished = envelop_old[i][j]
                    envelop_demolished[i][j] = demolished
        
        ############## ENVELOP EXPANSION ##################
        envelop_new[0] =  window_type_new #Add Window to envelop_new definition 
        keys = ["wall_type_ag", "roof_type", "ceiling_to_basement_type", "ceiling_type"] 
        
        for i, key in enumerate(keys): #Add the construction to the envelop_new definition: basement elements are excluded, since it is a extension
            envelop_new[i+1] = construction_type_add_storeys[key]
        
        envelop_new[7] = construction_type_add_storeys["partitions_type"]
        envelop_new[8] = construction_type_add_storeys["tilted_roof_type"]
         # TODO: add here partitions and titlted roof ! But attention, then exclud it from the iterator, since not directly in the list -> add it seperatrly 
        
        insulation_name = 'insulation_' + insulation_type_new + '_' + insulation_thickness_new
        for i in iterator_extension_new_part:  # Add the Insulation according to the input (type and thickness)
            envelop_new[i][2] = insulation_name
            
            #Add the outer most layer of the envelop (based on the core and the insulation type, specifyed in the construction_configurations_db)
            if simplifed_LCA==False: 
                envelop_new[i][3] = envelope_assignement(construction_configurations_db, iterator_categorys[i],envelop_new[i][1],insulation_type_new)
                
        
        # Remove insulation, finishing, and sturcture core, of "ceiling to basement" since it is not used for adding storeis (only flooring ) 
        for i in [1,2,3]: 
            envelop_new[3][i] = 'empty_layer' 
        
        #Other envelop properties 
        infiltration_volume_flow_new = construction_type_add_storeys['infiltration_volume_flow']
        if thermal_bridge_add_on_new == 'default': #if not thermal bridge add no is specified, than the value form the standart value from the construction is used 
            thermal_bridge_add_on_new = construction_type_add_storeys['thermal_bridge_add_on']
        heat_capacity_per_energyreferencearea_new = construction_type_add_storeys['heat_capacity_per_energyreferencearea']
       

       
        
       ################# SYSTEMS #############
        #Filters invalid Combination
        if 'original' in [heating_system_sc,heating_system_dhw_sc,heat_emission_system_sc,heat_distribution_system_sc,cooling_system_sc,cold_emission_system_sc,has_mechanical_ventilation_sc]:
            Building.invalid_combination()
            print('invalid system combination new construction: ORIGINAL was tried to be assessed')
            return 
       
        #TODO: Questino how tho handle the situation, where the emission system in the existing building stays the same? Split in capacity new to calc the emission systems parts?
        system_demolished[0] = system_old[0]
        system_demolished[1] = system_old[1]
        system_demolished[2] = system_old[2]
        system_demolished[3] = system_old[3]
        
        system_total[0] = heating_system_sc
        system_total[1] = heating_system_dhw_sc
        system_total[2] = heat_emission_system_sc
        system_total[3] = heat_distribution_system_sc
        system_total[4] = cooling_system_sc
        system_total[5] = cold_emission_system_sc
        system_total[6] = has_mechanical_ventilation_sc
        
        
        ######## Return to Simulation_Setup ##########
        #Geometry new parts:
        Building.new_construction_geometry(window_to_wall_ratio_new,floors_ag_new,floors_bg_new,width_new,length_new,heated_fraction_ag_new,fraction_partitions_new)  
        
        #Envelop/Construction new parts: 
        args = envelop_new + [infiltration_volume_flow_new,thermal_bridge_add_on_new,heat_capacity_per_energyreferencearea_new]
        Building.new_construction_envelop(*args)
        #Envelop renovated
        args = envelop_renovated + [infiltration_volume_flow_ren, roof_area_ren, thermal_bridge_add_on_ren]
        Building.refurbishment_envelop(*args)
        
        # System properties of Renovated Building
        Building.new_systems(*system_total)
        
        #Demolished Envelop parts: 
        Building.demolished_envelop(*envelop_demolished)
        #Demolished System parts: 
        Building.demolished_systems(*system_demolished)
        
        ######### CALCULATE U-VALUES #############
        Building.new_construction_uvalues(construction_db)
        Building.calc_uvalues_renovation(construction_db)
        Building.modify_u_values_due_to_extension()
        
        
        ######### Further Basic Setup#############
        Building.whole_building_featues()
        
        

#################################################################      
    if Intervention_scenario not in [0, 1, 2, 3,]:
        print('Wrong Scenario, simualtion stopped')
        return
        
    return 


    



def call_simulations(Building, Intervention_scenario):
    """
    This Function calls the corresponding simulations
    TODO: embodied emissions systems demolished -> neglected since marginal (based on represantive hand calculation)


    """
    
    if Intervention_scenario == 0: #No intervention now
        #TODO: In the databse GWP prod must be 0 for original components. Question how to handle minimal retrofits (e.g. repaint facade), since this is a frequent measure. 
        #The Building properties are calculated with the renovated setup. 
        #Operational Emissions and Energy demands
        Building.operational_energy_demand_and_emissions_renovated_areas()
        
        #Embodied Emissions
        Building.embodied_emissions_envelop_ren()
        Building.embodied_emissions_system_total()
        
        #Demolished emissions
        Building.embodied_emissions_envelop_demolished()
        #TODO: sys demolished
        
        #Sum all up and store data
        Building.data_collector()
        
    
    if Intervention_scenario == 1: #Refurbishment
        time_1 = time.time()
        #Operational Emissions and Energy demands
        Building.operational_energy_demand_and_emissions_renovated_areas()
        time_2 = time.time()
        #Embodied Emissions
        Building.embodied_emissions_envelop_ren()
        time_3 = time.time()
        Building.embodied_emissions_system_total()
        time_4 = time.time()
        #Demolished emissions
        Building.embodied_emissions_envelop_demolished()
        time_5 = time.time()
        #TODO: sys demolished
        
        #Sum all up and store data
        Building.data_collector()
        
        time_6 = time.time()
        # print('time e demand & op emmissions: ',time_2-time_1)
        # print('emb emissions envelop: ',time_3-time_2)
        # print('emb emissions systems: ',time_4-time_3)
        # print('data collector ',time_6-time_5)
    
    if Intervention_scenario == 2: #New Construction 
        #Operational Emissions and Energy demands
        Building.operational_energy_demand_and_emissions_new_areas()
        #Embodied Emissions
        Building.embodied_emissions_envelop_new()
        Building.embodied_emissions_system_total()
        #Demolished Emissions
        Building.embodied_emissions_envelop_demolished()
        #TODO: sys demolished
        
        #Sum all up and store data
        Building.data_collector()
    
    if Intervention_scenario == 3: #Extenstion
    
        #Operational Emissions and Energy demands
        Building.operational_energy_demand_and_emissions_renovated_areas()
        Building.operational_energy_demand_and_emissions_new_areas()
        
        #Embodied Emissions
        Building.embodied_emissions_envelop_ren()
        Building.embodied_emissions_envelop_new()
        Building.embodied_emissions_system_total()
       
        #Demolished Emissions
        Building.embodied_emissions_envelop_demolished()
        #TODO: sys demolished
        
        #Sum all up and store data
        Building.data_collector()
        
    
    if Intervention_scenario not in [0, 1, 2, 3]:
       print('Scenario Wrong')
       quit()
      
    return 
    
    
    
    