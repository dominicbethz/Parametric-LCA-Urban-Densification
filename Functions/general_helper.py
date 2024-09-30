#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  4 14:47:10 2024

@author: dominicbuettiker
"""

import numpy as np
import pandas as pd
#import sys
#sys.path.append(f"{main_path}/SIA_380_1") #Functions directly used from ITA: Energy Calculation 
import data_prep as dp


def basic_setup_params(input_db):
    """
    This Function specifys the basic simulatino parameters, can be overwritten afterwords 
    (most of them are, if not in constant table explained in Thesis)
    param: input_db: path to input databses 
    """
    
    """Fix Parameters General"""
    regelung = "andere"  # oder "Referenzraum" oder "andere"
    anlagennutzungsgrad_wrg = 0.0  # SIA 380-1 Tab 23  Rückgewinnung Wärme (Lüftung). DEFAULT: 0, keine Wärmerückgewinnung
    korrekturfaktor_luftungs_eff_f_v = 1.0  # zwischen 0.8 und 1.2 gemäss SIA380-1 Tab 24 (Lüftungseffektivität ), DEFAULT: 1, Lüftung ungeregelt/ Fensterlüftung
    ventilation_volume_flow = 0.7 # give a number in m3/(hm2) or select "SIA" to follow SIA380-1 code (0.7 for MFH). ATTENTION: IF SIA: INFILTRATION IS NOT TAKEN INTO ACCOUNT!
    increased_ventilation_volume_flow = 1.5 # give a number in m3/hm2, this volume flow is used when cooling with outside air is possible
    area_per_person = "SIA"  # give a number or select "SIA" to follow the SIA380-1 code (typical for MFH 40)
    combustion_efficiency_factor_new = 1 # To ajust Combustion efficency, if DEFAULT = 1, standart efficency values (in data_prep.py) are used. like 0.88 for gasboiler 
    combustion_efficiency_factor_old = 0.8 #Never used acutally, should be lower than 1, since assuming that the old boilers are not condensing

    #THIS TWO PARAMETERS ARE OVERWRITTEN BY THE CASESTUDIES!
    window_orientations = np.array(["N", "E", "S", "W"], dtype = str) # or np.array(["NE", "SE", "SW", "NW"], dtype = str)
    height_floors = 3 #in meters


    """Fix Parameters Building_Location"""
    hohe_uber_meer = 500 # Eingabe
    gebaeudekategorie_sia = 1.1 #MFH

    """Exogenous_Parameters_Building"""

    heating_setpoint = 20  # number in deC or select "SIA" to follow the SIA380-1 code
    cooling_setpoint = 26 
    heat_pump_efficiency = 0.55 #Here changed to 0.55 2.7. 2024 -> according to linus paper. 0.35 #Exergy efficency of Heatpump 
    shading_factor_season = np.array([0.8, 0.8, 0.8, 0.8],dtype=float) #from 0 to 1, 1 no shading, There is some shading, but no seasonal variation 
    RSP = 60 #According SIA 2032


    """Exogenous_Parameters_Environement"""
    electricity_decarbonization_factor = 1 #1 = no decarbonization 
    #weather_file: ONLY one (current) weather file, since basic setup of parameters 
    weatherfile_path = f'{input_db}/weather_data/Zürich-hour_historic.epw' # f'{input_db}/weather_data/Zürich-hour_historic.epw' # f'{input_db}/weather_data/Zürich-hour-current-Meteonorm.epw'

    epw_labels = ['year', 'month', 'day', 'hour', 'minute', 'datasource', 'drybulb_C', 'dewpoint_C', 'relhum_percent',
                      'atmos_Pa', 'exthorrad_Whm2', 'extdirrad_Whm2', 'horirsky_Whm2', 'glohorrad_Whm2',
                      'dirnorrad_Whm2', 'difhorrad_Whm2', 'glohorillum_lux', 'dirnorillum_lux', 'difhorillum_lux',
                      'zenlum_lux', 'winddir_deg', 'windspd_ms', 'totskycvr_tenths', 'opaqskycvr_tenths', 'visibility_km',
                      'ceiling_hgt_m', 'presweathobs', 'presweathcodes', 'precip_wtr_mm', 'aerosol_opt_thousandths',
                      'snowdepth_cm', 'days_last_snow', 'Albedo', 'liq_precip_depth_mm', 'liq_precip_rate_Hour']
    weather_file_dict_headers = {}
    weather_file_dict_bodies = {}
    weather_sia_dict = {}
    unique_weather_paths = [weatherfile_path] #Create here list with all weather files (scenarios)


    for unique_path in unique_weather_paths:
        weather_file_dict_headers[unique_path] = pd.read_csv(unique_path, header=None, nrows=1)
        weather_file_dict_bodies[unique_path] = pd.read_csv(unique_path, skiprows=8, header=None, names=epw_labels)
        weather_sia_dict[unique_path] = dp.epw_to_sia_irrad(weather_file_dict_headers[unique_path],
                                                            weather_file_dict_bodies[unique_path])

    #Selecthion of the historic scenario for sizing the heating system: zurich Historic
    weather_data_sia = weather_sia_dict[weatherfile_path]

    
    return regelung,anlagennutzungsgrad_wrg,korrekturfaktor_luftungs_eff_f_v,ventilation_volume_flow,increased_ventilation_volume_flow,area_per_person,\
           combustion_efficiency_factor_new,combustion_efficiency_factor_old,window_orientations,height_floors,hohe_uber_meer,gebaeudekategorie_sia,\
           heating_setpoint,cooling_setpoint,heat_pump_efficiency,shading_factor_season,RSP, electricity_decarbonization_factor,weatherfile_path, weather_data_sia


def set_new_constructions(typ):
    """
    This Function stores some construction configurations for new buildings. 
    
    """
    return 

def get_closest_interval(value, intervals, prefer='lower'):
    """
    Functinon to get the nearest interval: to identify the GWP_bio_factors. 
    It takes always the lower one: e.g. if interval 10, 20 and value=15 -> it takes 10
    """
    distances = [abs(x - value) for x in intervals]
    min_distance = min(distances)
    closest_intervals = [x for x, d in zip(intervals, distances) if d == min_distance]
    
    if len(closest_intervals) > 1:
        if prefer == 'lower':
            return min(closest_intervals)
        elif prefer == 'higher':
            return max(closest_intervals)
    else:
        return closest_intervals[0]


def get_factor(rotation_period, storage_period, GWP_bio_factors):
    """
    Function to get the factor from the GWP_bio_factors
    Based on the Table of Guest et. al. 2013
    """
    rotation_intervals = GWP_bio_factors.index.to_list()
    storage_period_intervals = GWP_bio_factors.columns.to_list()

    closest_rotation = get_closest_interval(rotation_period, rotation_intervals)
    closest_storage_period = get_closest_interval(storage_period, storage_period_intervals)

    return GWP_bio_factors.loc[closest_rotation, closest_storage_period]


def assign_gwp_bio_factor(RSP,construction_db,GWP_bio_factors):
    """
    Function assigns GWP bio Factor in a database, based ond RSL (ref. service life of component) and Rotation_time_bio of dataframe. 
    If RSL = RSP, (RSP: ref. service period building), the RSP value is used. 
    """
    
    construction_db['GWP_Bio'] = 0.0

    for construction_db_index, construction_db_values in construction_db.iterrows(): #SKIP nan rows. 
            if ((str(construction_db['Rotation_time_bio'][construction_db_index]).isnumeric())):
                if construction_db['RSL'][construction_db_index] == 'RSP':
                    RSL = RSP
                else: 
                    RSL = construction_db['RSL'][construction_db_index]
                construction_db.loc[construction_db_index, 'GWP_bio_factor'] =  get_factor(construction_db['Rotation_time_bio'][construction_db_index],RSL, GWP_bio_factors)
                construction_db.loc[construction_db_index,'GWP_Bio'] = construction_db.loc[construction_db_index,'GWP_bio_factor']*construction_db.loc[construction_db_index, 'CO2_bio_stored'] #calculates GWP_Bio
            else: continue 
    
    
    return construction_db


def casestudy_setup(case_study_configurations,CASE):
    """
    This Function reads the configurations of the casestudies out of the excel sheet
    """
    
    
    infiltration_volume_flow_old = case_study_configurations['infiltration_volume_flow_old'][CASE]
    thermal_bridge_add_on_old = case_study_configurations['thermal_bridge_add_on_old'][CASE]

    height_floors = case_study_configurations['height_floors'][CASE]
    window_orientations = str(case_study_configurations['window_orientations'][CASE]).split(",")
    window_to_wall_ratio_old = case_study_configurations['window_to_wall_ratio_old'][CASE]
    floors_ag_old = case_study_configurations['floors_ag_old'][CASE]
    floors_bg_old = case_study_configurations['floors_bg_old'][CASE]
    width_old = case_study_configurations['width_old'][CASE]
    length_old = case_study_configurations['length_old'][CASE]
    heated_fraction_ag_old = case_study_configurations['heated_fraction_ag_old'][CASE]
    fraction_partitions_old = case_study_configurations['fraction_partitions_old'][CASE]
   
    window_type_old =  case_study_configurations['window_type_old'][CASE] 
    wall_type_ag_old =  str(case_study_configurations['wall_type_ag_old'][CASE]).split(",")
    roof_type_old = str(case_study_configurations['roof_type_old'][CASE]).split(",")
    ceiling_to_basement_type_old = str(case_study_configurations['ceiling_to_basement_type_old'][CASE]).split(",")
    ceiling_type_old = str(case_study_configurations['ceiling_type_old'][CASE]).split(",")
    wall_type_bg_old = str(case_study_configurations['wall_type_bg_old'][CASE]).split(",")
    slab_basement_type_old = str(case_study_configurations['slab_basement_type_old'][CASE]).split(",")
    partitions_type_old =  str(case_study_configurations['partitions_type_old'][CASE]).split(",")
    if partitions_type_old[0] == 'nan': # change to None, if there are no partitions
        partitions_type_old = None
    tilted_roof_type_old = str(case_study_configurations['tilted_roof_type_old'][CASE]).split(",")
    if tilted_roof_type_old[0] == 'nan': # change to None, if there is no tilted roof 
        tilted_roof_type_old = None
   
    
    heat_capacity_per_energyreferencearea_old = case_study_configurations['heat_capacity_per_energyreferencearea_old'][CASE]

    heating_system_old= case_study_configurations['heating_system_old'][CASE]
    heating_system_dhw_old =  case_study_configurations['heating_system_dhw_old'][CASE]
    heat_emission_system_old =  case_study_configurations['heat_emission_system_old'][CASE]
    heat_distribution_old =  case_study_configurations['heat_distribution_old'][CASE]
    
    return infiltration_volume_flow_old,thermal_bridge_add_on_old,height_floors,window_orientations,window_to_wall_ratio_old,floors_ag_old, \
            floors_bg_old,width_old,length_old,heated_fraction_ag_old,fraction_partitions_old,\
            window_type_old,wall_type_ag_old,roof_type_old,ceiling_to_basement_type_old,\
            ceiling_type_old,wall_type_bg_old,slab_basement_type_old,partitions_type_old,tilted_roof_type_old,\
            heat_capacity_per_energyreferencearea_old, heating_system_old,heating_system_dhw_old,heat_emission_system_old,heat_distribution_old
 
    

def multiple_scenario_configurator(scenario_db,intervention):
    """ 
    THIS FUNCTINO  is used in the robust assessment main file (multi_core_main_roubst_assessment.py) to read given configuration out of the excel sheet
    
    """
    
    scenario_group =                scenario_db['scenario_group'][intervention]
    label =                         scenario_db['label'][intervention]
    scenario =                      scenario_db['scenario'][intervention]
    original_building_archetype =   scenario_db['original_building_archetype'][intervention]
    window_to_wall_ratio_new =      scenario_db['window_to_wall_ratio_new'][intervention]
    add_storeys_new =               scenario_db['add_storeys_new'][intervention]
    change_footprint_area_new =     scenario_db['change_footprint_area_new'][intervention]
    add_storeys_extension =         scenario_db['add_storeys_extension'][intervention]

    insulation_type_renovation =    scenario_db['insulation_type_renovation'][intervention]
    insulation_thickness_renovation = str(int(scenario_db['insulation_thickness_renovation'][intervention]))
    window_type_renovation =        scenario_db['window_type_renovation'][intervention]
    interior_renovation_at_intervention = scenario_db['interior_renovation_at_intervention'][intervention]


    insulation_type_new =           scenario_db['insulation_type_new'][intervention]
    insulation_thickness_new =      str(int(scenario_db['insulation_thickness_new'][intervention]))
    window_type_new =               scenario_db['window_type_new'][intervention]
    construction_type_new =         scenario_db['construction_type_new'][intervention]
    construction_type_add_storeys = scenario_db['construction_type_add_storeys'][intervention]

    heating_system_overall =        scenario_db['heating_system_overall'][intervention]
    has_mechanical_ventilation =    scenario_db['has_mechanical_ventilation'][intervention]


    #FIX DESIGN PARAMS 1.0
    heating_system_dhw_sc =         scenario_db['heating_system_dhw_sc'][intervention]
    heat_emission_system_sc =       scenario_db['heat_emission_system_sc'][intervention]
    heat_distribution_system_sc =   scenario_db['heat_distribution_system_sc'][intervention]

    account_for_biogenic_carbon =   scenario_db['account_for_biogenic_carbon'][intervention]
    account_disposal_emissions_of_existing_building = scenario_db['account_disposal_emissions_of_existing_building'][intervention]

    #FIX DESIGN PARAMS 2.0
    cooling_system_sc =             scenario_db['cooling_system_sc'][intervention]
    if np.isnan(cooling_system_sc):
        cooling_system_sc = 'None'
    cold_emission_system_sc =       scenario_db['cold_emission_system_sc'][intervention]
    if np.isnan(cold_emission_system_sc):
        cold_emission_system_sc = 'None'
    simplifed_LCA =                 scenario_db['simplifed_LCA'][intervention]
    change_orientation =            scenario_db['change_orientation'][intervention]
    infiltration_volume_flow_ren =  scenario_db['infiltration_volume_flow_ren'][intervention]
    
    
    return [scenario_group,label,scenario,original_building_archetype,window_to_wall_ratio_new,add_storeys_new,change_footprint_area_new,add_storeys_extension,\
           insulation_type_renovation,insulation_thickness_renovation,window_type_renovation,interior_renovation_at_intervention,\
           insulation_type_new, insulation_thickness_new, window_type_new,construction_type_new,construction_type_add_storeys,\
           heating_system_overall, has_mechanical_ventilation,\
           heating_system_dhw_sc,heat_emission_system_sc,heat_distribution_system_sc,\
           account_for_biogenic_carbon,account_disposal_emissions_of_existing_building,\
           cooling_system_sc,cold_emission_system_sc,simplifed_LCA,change_orientation,infiltration_volume_flow_ren]


           # scenario_group, label, scenario, original_building_archetype, window_to_wall_ratio_new,\
           # add_storeys_new, change_footprint_area_new, add_storeys_extension, insulation_type_renovation,\
           # insulation_thickness_renovation, window_type_renovation, interior_renovation_at_intervention,\
           # insulation_type_new, insulation_thickness_new, window_type_new, construction_type_new,\
           # construction_type_add_storeys, heating_system_overall, has_mechanical_ventilation,\
           # heating_system_dhw_sc, heat_emission_system_sc, heat_distribution_system_sc, account_for_biogenic_carbon,\
           # account_disposal_emissions_of_existing_building, cooling_system_sc, cold_emission_system_sc, simplifed_LCA,\
           # change_orientation, infiltration_volume_flow_ren

    

def read_materials(construction_db,path_excel,list_all_excel_sheets): 
    """This Function extracts the construction entries form the database"""

    for i, sheet in enumerate(list_all_excel_sheets):
        db = pd.read_excel(path_excel, sheet, index_col="ID_Construction",skiprows=[1])
        db['u_value'].fillna(np.inf, inplace=True) #Replace empty u value columns with ininite, to ensure propere u-value calculation. 
    
        db = db[db.index.notna()]
        if 'Old_component' not in db.columns:
            db['Old_component'] = None
        db = db[['Category','u_value','g_value','GWP_prod','GWP_disp','CO2_bio_stored','Rotation_time_bio','GWP_Bio','RSL','Cost','functional_unit','Literature','Note','Literature_Biogenic','Old_component']]
        
        # Check if the DataFrame is empty or all-NA before concatenating
        if not db.empty and not db.isna().all().all():
            frames = [construction_db, db]
            construction_db = pd.concat(frames)
        # frames = [construction_db, db]
        # construction_db = pd.concat(frames)
        #print(sheet)
   
    return construction_db
    
        
def decarbonization_factor(GWP_2022,RSP,Y_minimal,Y_intervention = 2025, E_min = 0.032):
    """
    Calculates the decarbonization factor for electricity, which is then multipied with the GWP_2022 value (KBOB 2022, per kWh electricty): 
    Assumes a Linear decrease form 2020 on to the minimal value  E_min until year Y_minimal (target year of decarbonization)
    The year of intevention is assumet to be in 2025 per default. 
    
    E_min 0.032 KgCO2eq/kWh ele,  according to  Zappa et. al. 2018, Is a 100% renewable European power system feasible by 2050?
    
    Other option: 
    E_min 0.004 KgCO2eq/kWh ele, 
    According to . Pleßmann G, Blechinger P. How to meet EU GHG emission reduction targets? A
    model based decarbonization pathway for Europe’s electricity supply system until
    2050. Energy Strategy Rev. 2017;15:19–32. https://doi.org/10.1016/j.esr.2016.11.003.
    
    Both those assumtions are still really optimistic, and not seen in "real projections"!!!
    -> THIS BASIC SETUP IS ALWAYS OVERWRITTEN WITH VALUES SPECIFIED IN THE INPUT!
    """
    a = (GWP_2022-E_min)/(2022 - Y_minimal) #Slope linear decrease form 2022 to Y_minimal
    b = GWP_2022 - a*2022                   #Ordinate cut for linear decrease curve form 2022 to Y_minimal
    
    h = a*Y_intervention + b                #Grid emissions in the year of intervention 
    GWP_cum = RSP*E_min + (1/2)*(Y_minimal-Y_intervention)*(h-E_min)    # Cummulative emissions per kWh for the whole RSP 
    GWP_ele_factor = GWP_cum/(RSP*GWP_2022)                             # Devision by the Cummulative emissions per kWh, if no decarbonizatino happens
    
    return  GWP_ele_factor   


def change_RSL_construction(construction_type, RSL_new, construction_db):
    """
    This function changes all RSL entries for a given construction layer type: e.g. insulation. 
    The usage is for the sensitivity analysis, considering different RSL
    """
    construction_db_updated = construction_db.copy()
    construction_db_index = construction_db_updated[construction_db_updated['Category']==construction_type].index
    construction_db_updated.loc[construction_db_index, 'RSL'] = RSL_new

    return construction_db_updated


def change_RSL_system(system_type, RSL_new, system_db):
    """
    This function changes all RSL entries for a system type: e.g. ASHP. 
    The usage is for the sensitivity analysis, considering different RSL
    """
    system_db_updated = system_db.copy()
    system_db_index = system_db_updated[system_db_updated['Category']==system_type].index
    system_db_updated.loc[system_db_index, 'RSL'] = RSL_new

    return system_db_updated


    
def new_constructions_configurations(typ):
    """
    Stores A set of new constructions
    """
    full_concrete_conventional = {"wall_type_ag":                   ['int_finishing_plaster_conventional','wall_concrete_conventional_18cm_60Fe','empty_layer','empty_layer'],
                                  "roof_type":                      ['int_finishing_plaster_conventional','roof_flat_core_concrete','empty_layer','empty_layer'],
                                  "ceiling_to_basement_type" :      ['flooring_parquet_glued','ceiling_concrete_conventional_24cm_90Fe','empty_layer','empty_layer'],
                                  "ceiling_type":                   ['int_finishing_plaster_conventional','ceiling_concrete_conventional_24cm_90Fe','empty_layer','flooring_parquet_glued'],
                                  "wall_type_bg":                   ['empty_layer','wall_bg_concrete_conventional_cold_18','empty_layer','empty_layer'],
                                  "slab_basement_type":             ['empty_layer','slab_to_basement_conventional_cold_25','empty_layer','empty_layer'],
                                  "partitions_type":                ['int_finishing_plaster_conventional','partition_masonry_BN15','empty_layer','int_finishing_plaster_conventional'], 
                                  "tilted_roof_type":               None,
                                  "fraction_partitions":            0.03,
                                  "infiltration_volume_flow":       0.15, #Gemäss SIA 380-1 2016 3.5.5 soll 0.15m3/(hm2) verwendet werden
                                  "thermal_bridge_add_on" :         0,
                                  "heat_capacity_per_energyreferencearea": 0.15,
                                  "construction_type":              'heavy_weight', #this parameter is needed for the criteria, if the construction also for extensions (add stories) can be used
                                  "construction_name":              'full_concrete_conventional'} 
    
    full_concrete_lowco2 =       {"wall_type_ag":                   ['int_finishing_plaster_conventional','wall_concrete_lowco2_18cm_60Fe','empty_layer','empty_layer'],
                                  "roof_type":                      ['int_finishing_plaster_conventional','roof_flat_core_concrete','empty_layer','empty_layer'],
                                  "ceiling_to_basement_type" :      ['flooring_parquet_glued','ceiling_concrete_lowco2_24cm_90Fe','empty_layer','empty_layer'],
                                  "ceiling_type":                   ['int_finishing_plaster_conventional','ceiling_concrete_lowco2_24cm_90Fe','empty_layer','flooring_parquet_glued'],
                                  "wall_type_bg":                   ['empty_layer','wall_bg_concrete_lowco2_cold_18','empty_layer','empty_layer'],
                                  "slab_basement_type":             ['empty_layer','slab_to_basement_lowco2_cold_25','empty_layer','empty_layer'],
                                  "partitions_type":                ['int_finishing_plaster_conventional','partition_masonry_BN15','empty_layer','int_finishing_plaster_conventional'], 
                                  "tilted_roof_type":               None,
                                  "fraction_partitions":            0.03,
                                  "infiltration_volume_flow":       0.15, #Gemäss SIA 380-1 2016 3.5.5 soll 0.15m3/(hm2) verwendet werden
                                  "thermal_bridge_add_on" :         0,
                                  "heat_capacity_per_energyreferencearea": 0.15,
                                  "construction_type":              'heavy_weight', #this parameter is needed for the criteria, if the construction also for extensions (add stories) can be used
                                  "construction_name":              'full_concrete_lowco2'} 
    
    wood_armature_classical =    {"wall_type_ag":                   ['int_finishing_plaster_conventional','wall_woodframe_24_non_loadbearing','empty_layer','empty_layer'],
                                  "roof_type":                      ['int_finishing_plaster_conventional','roof_flat_core_wood','empty_layer','empty_layer'],
                                  "ceiling_to_basement_type" :      ['flooring_parquet_glued','ceiling_concrete_conventional_24cm_90Fe','empty_layer','empty_layer'],
                                  "ceiling_type":                   ['int_finishing_plaster_conventional','wood_armature_construction_glulam_conventional','empty_layer','flooring_parquet_glued'],
                                  "wall_type_bg":                   ['empty_layer','wall_bg_concrete_conventional_cold_18','empty_layer','empty_layer'],
                                  "slab_basement_type":             ['empty_layer','slab_to_basement_conventional_cold_25','empty_layer','empty_layer'],
                                  "partitions_type":                ['int_finishing_plaster_conventional','partition_wood_frame_15_conventional','empty_layer','int_finishing_plaster_conventional'],
                                  "tilted_roof_type":               None,
                                  "fraction_partitions":            0.03,
                                  "infiltration_volume_flow":       0.15, #Gemäss SIA 380-1 2016 3.5.5 soll 0.15m3/(hm2) verwendet werden
                                  "thermal_bridge_add_on" :         0,
                                  "heat_capacity_per_energyreferencearea": 0.08,
                                  "construction_type":              'light_weight', #this parameter is needed for the criteria, if the construction also for extensions (add stories) can be used
                                  "construction_name":              'wood_armature_classical'} 
    
    wood_armature_lowco2 =       {"wall_type_ag":                   ['int_finishing_wood','wall_woodframe_24_non_loadbearing','empty_layer','empty_layer'],
                                  "roof_type":                      ['int_finishing_wood','roof_flat_core_wood','empty_layer','empty_layer'],
                                  "ceiling_to_basement_type" :      ['flooring_parquet_floating','ceiling_concrete_lowco2_24cm_90Fe','empty_layer','empty_layer'],
                                  "ceiling_type":                   ['int_finishing_wood','wood_armature_construction_glulam_lowco2','empty_layer','flooring_parquet_floating'],
                                  "wall_type_bg":                   ['empty_layer','wall_bg_concrete_lowco2_cold_18','empty_layer','empty_layer'],
                                  "slab_basement_type":             ['empty_layer','slab_to_basement_lowco2_cold_25','empty_layer','empty_layer'],
                                  "partitions_type":                ['int_finishing_clay_plaster','partition_earth_masonry_15','empty_layer','int_finishing_clay_plaster'],
                                  "tilted_roof_type":               None,
                                  "fraction_partitions":            0.03,
                                  "infiltration_volume_flow":       0.15, #Gemäss SIA 380-1 2016 3.5.5 soll 0.15m3/(hm2) verwendet werden
                                  "thermal_bridge_add_on" :         0,
                                  "heat_capacity_per_energyreferencearea": 0.08,
                                  "construction_type":              'light_weight', #this parameter is needed for the criteria, if the construction also for extensions (add stories) can be used
                                  "construction_name":              'wood_armature_lowco2'} 
   
    wood_armature_rammed_earth = {"wall_type_ag":                   ['int_finishing_clay_plaster','wall_rammed_earth_50','empty_layer','empty_layer'],
                                  "roof_type":                      ['int_finishing_wood','roof_flat_core_wood','empty_layer','empty_layer'],
                                  "ceiling_to_basement_type" :      ['flooring_parquet_floating','ceiling_concrete_lowco2_24cm_90Fe','empty_layer','empty_layer'],
                                  "ceiling_type":                   ['int_finishing_wood','wood_armature_construction_glulam_lowco2','empty_layer','flooring_parquet_floating'],
                                  "wall_type_bg":                   ['empty_layer','wall_bg_concrete_lowco2_cold_18','empty_layer','empty_layer'],
                                  "slab_basement_type":             ['empty_layer','slab_to_basement_lowco2_cold_25','empty_layer','empty_layer'],
                                  "partitions_type":                ['int_finishing_clay_plaster','partition_earth_masonry_15','empty_layer','int_finishing_clay_plaster'],
                                  "tilted_roof_type":               None,
                                  "fraction_partitions":            0.03,
                                  "infiltration_volume_flow":       0.15, #Gemäss SIA 380-1 2016 3.5.5 soll 0.15m3/(hm2) verwendet werden
                                  "thermal_bridge_add_on" :         0,
                                  "heat_capacity_per_energyreferencearea": 0.15,
                                  "construction_type":              'heavy_weight', #this parameter is needed for the criteria, if the construction also for extensions (add stories) can be used
                                  "construction_name":              'wood_armature_rammed_earth'} 
  
    
    wood_frame_classical =       {"wall_type_ag":                   ['int_finishing_plaster_conventional','wall_woodframe_24_loadbearing','empty_layer','empty_layer'],
                                  "roof_type":                      ['int_finishing_plaster_conventional','roof_flat_core_wood','empty_layer','empty_layer'],
                                  "ceiling_to_basement_type" :      ['flooring_parquet_glued','ceiling_concrete_conventional_24cm_90Fe','empty_layer','empty_layer'],
                                  "ceiling_type":                   ['int_finishing_plaster_conventional','ceiling_woodbeams_conventional','empty_layer','flooring_parquet_glued'],
                                  "wall_type_bg":                   ['empty_layer','wall_bg_concrete_conventional_cold_18','empty_layer','empty_layer'],
                                  "slab_basement_type":             ['empty_layer','slab_to_basement_conventional_cold_25','empty_layer','empty_layer'],
                                  "partitions_type":                ['int_finishing_plaster_conventional','partition_wood_frame_15_conventional','empty_layer','int_finishing_plaster_conventional'],
                                  "tilted_roof_type":               None,
                                  "fraction_partitions":            0.03,
                                  "infiltration_volume_flow":       0.15, #Gemäss SIA 380-1 2016 3.5.5 soll 0.15m3/(hm2) verwendet werden
                                  "thermal_bridge_add_on" :         0,
                                  "heat_capacity_per_energyreferencearea": 0.03,
                                  "construction_type":              'light_weight', #this parameter is needed for the criteria, if the construction also for extensions (add stories) can be used
                                  "construction_name":              'wood_frame_classical'} #can be used ONLY until 3 stories, mainly for adding storeys
   
   
    wood_frame_lowco2  =         {"wall_type_ag":                   ['int_finishing_wood','wall_woodframe_24_loadbearing','empty_layer','empty_layer'],
                                  "roof_type":                      ['int_finishing_wood','roof_flat_core_wood','empty_layer','empty_layer'],
                                  "ceiling_to_basement_type" :      ['flooring_parquet_floating','ceiling_concrete_lowco2_24cm_90Fe','empty_layer','empty_layer'],
                                  "ceiling_type":                   ['int_finishing_wood','ceiling_woodbeams_low_co2','empty_layer','flooring_parquet_floating'],
                                  "wall_type_bg":                   ['empty_layer','wall_bg_concrete_lowco2_cold_18','empty_layer','empty_layer'],
                                  "slab_basement_type":             ['empty_layer','slab_to_basement_lowco2_cold_25','empty_layer','empty_layer'],
                                  "partitions_type":                ['int_finishing_clay_plaster','partition_earth_masonry_15','empty_layer','int_finishing_clay_plaster'],
                                  "tilted_roof_type":               None,
                                  "fraction_partitions":            0.03,
                                  "infiltration_volume_flow":       0.15, #Gemäss SIA 380-1 2016 3.5.5 soll 0.15m3/(hm2) verwendet werden
                                  "thermal_bridge_add_on" :         0,
                                  "heat_capacity_per_energyreferencearea": 0.03,
                                  "construction_type":              'light_weight', #this parameter is needed for the criteria, if the construction also for extensions (add stories) can be used
                                  "construction_name":              'wood_frame_lowco2'} #can be used ONLY until 3 stories, mainly for adding storeys

    None_type  =                 {"wall_type_ag":                   ['empty_layer','empty_layer','empty_layer','empty_layer'],
                                  "roof_type":                      ['empty_layer','empty_layer','empty_layer','empty_layer'],
                                  "ceiling_to_basement_type" :      ['empty_layer','empty_layer','empty_layer','empty_layer'],
                                  "ceiling_type":                   ['empty_layer','empty_layer','empty_layer','empty_layer'],
                                  "wall_type_bg":                   ['empty_layer','empty_layer','empty_layer','empty_layer'],
                                  "slab_basement_type":             ['empty_layer','empty_layer','empty_layer','empty_layer'],
                                  "partitions_type":                ['empty_layer','empty_layer','empty_layer','empty_layer'],
                                  "tilted_roof_type":               None,
                                  "fraction_partitions":            0.00,
                                  "infiltration_volume_flow":       0.15, #Gemäss SIA 380-1 2016 3.5.5 soll 0.15m3/(hm2) verwendet werden
                                  "thermal_bridge_add_on" :         0,
                                  "heat_capacity_per_energyreferencearea": 0.03,
                                  "construction_type":              None, #this parameter is needed for the criteria, if the construction also for extensions (add stories) can be used
                                  "construction_name":              'None_type_new_construction'} #can be used ONLY until 3 stories, mainly for adding storeys

    
    
    new_constructions =  {#For new constructions 
                          'full_concrete_conventional': full_concrete_conventional,
                          'full_concrete_lowco2': full_concrete_lowco2,
                          'wood_armature_classical': wood_armature_classical,
                          'wood_armature_lowco2': wood_armature_lowco2,
                          'wood_armature_rammed_earth': wood_armature_rammed_earth,
                          #for adding storeys
                          'wood_frame_classical': wood_frame_classical,
                          'wood_frame_lowco2': wood_frame_lowco2,
                          'None_type': None_type,
                          }
    
    return new_constructions[typ]

        