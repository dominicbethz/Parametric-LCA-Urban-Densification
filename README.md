# Parametric-LCA-Urban-Densification

This model can be used to assess different types of densification interventions - refurbishment, replacement construction, and add storeys -  from a LCA perspective. 

## Basics methodology 
The life cycle impact assessment is calculated based on the designed intervention and quantified exogenous parameters, including modules A1-A3, B4, C3-C4, and B6, according to SN EN 15978:2011. Biogenic stored carbon was accounted for dynamically (Guest et al., 2013). The related energy demands were modeled with a monthly quasistatic approach to determine operational emissions. Therefore the Swiss building code SIA 380/1 was used, and the following model was incorporated:  [https://github.com/architecture-building-systems/sia_380-1-full_version](https://github.com/architecture-building-systems/sia_380-1-full_version).
The model approach is based on a single-box model. 

## Getting started
Download the repository and open the `Setup_Simulation.py`, modify the `main_path` and  `SIA_380_1_directory`. 

**To evaluate one building deterministically** open the `Scenario_Configurator.py`, adapt the `main_path`, choose the building, and specify the intervention.  To check everything in the installation worked properly, it is recommended to first run one building deterministically. 

**To run the global sensitivity analysis**, the files `multi_core_sa_main_big_2.py`and `multi_core_sa_model_big_2.py.` are needed. Specify in both the file directories. In the main file, the parameters can be adjusted (distribution and exclusion of some designs); the model file should not be adjusted except when different electricity grid decarbonization scenarios or fixed buildings RSP are used. 

**To assess intervention designs under uncertainty** the files `multi_core_main_robust_assessment.py`and `multi_core_model_big_2.py.` are needed. Specify in both the file directories. In the main file, the parameters can be adjusted (distribution and exclusion of some designs); the model file should not be adjusted except when other electricity grid decarbonization scenarios are applied. 
* For the default configuration, the designs of the thesis are assessed 
* To assess other intervention designs, just edit the `intervention_designs.xlsx` Excel with adding new designs, name the column *scenario_group* like the variable *scenario_group_multi* in the `multi_core_main_robust_assessment.py`file. 
* To assess other buildings/archetypes, create new ones in excel `Case_study_for_validation.xlsx`, refer to those in the `intervention_designs.xlsx` Excel (*original_building_archetype* column)

## Files Structure
* **To assess intervention designs under uncertainty**: `multi_core_main_robust_assessment.py`and `multi_core_model_big_2.py.`
* To run the global sensitivity analysis**: `multi_core_sa_main_big_2.py`and `multi_core_sa_model_big_2.py.`
* ***Deterministic evaluation of one building**: `Scenario_Configurator.py`


### FUNCTIONS
* `Simulation_setup.py`: The Main Function initializes the object Building and stores all related functions to configure and assess an intervention. 
* `qmc_sampling.py`: to sample the input space for different PDF's and sampling techniques
* `SIA_380_1\embodied_emissions_calculation.py`: calculates the systems and materials embodied emissions (complete newly written, independent of energy demand model)
* `SIA_380_1\data_prep.py`: input data and helper functions of the energy demand model  (adapted of original SIA_380_1)
* `simulation_engine.py`: calculates energy demands of one zone (original SIA_380_1)
* Other `SIA_380_1`files not used
* `Functions/general_helper.py`: Functions to read databases and other helper functions and store presets of new construction designs. 
* `Functions/cenario_configurator_helper.py`: This function assigns an intervention to a building.  

### INPUTS
* All inputs are stored in the folder `input_data`, except for: 
    * Presets of construction designs: `general_helper.py`
    * Fixed input data energy demand model: `data_prep.py`
    * Basic input configurations (some of them are in the probabilistic model overwritten): `general_helper.py`

* `Case_study_for_validation.xlsx`: Archetypes and material layers used for the archetypes (already built = old)
* `Construcion_db.xlsx`: no input, only defines the data frame structure in the program
* `duree_db.xlsx`: uncertainty data of components reference service life, according to (Goulouti et al., 2021)
* `envelope_assignement.xlsx`: To avoid infeasible material assembly configurations from a building physics perspective, exterior finishings were assigned based on the given insulation and core construction type
* `GWP_bio_values.xlsx`: To account for biogenic carbon, according to  (Guest et al., 2013) 
* `intervention_designs.xlsx`: stores the interventions, that are assessed under uncertainty
* `renovation_construction_db.xlsx`: material layers with GWP data and u-Values, based on KBOB
* `Systems_db_new.xlsx`: systems GWP values, based on KBOB
* `weather_data`: weather file (Zurich)


Guest et al., 2013: _Global Warming Potential of Carbon Dioxide Emissions from Biomass Stored in the Anthroposphere and Used for Bioenergy at End of Life_

Goulouti et al., 2021: _Dataset of service life data for 100 building elements and technical systems including their descriptive statistics and fitting to lognormal distribution_

