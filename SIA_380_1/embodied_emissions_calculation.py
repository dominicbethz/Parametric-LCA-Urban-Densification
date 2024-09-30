import pandas as pd
import numpy as np


def embodied_emissions_decarbonization_factor_systems(RSL,RSP, decarbonization_frac_2050, first_replacement = True, Y_intervention = 2025):
    """ 
    Calculates the cummulative impact factor, of one component, based on the components RSL and the RSP of the Building. 
    It is a linear decrease assumed until 2050, to the fraction "decarbonization_2050" (between 0 and 1), which is the fraction of GHG inventory in 2022 (=1)
    The year of intervention is set by default to 2025. 
    Important: the decarbonization form 2022 to 2025 is not taken into account for the intervention itselve, only for the replacements
    If first_replacement = False, the layer are not changed in the year of intervention. This is intorduced, such that interior finishings
    can be not alterd for a intervention, but they will be replaced later according to the given RSL (needed in the renovation case)
    To calculate the life cycle impact, the ummulative impact factor must be multipled with the LCA Database GWP_100 value of 2022. 
    IMPORTANT: replaced components, which have a RSL that is not a Divisor of the RSP (eg. RSP modulo RSL != 0), are accunted fully! 
    this represents the fact, that systems must be replaced if they have a malfunction 
    
    """
    
    #linear decrease function, form 2022 to 2050 , with f(2022)= 1 and f(2050) = decarbonization_frac_2050
    a = (decarbonization_frac_2050 - 1)/(2050-2022) #slope
    b = 1 - 2022*a
    
    
    def fraction(year): # returns the fraction, if before 2050, on the linear decerase curve, after 2050 it is constant. 
        if year >= 2050:
            frac = decarbonization_frac_2050
        else: 
            frac = a*year + b
        return frac
    
    if first_replacement:
        F_0 = 1
    else:
        F_0 = 0
    
    F_is  =  0 
    k = int((RSP/RSL)//1)  #how often a component is (absolutly) replaced over the RSP

    for i in range(k): #all replacements after the intervention (including replacements short before demolishment! This is only used for systems!)
        F_is  += fraction(Y_intervention + RSL * (i+1)) #sum up the share of GHG for each replacement, realtive to the GHG in the inventory, in 2022
    
    #Add the emissions fraction (=1 or 0) of the first intervention
    F_cum_mean = (F_0 + F_is)
    #print(F_cum_mean)
    
    return F_cum_mean

def embodied_emissions_decarbonization_factor_construction(RSL,RSP, decarbonization_frac_2050, first_replacement = True, Y_intervention = 2025):
    """ 
    Calculates the cummulative impact factor, of one component, based on the components RSL and the RSP of the Building. 
    It is a linear decrease assumed until 2050, to the fraction "decarbonization_2050" (between 0 and 1), which is the fraction of GHG inventory in 2022 (=1)
    The year of intervention is set by default to 2025. 
    Important: the decarbonization form 2022 to 2025 is not taken into account for the intervention itselve, only for the replacements
    If first_replacement = False, the layer are not changed in the year of intervention. This is intorduced, such that interior finishings
    can be not alterd for a intervention, but they will be replaced later according to the given RSL (needed in the renovation case)
    To calculate the life cycle impact, the ummulative impact factor must be multipled with the LCA Database GWP_100 value of 2022. 
    IMPORTANT: replaced components, which have a RSL that is not a Divisor of the RSP (eg. RSP modulo RSL != 0), are accunted fully! 
    To guarantee unrealistic replacements before demolishment (Typically a building is maintained on a minium level before demolishment)
    Replacements 10 years before demolishment are not taken into account. 
    
    """
    
    #linear decrease function, form 2022 to 2050 , with f(2022)= 1 and f(2050) = decarbonization_frac_2050
    a = (decarbonization_frac_2050 - 1)/(2050-2022) #slope
    b = 1 - 2022*a
    
    
    def fraction(year): # returns the fraction, if before 2050, on the linear decerase curve, after 2050 it is constant. 
        if year >= 2050:
            frac = decarbonization_frac_2050
        else: 
            frac = a*year + b
        return frac
    
    if first_replacement:
        F_0 = 1
    else:
        F_0 = 0
    
    F_is  =  0 
    k = int((RSP/RSL)//1)  #how often a component is (absolutly) replaced over the RSP

    for i in range(k-1): #all replacements after the intervention (including replacements short before demolishment! This is only used for systems!)
        F_is  += fraction(Y_intervention + RSL * (i+1)) #sum up the share of GHG for each replacement, realtive to the GHG in the inventory, in 2022
   
    if RSP%RSL >= 10: #last replacement base on condition -> 10 years before demolishment no replacements are made. 
        F_is  +=  fraction(Y_intervention + RSL * k) #last replacement base on condition
   
    
    #Add the emissions fraction (=1 or 0) of the first intervention
    F_cum_mean = (F_0 + F_is)
    #print(F_cum_mean)
    
    return F_cum_mean



# def embodied_emissions_decarbonization_factor(RSL,RSP, decarbonization_frac_2050, first_replacement = True, Y_intervention = 2025):
#     """ 
#     NOT USED ANYMORE! 
    
#     Calculates the cummulative impact factor, of one component, based on the components RSL and the RSP of the Building. 
#     It is a linear decrease assumed until 2050, to the fraction "decarbonization_2050" (between 0 and 1), which is the fraction of GHG inventory in 2022 (=1)
#     The year of intervention is set by default to 2025. 
#     Important: the decarbonization form 2022 to 2025 is not taken into account for the intervention itselve, only for the replacements
#     If first_replacement = False, the layer are not changed in the year of intervention. This is intorduced, such that interior finishings
#     can be not alterd for a intervention, but they will be replaced later according to the given RSL (needed in the renovation case)
#     To calculate the life cycle impact, the ummulative impact factor must be multipled with the LCA Database GWP_100 value of 2022. 
    
#     IMPORTANT: replaced components, which have a RSL that is not a Divisor of the RSP (eg. RSP modulo RSL != 0), are accunted in fractions!
    
#     """
    
#     #linear decrease function, form 2022 to 2050 , with f(2022)= 1 and f(2050) = decarbonization_frac_2050
#     a = (decarbonization_frac_2050 - 1)/(2050-2022) #slope
#     b = 1 - 2022*a
    
    
#     def fraction(year): # returns the fraction, if before 2050, on the linear decerase curve, after 2050 it is constant. 
#         if year >= 2050:
#             frac = decarbonization_frac_2050
#         else: 
#             frac = a*year + b
#         return frac
    
#     if first_replacement:
#         F_0 = 1
#     else:
#         F_0 = 0
    
#     F_is  =  0 
#     k = int((RSP/RSL)//1)  #how often a component is (absolutly) replaced over the RSP

#     for i in range(k-1):
#         F_is  += fraction(Y_intervention + RSL * (i+1)) #sum up the share of GHG for each replacement, realtive to the GHG in the inventory, in 2022
    
#     #Last replacement is accounted only in parts: e.g. if  RSL is longer than remaining RSP, the intervention is accounted only in fraction. 
#     #This does not make sens from a deterministic perspective (there typically RSL are devisors or RSP), but make sens in Probabilisitc calculations. (since in reality before a demolition parts are usually not replaced)
#     F_is  +=  fraction(Y_intervention + RSL * k)*(RSP - RSL*k)/RSL #TODO: This can be discussed, if it make sense! 
   
#     #Add the emissions fraction (=1 or 0) of the first intervention
#     F_cum_mean = (F_0 + F_is)
#     #print(F_cum_mean)
    
#     return F_cum_mean




"""NEW VERSION, Dominic Büttiker, based on production and disposal emissions"""


def calculate_system_related_embodied_emissions_new(ee_database, gebaeudekategorie, energy_reference_area, RSP,
                                                heizsystem, heat_emission_system,
                                                heat_distribution, nominal_heating_power, dhw_heizsystem,
                                                cooling_system, cold_emission_system, nominal_cooling_power,
                                                pv_area, pv_type, pv_efficiency, has_mechanical_ventilation,
                                                max_aussenluft_volumenstrom, battery_capacity, decarbonization_frac_2050 = 1.0):
    """
    This function is used to calculate the annualized embodied emissions of the considered building systems. A database
    file is called that includes impact and lifetime values. Further the system sizing has to be known for some power
    based components. Other components are sized directly from the energy reference area.
    Currently included: heat/cold production, heat/cold distribution, heat/cold emission, Ventilation, PV and Battery
    
    TODO: 
        - possibly add electrical systems
        - Question how to handle if the system stays: mainly the distribution system, since there is coupeling to the type in the function 
    
    :param ee_database_path: string, database path where the system's impact and lifetimes are stored (xlsx file)
    :param gebaeudekategorie: float/int of SIA building category
    :param energy_reference_area: float
    :param RSP: Reference service period of Building 
    :param heizsystem: string of the heating system type
    :param heat_emission_system: string of heat emission system
    :param heat_distribution: string of heat distribution system
    :param nominal_heating_power: float [W] heating sizing. MAKE SURE TO USE CORRECT DIMENSION
    :param dhw_heizsystem: string dhw heating system (currently not used, assumed to be the heating system)
    :param cooling_system: string of cooling system
    :param cold_emission_system: string of cold emission system
    :param nominal_cooling_power: [W] float cooling sizing. MAKE SURE TO USE CORRECT DIMENSION
    :param pv_area: m2 float/int
    :param pv_type: string of pv type as in database
    :param pv_efficiency: stc efficiency is required for m2 to kWp transformation
    :param has_mechanical_ventilation: boolean (True/False)
    :param max_aussenluft_volumenstrom: float in m3/hm2
    
    :return: annualized embodied emissions for building systems per area in kgCO2eq/m2a
    """

    database = ee_database

    #Function that calculates the reference service life of a component: if RSP in database: the same periode like the building is choosen 
    def RSL(ID_System):
        if database.loc[ID_System ,'RSL'] =='RSP':
            RSL = RSP
        else: 
            RSL = database.loc[ID_System ,'RSL']
        return RSL
    

    # Calculation of embodied emissions for the thermal systems
    """Structure:
        
    - All GWP values: array of two elements: firstly GWP_prod, secondly GWP_disp
        
    """

    ## Heater
    heater_embodied_per_kw = np.array([database['GWP_prod'][heizsystem],database['GWP_disp'][heizsystem]]) # this data is in kgCO2eq/kW
    heater_lifetime = RSL(heizsystem)
    heater_embodied = heater_embodied_per_kw * nominal_heating_power/1000.0 * embodied_emissions_decarbonization_factor_systems(heater_lifetime,RSP, decarbonization_frac_2050)  #    (RSP/ heater_lifetime)   # heating power comes in W
    #dhw heating is assumed to be included in the space heating capacity

    if cooling_system == heizsystem:
        if nominal_cooling_power <= nominal_heating_power:
            cooler_embodied = np.array([0.0,0.0])

        else:
            cooler_embodied_per_kw =  np.array([database['GWP_prod'][cooling_system],database['GWP_disp'][cooling_system]]) # this data is in kgCO2eq/kW
            cooler_lifetime = RSL(cooling_system)
            cooler_embodied = cooler_embodied_per_kw * nominal_cooling_power/1000.0 * embodied_emissions_decarbonization_factor_systems(cooler_lifetime,RSP, decarbonization_frac_2050) #(RSP/ cooler_lifetime)  # cooling power comes in W
            #heating sys is 0, since smaller 
            heater_embodied = np.array([0.0,0.0])

    else:
        cooler_embodied_per_kw =  np.array([database['GWP_prod'][cooling_system],database['GWP_disp'][cooling_system]]) # this data is in kgCO2eq/kW
        cooler_lifetime = RSL(cooling_system)
        cooler_embodied = cooler_embodied_per_kw * nominal_cooling_power/1000.0 * embodied_emissions_decarbonization_factor_systems(cooler_lifetime,RSP, decarbonization_frac_2050) #(RSP/ cooler_lifetime) # cooling power comes in W

    ######### Heat emission
    if heat_emission_system == 'air':
        # In that case 0.0 is assigned to heat emission system because it is already considered in
        # mechanical ventilation
        heat_emission_embodied_per_area = np.array([0.0,0.0])
        heat_emission_lifetime = 1.0  # to avoid division by 0
        if has_mechanical_ventilation == False:
            print("you chose heat distribution by air but do not have mechanical ventilation")
            quit()

    else:
        heat_emission_embodied_per_area = np.array([database['GWP_prod'][heat_emission_system],database['GWP_disp'][heat_emission_system]]) # this data is in kgCO2eq/m2
        heat_emission_lifetime = RSL(heat_emission_system)
        

    heat_emission_embodied = heat_emission_embodied_per_area * energy_reference_area  * embodied_emissions_decarbonization_factor_systems(heat_emission_lifetime, RSP, decarbonization_frac_2050)# (RSP/ heat_emission_lifetime)
    

    ######### Distribution
   
    if heat_distribution == "hydronic":
        if int(gebaeudekategorie) == 1:
            heat_distribution_embodied_per_area =  np.array([database['GWP_prod']['hydronic heat distribution residential'],database['GWP_disp']['hydronic heat distribution residential']]) 
            heat_distribution_lifetime = RSL('hydronic heat distribution residential')
        
        elif int(gebaeudekategorie) == 3:
            heat_distribution_embodied_per_area = np.array([database['GWP_prod']['hydronic heat distribution office'],database['GWP_disp']['hydronic heat distribution office']]) 
            heat_distribution_lifetime = RSL('hydronic heat distribution office')

        else:
            heat_distribution_embodied_per_area =  np.array([0.0,0.0])
            heat_distribution_lifetime = 1.0  # this avoids division by zero if embodied = 0
            print("no embodied emissions for heat distribution, this building category is not implemented")
    
    elif heat_distribution == "hydronic old": #case if the distirubution system is not changed. 
        if int(gebaeudekategorie) == 1:
            heat_distribution_embodied_per_area =  np.array([database['GWP_prod']['hydronic heat distribution residential old'],database['GWP_disp']['hydronic heat distribution residential']]) 
            heat_distribution_lifetime = RSL('hydronic heat distribution residential')
        
        else:
            heat_distribution_embodied_per_area =  np.array([0.0,0.0])
            heat_distribution_lifetime = 1.0  # this avoids division by zero if embodied = 0
            print("no embodied emissions for heat distribution, this building category is not implemented")

    elif heat_distribution == 'electric':
        heat_distribution_embodied_per_area = np.array([0.0,0.0])
        heat_distribution_lifetime = 1.0  # to avoid division by zero

    elif heat_distribution == 'air':
        #Todo: I am not sure if that makes sense or if it would be included in mechanidcal ventilation
        heat_distribution_embodied_per_area = np.array([database['GWP_prod'][heat_distribution],database['GWP_disp'][heat_distribution]])   # this data is in kgCO2eq/kW
        heat_distribution_lifetime = RSL(heat_distribution)

    else:
        print('You did not specify a correct heat distribution system')
        quit()

    embodied_heat_distribution = heat_distribution_embodied_per_area * energy_reference_area * embodied_emissions_decarbonization_factor_systems(heat_distribution_lifetime, RSP, decarbonization_frac_2050) #(RSP/ heat_distribution_lifetime) 
   



    ######### Cold distribution and emission 
    #TODO: IF COOLING POWER IS BIGGER THAN HEATING POWER IT IS NOT CALCULATED CORRECTLY
    if heat_emission_system == cold_emission_system:

        cold_emission_embodied =  np.array([0.0,0.0])


    else:
        cold_emission_embodied_per_area = np.array([database['GWP_prod'][cold_emission_system],database['GWP_disp'][cold_emission_system]])  # this data is in kgCO2eq/m2
        cold_emission_embodied_lifetime = RSL(cold_emission_system)
        
        cold_emission_embodied = cold_emission_embodied_per_area * energy_reference_area * embodied_emissions_decarbonization_factor_systems(cold_emission_embodied_lifetime, RSP, decarbonization_frac_2050) #(RSP/ cold_emission_embodied_lifetime) 

    

    embodied_thermal = heater_embodied + cooler_embodied + embodied_heat_distribution + heat_emission_embodied +\
                                                                cold_emission_embodied
    
    

    ######### Calculation of embodied emissions for ventilation system -> lineearizatino apporach, first value is the cut of the y axies, the second value is the slope
    if has_mechanical_ventilation == True:
         ventilation_embodied_per_era = np.array([float(database['GWP_prod']['mechanical ventilation'].split(",")[0]),float(database['GWP_disp']['mechanical ventilation'].split(",")[0])]) 
         ventilation_embodied_per_era += np.array([float(database['GWP_prod']['mechanical ventilation'].split(",")[1]),float(database['GWP_disp']['mechanical ventilation'].split(",")[1])]) * max_aussenluft_volumenstrom
         #print(ventilation_embodied_per_era)
         ventilation_lifetime = RSL('mechanical ventilation')
         
         embodied_ventilation = ventilation_embodied_per_era * energy_reference_area * embodied_emissions_decarbonization_factor_systems(ventilation_lifetime, RSP, decarbonization_frac_2050) #(RSP/ ventilation_lifetime) 


    else:
        embodied_ventilation = np.array([0.0,0.0])
    

    
    ######### Calculation of embodied emissions for the electrical systems
    ## PV System
    if pv_type != None: 
        pv_embodied_per_kw = np.array([database['GWP_prod'][pv_type],database['GWP_disp'][pv_type]]) # this data is in kgCO2eq/kWp
        pv_lifetime = RSL(pv_type)
        
        pv_embodied = pv_embodied_per_kw * pv_area * pv_efficiency * embodied_emissions_decarbonization_factor_systems(pv_lifetime, RSP, decarbonization_frac_2050) # (RSP/ pv_lifetime)  # at STC Irradiance = 1kW/m2
    else:
        pv_embodied = np.array([0.0,0.0])
    embodied_electrical = pv_embodied #TODO: Question if general electrical installatinos shoud be included?


    ######### embodied emissions of batteries
    battery_embodied_per_kWh = np.array([database['GWP_prod']['battery'],database['GWP_disp']['battery']]) 
    battery_lifetime = RSL('battery')

    embodied_battery = battery_capacity/1000 * battery_embodied_per_kWh * embodied_emissions_decarbonization_factor_systems(battery_lifetime, RSP, decarbonization_frac_2050)# (RSP/ battery_lifetime)  # division by 1000 because battery input comes in Wh


    ######### Calculation of total embodied building systems (annualized per ERA): heater, cooler, distribution, emission, electric (PV), ventilation per energy reference area. 

    embodied_thermal_electrical_vent = (embodied_thermal + embodied_electrical + embodied_ventilation + embodied_battery)/(energy_reference_area*RSP)
    return embodied_thermal_electrical_vent



"""NEW VERSION, Dominic Büttiker, based on production and disposal emissions"""
def calculate_system_related_embodied_emissions_upfront_new(ee_database, gebaeudekategorie, energy_reference_area, RSP,
                                                heizsystem, heat_emission_system,
                                                heat_distribution, nominal_heating_power, dhw_heizsystem,
                                                cooling_system, cold_emission_system, nominal_cooling_power,
                                                pv_area, pv_type, pv_efficiency, has_mechanical_ventilation,
                                                max_aussenluft_volumenstrom, battery_capacity, decarbonization_frac_2050 = 1.0):
    """
    This function is used to calculate the UPFRONT annualized embodied emissions of the considered building systems. A database
    file is called that includes impact and lifetime values. Further the system sizing has to be known for some power
    based components. Other components are sized directly from the energy reference area.
    Currently included: heat/cold production, heat/cold distribution, heat/cold emission, Ventilation, PV and Battery
    
    TODO: 
        - possibly add electrical systems
        - Question how to handle if the system stays: mainly the distribution system, since there is coupeling to the type in the function 
    
    :param ee_database_path: string, database path where the system's impact and lifetimes are stored (xlsx file)
    :param gebaeudekategorie: float/int of SIA building category
    :param energy_reference_area: float
    :param RSP: Reference service period of Building 
    :param heizsystem: string of the heating system type
    :param heat_emission_system: string of heat emission system
    :param heat_distribution: string of heat distribution system
    :param nominal_heating_power: float [W] heating sizing. MAKE SURE TO USE CORRECT DIMENSION
    :param dhw_heizsystem: string dhw heating system (currently not used, assumed to be the heating system)
    :param cooling_system: string of cooling system
    :param cold_emission_system: string of cold emission system
    :param nominal_cooling_power: [W] float cooling sizing. MAKE SURE TO USE CORRECT DIMENSION
    :param pv_area: m2 float/int
    :param pv_type: string of pv type as in database
    :param pv_efficiency: stc efficiency is required for m2 to kWp transformation
    :param has_mechanical_ventilation: boolean (True/False)
    :param max_aussenluft_volumenstrom: float in m3/hm2
    
    :return: annualized embodied upfront emissions for building systems per area in kgCO2eq/m2a
    """

    database = ee_database

    #Function that calculates the reference service life of a component: if RSP in database: the same periode like the building is choosen 
    def RSL(ID_System):
        if database.loc[ID_System ,'RSL'] =='RSP':
            RSL = RSP
        else: 
            RSL = database.loc[ID_System ,'RSL']
        return RSL
    

    # Calculation of embodied emissions for the thermal systems
    """Structure:
        
    - All GWP values: array of two elements: firstly GWP_prod, secondly GWP_disp
        
    """

    ## Heater
    heater_embodied_per_kw = np.array([database['GWP_prod'][heizsystem],database['GWP_disp'][heizsystem]]) # this data is in kgCO2eq/kW
    heater_embodied = heater_embodied_per_kw * nominal_heating_power/1000.0 * 1 #    (RSP/ heater_lifetime)   # heating power comes in W
    #dhw heating is assumed to be included in the space heating capacity

    if cooling_system == heizsystem:
        if nominal_cooling_power <= nominal_heating_power:
            cooler_embodied = np.array([0.0,0.0])

        else:
            cooler_embodied_per_kw =  np.array([database['GWP_prod'][cooling_system],database['GWP_disp'][cooling_system]]) # this data is in kgCO2eq/kW
            cooler_embodied = cooler_embodied_per_kw * nominal_cooling_power/1000.0 * 1  # cooling power comes in W
            #heating sys is 0, since smaller 
            heater_embodied = np.array([0.0,0.0])

    else:
        cooler_embodied_per_kw =  np.array([database['GWP_prod'][cooling_system],database['GWP_disp'][cooling_system]]) # this data is in kgCO2eq/kW
        cooler_embodied = cooler_embodied_per_kw * nominal_cooling_power/1000.0 * 1# cooling power comes in W

    ######### Heat emission
    if heat_emission_system == 'air':
        # In that case 0.0 is assigned to heat emission system because it is already considered in
        # mechanical ventilation
        heat_emission_embodied_per_area = np.array([0.0,0.0])
        if has_mechanical_ventilation == False:
            print("you chose heat distribution by air but do not have mechanical ventilation")
            quit()

    else:
        heat_emission_embodied_per_area = np.array([database['GWP_prod'][heat_emission_system],database['GWP_disp'][heat_emission_system]]) # this data is in kgCO2eq/m2
        

    heat_emission_embodied = heat_emission_embodied_per_area * energy_reference_area * 1  # (RSP/ heat_emission_lifetime)
    

    ######### Distribution
   
    if heat_distribution == "hydronic":
        if int(gebaeudekategorie) == 1:
            heat_distribution_embodied_per_area =  np.array([database['GWP_prod']['hydronic heat distribution residential'],database['GWP_disp']['hydronic heat distribution residential']]) 
        
        elif int(gebaeudekategorie) == 3:
            heat_distribution_embodied_per_area = np.array([database['GWP_prod']['hydronic heat distribution office'],database['GWP_disp']['hydronic heat distribution office']]) 

        else:
            heat_distribution_embodied_per_area =  np.array([0.0,0.0])
            print("no embodied emissions for heat distribution, this building category is not implemented")
    
    elif heat_distribution == "hydronic old": #case if the distirubution system is not changed. 
        if int(gebaeudekategorie) == 1:
            heat_distribution_embodied_per_area =  np.array([database['GWP_prod']['hydronic heat distribution residential old'],database['GWP_disp']['hydronic heat distribution residential']]) 
        
        else:
            heat_distribution_embodied_per_area =  np.array([0.0,0.0])
            print("no embodied emissions for heat distribution, this building category is not implemented")

    elif heat_distribution == 'electric':
        heat_distribution_embodied_per_area = np.array([0.0,0.0])

    elif heat_distribution == 'air':
        #Todo: I am not sure if that makes sense or if it would be included in mechanidcal ventilation
        heat_distribution_embodied_per_area = np.array([database['GWP_prod'][heat_distribution],database['GWP_disp'][heat_distribution]])   # this data is in kgCO2eq/kW

    else:
        print('You did not specify a correct heat distribution system')
        quit()

    embodied_heat_distribution = heat_distribution_embodied_per_area * energy_reference_area *1 #(RSP/ heat_distribution_lifetime) 
   



    ######### Cold distribution and emission 
    #TODO: IF COOLING POWER IS BIGGER THAN HEATING POWER IT IS NOT CALCULATED CORRECTLY
    if heat_emission_system == cold_emission_system:

        cold_emission_embodied =  np.array([0.0,0.0])


    else:
        cold_emission_embodied_per_area = np.array([database['GWP_prod'][cold_emission_system],database['GWP_disp'][cold_emission_system]])  # this data is in kgCO2eq/m2
        
        
        cold_emission_embodied = cold_emission_embodied_per_area * energy_reference_area * 1 #(RSP/ cold_emission_embodied_lifetime) 

    

    embodied_thermal = heater_embodied + cooler_embodied + embodied_heat_distribution + heat_emission_embodied +\
                                                                cold_emission_embodied
    
    

    ######### Calculation of embodied emissions for ventilation system. lineearizatino apporach, first value is the cut of the y axies, the second value is the slope
    if has_mechanical_ventilation == True:
        
         ventilation_embodied_per_era = np.array([float(database['GWP_prod']['mechanical ventilation'].split(",")[0]),float(database['GWP_disp']['mechanical ventilation'].split(",")[0])]) 
         ventilation_embodied_per_era += np.array([float(database['GWP_prod']['mechanical ventilation'].split(",")[1]),float(database['GWP_disp']['mechanical ventilation'].split(",")[1])]) * max_aussenluft_volumenstrom
         
         embodied_ventilation = ventilation_embodied_per_era * energy_reference_area * 1 #(RSP/ ventilation_lifetime) 


    else:
        embodied_ventilation = np.array([0.0,0.0])
    

    
    ######### Calculation of embodied emissions for the electrical systems
    ## PV System
    if pv_type != None: 
        pv_embodied_per_kw = np.array([database['GWP_prod'][pv_type],database['GWP_disp'][pv_type]]) # this data is in kgCO2eq/kWp
        
        pv_embodied = pv_embodied_per_kw * pv_area * pv_efficiency * 1# (RSP/ pv_lifetime)  # at STC Irradiance = 1kW/m2
    else:
        pv_embodied = np.array([0.0,0.0])
    embodied_electrical = pv_embodied #TODO: Question if general electrical installatinos shoud be included?


    ######### embodied emissions of batteries
    battery_embodied_per_kWh = np.array([database['GWP_prod']['battery'],database['GWP_disp']['battery']]) 

    embodied_battery = battery_capacity/1000 * battery_embodied_per_kWh * 1# (RSP/ battery_lifetime)  # division by 1000 because battery input comes in Wh


    ######### Calculation of total embodied building systems (annualized per ERA): heater, cooler, distribution, emission, electric (PV), ventilation per energy reference area. 

    embodied_thermal_electrical_vent = (embodied_thermal + embodied_electrical + embodied_ventilation + embodied_battery)/(energy_reference_area*RSP)
    return embodied_thermal_electrical_vent





"""New Version, Dominic, Based on Inner and Outer Enveloppe, as well as Core""" 

def calculate_envelope_emissions(database,RSP,energy_reference_area, floors_ag,
                                 window_type, total_window_area, wall_type_ag,total_wall_area_ag, roof_type,total_roof_area, 
                                 ceiling_to_basement_type, floor_area, ceiling_type,
                                 wall_type_bg,total_wall_area_bg, slab_basement,partitions_type,total_area_partitions,tilted_roof_type,
                                 simplifed_LCA = True, decarbonization_frac_2050 = 1, int_finishings_replacement_at_intervention = True):
         
    """
        This Function calculates the annualized embodied emissions of new or retrofitted construction elements per ERA due to the demolishment 
        
        
        Area inputs: in m2 for the corresponding construction 
        constructions: Lists of ID's of each Layer with corresponding entries in the Database. e.g. Wall core (loadbearing) and Wall shell (insulation)
        window_type
        wall_type_ag
        roof_type
        ceiling_to_basement_type
        ceiling_type
        wall_type_bg
        slab_basement
        partitions_type
        tilted_roof_type
        int_finishings_replacement_at_intervention -> can be set to False, but ONLY for renovations! not for new Buildings! 
        decarbonization_frac_2050: fraction of embodied emssions in 2050, (of emissions now). -> Linear decarbonization assumption
        
        
        ACTUAL MISSING:    
        TODO: Integrate emissions of "Baugrube?"
        
        
    """
    floor_area_ceiling = floor_area * (floors_ag - 1)
    constructions  = [[window_type],wall_type_ag,roof_type,ceiling_to_basement_type,ceiling_type,wall_type_bg,slab_basement,partitions_type,tilted_roof_type] 
    areas = [total_window_area,total_wall_area_ag,total_roof_area,floor_area,floor_area_ceiling,total_wall_area_bg,floor_area,total_area_partitions,total_roof_area] 
    
    LCIA_production = 0
    LCIA_disposal = 0
    LCIA_Biogenic = 0
    
    LCIA_production_upfront = 0
    LCIA_disposal_upfront = 0
    LCIA_Biogenic_upfront = 0
    
    
    for i,construction in enumerate(constructions):
        if construction is None: continue
        
        for j, layer in enumerate(construction):
            #simplifyed LCA calculats only core and insulation (not interior and exterior finishings)
            if simplifed_LCA and i != 0 and (j == 0 or j == 3): #i !=0 is the exception for the windows 
                continue
            
            # If the layer is never changed, e.g. stays over the whole life of the building. RSL = RSP 
            # -> this enables to use different service lifes of the buildings (RSP)
            if database.loc[layer,'RSL']=='RSP':
                RSL = RSP
            else: 
                RSL = database.loc[layer,'RSL']
            
            first_replacement = True
            # Exclude the replacement of interior finishings for the intervention (but they are then counted for the later replacements) 
            if ((int_finishings_replacement_at_intervention == False) and ((i in [1,2,3] and j == 0) or (i in [4,7] and j in[0,3]))): #(i in [1,2,3] and j == 0) Are the interior layers of wall_ag, roof, ceiling to basement, (i in [4,7] and j in[0,3]) are the finishing layers of ceilings and partitions  
                first_replacement = False
           
            
            #sanitiy checks
            # construction_names  = ['window_type','wall_type_ag','roof_type','ceiling_to_basement_type','ceiling_type','wall_type_bg','slab_basement','partitions_type','tilted_roof_type'] 
            # print('construction: ',construction_names[i],'Layer: ',layer)
            # print('area: ', areas[i])
            
           
            
            if database.loc[layer, 'Old_component']== True: #for old components, no first replacements, since reused. The core is always the same! Afterwords the components are replaced with the same materials (conservative assumpion)
               
                # TODO: Questino how to count the biogenic stored carbon, which is reused for one rotation period 
                # actually counted with the GWP bio approach, since it is stored agian. The -1/+1 approach seems also reasonabile. 
                
                LCIA_production +=  database['GWP_prod'][layer] * areas[i] * embodied_emissions_decarbonization_factor_construction(RSL,RSP, decarbonization_frac_2050, first_replacement = False)   # 0
                LCIA_disposal += database['GWP_disp'][layer]*areas[i] + database['GWP_disp'][layer]*areas[i] * embodied_emissions_decarbonization_factor_construction(RSL,RSP, decarbonization_frac_2050, first_replacement = False) # One disposal extra, due to the original constructino  #database['GWP_disp'][layer]*areas[i] 
                LCIA_Biogenic +=  database['GWP_Bio'][layer]*areas[i] + database['GWP_Bio'][layer]* areas[i] * embodied_emissions_decarbonization_factor_construction(RSL,RSP, 1 , first_replacement=False) # No decarbonization of CO2 Bio strored! # 0
                #TODO: line LCIA_Biogenic: first element due to disposal later (not at intervention). open question if -1, 0 or dynamic approach should be used! CO2_bio_stored or GWP_Bio
                
                #sanitiy checks
                # construction_names  = ['window_type','wall_type_ag','roof_type','ceiling_to_basement_type','ceiling_type','wall_type_bg','slab_basement','partitions_type','tilted_roof_type'] 
                # print('construction: ',construction_names[i],'Layer: ',layer)
                # print('area: ', areas[i])
                # print('LCIA values: prod, disp, bio: ',database['GWP_prod'][layer] * areas[i] * embodied_emissions_decarbonization_factor_construction(RSL,RSP, decarbonization_frac_2050, first_replacement = False)  , database['GWP_disp'][layer]*areas[i] + database['GWP_disp'][layer]*areas[i] * embodied_emissions_decarbonization_factor_construction(RSL,RSP, decarbonization_frac_2050, first_replacement = False)  , database['CO2_bio_stored'][layer]*areas[i] + database['GWP_Bio'][layer]* areas[i] * embodied_emissions_decarbonization_factor_construction(RSL,RSP, 1 , first_replacement=False))
                #print('test old component')
                
                #OLD configuration, NO replacement of layers, e.i. optimistic approach. 
                # LCIA_production +=  0
                # LCIA_disposal +=  database['GWP_disp'][layer]*areas[i] 
                # LCIA_Biogenic +=  0
                  
                    
            
            else: 
                # Calculate all embodied emissions of the construction (for all non old components)
                LCIA_production += database['GWP_prod'][layer] * areas[i] * embodied_emissions_decarbonization_factor_construction(RSL,RSP, decarbonization_frac_2050, first_replacement)                #*(RSP/RSL)
                LCIA_disposal += database['GWP_disp'][layer]*areas[i] * embodied_emissions_decarbonization_factor_construction(RSL,RSP, decarbonization_frac_2050, first_replacement)                    #*(RSP/RSL)
                LCIA_Biogenic += database['GWP_Bio'][layer]* areas[i] * embodied_emissions_decarbonization_factor_construction(RSL,RSP, 1 , first_replacement) # No decarbonization of CO2 Bio strored!  #*(RSP/RSL)
                
                
                # Here the disposal emissions are accounted, for the first disposal of interior finishings in case of a renovation and if at the intervention no internal finishings were changed. 
                # TODO: discuss how to count those emissions: reduction on disposal ? and how to deal with the biogenic ones...
                if first_replacement == False: 
                    LCIA_production += 0
                    LCIA_disposal += database['GWP_disp'][layer]*areas[i] * 1
                    LCIA_Biogenic += database['GWP_Bio'][layer]* areas[i] * 1 #Open question how biogenic stored carbon shold be accounted
                    #print('sanity check disposal int.finishings. late replacement')
               
                #calculate upfront emissions, all emissions of the first rotation (before replacement) are accounted: prod, disp and biogenic if true
                if first_replacement == True:   
                    LCIA_production_upfront += database['GWP_prod'][layer] * areas[i]
                    LCIA_disposal_upfront += database['GWP_disp'][layer]*areas[i] # IMPORTANT: THIS EMISSIONS ARE NOT COUNTED TO THE UPFRONT EMISSIONS (IN simulation_setup.py)!
                    LCIA_Biogenic_upfront += database['GWP_Bio'][layer]* areas[i]
                    #sanity checks:
                    # print(layer,database['GWP_prod'][layer] * areas[i] )
                     
                
    #Norm the Emissions to the service live of the Building RSP and the energy reference area ERA        
    LCIA_production = LCIA_production/(RSP*energy_reference_area)
    LCIA_disposal = LCIA_disposal/(RSP*energy_reference_area)
    LCIA_Biogenic = LCIA_Biogenic/(RSP*energy_reference_area)
    
    LCIA_production_upfront = LCIA_production_upfront/(RSP*energy_reference_area)
    LCIA_disposal_upfront = LCIA_disposal_upfront/(RSP*energy_reference_area)
    LCIA_Biogenic_upfront = LCIA_Biogenic_upfront/(RSP*energy_reference_area)
   

    return np.array([LCIA_production, LCIA_disposal, LCIA_Biogenic]), np.array([LCIA_production_upfront, LCIA_disposal_upfront, LCIA_Biogenic_upfront])







def calculate_envelope_emissions_demolished(database,RSP,energy_reference_area,floors_ag,
                                 window_type, total_window_area, wall_type_ag,total_wall_area_ag, roof_type,total_roof_area, 
                                 ceiling_to_basement_type, floor_area, ceiling_type,
                                 wall_type_bg,total_wall_area_bg, slab_basement,partitions_type,total_area_partitions, tilted_roof_type,
                                 simplifed_LCA = True):
    """
    This Function calculates the annualized embodied emissions of the construction per ERA due to the demolishment 
    Important: all construction type inputs must be ist of the different layers, also if there is only one layer .
    
        This function calculate the embodied emissions of the building envelope per year (based on RSP of Building) and Energy Reference Area
        
        
        Area inputs: in m2 for the corresponding construction 
        constructions: Lists of ID's of each Layer with corresponding entries in the Database. e.g. Wall core (loadbearing) and Wall shell (insulation)
        window_type
        wall_type_ag
        roof_type
        ceiling_to_basement_type
        ceiling_type
        wall_type_bg
        slab_basement
        partitions_type
        tilted_roof_type
        
        TODO: QUESTION how to deal with CO2 stored? 
        
    """
   
    
   
    floor_area_ceiling = floor_area * (floors_ag - 1)
    constructions  = [[window_type],wall_type_ag,roof_type,ceiling_to_basement_type,ceiling_type,wall_type_bg,slab_basement,partitions_type,tilted_roof_type] 
    areas = [total_window_area,total_wall_area_ag,total_roof_area,floor_area,floor_area_ceiling,total_wall_area_bg,floor_area,total_area_partitions,total_roof_area] 
    
    
    LCIA_disposal = 0
    LCIA_Biogenic = 0
    
    for i,construction in enumerate(constructions):
        if construction is None: continue
        
        for j, layer in enumerate(construction):
            #simplifyed LCA calculats only core and insulation (not interior and exterior finishings)
            if simplifed_LCA and i != 0 and (j == 0 or j == 3): #i !=0 is the exception for the windows 
                continue

            # Calculate all embodied emissions of the construction             
            LCIA_disposal += database['GWP_disp'][layer]*areas[i]
            LCIA_Biogenic += database['CO2_bio_stored'][layer]*areas[i]     # Here the +1 approach is used, since biogenic materials are typically burned and no credits for buildings before 1990
   
    #Norm the Emissions to the service live of the Building RSP and the energy reference area ERA        
    LCIA_disposal = LCIA_disposal/(RSP*energy_reference_area)
    LCIA_Biogenic = LCIA_Biogenic/(RSP*energy_reference_area)
    

    return np.array([0,LCIA_disposal, LCIA_Biogenic])


if __name__ == "__main__":
    pass

