"""
Mobile broadband simulation model.

Developed by Bonface Osoro and Ed Oughton.

October 2024

"""
import math
import itertools
import numpy as np


############################
######## COST MODEL ########
############################
def capex_cost(olt_usd, civil_usd, transportation_usd, installation_usd, 
               rpu_usd, odf_unit_usd, length_km, nodes):
    """
    This function calculates capital expenditures

    Parameters
    ----------
    olt_usd : int.
        Cost of Optical Line Terminal.
    civil_usd : int.
        Total civil construction costs.
    transportation_usd : int.
        Cost of transporting equipment and staff during construction.
    installation_usd : int.
        Total cost of installing the macro base station.
    rpu_usd : int.
        Total cost of Remote Power Unit.
    odf_unit_usd : int.
        Total cost of Optical Distribution Frame.
    length_km : float.
        Total length of fiber optic cable.
    nodes : int.
        Total number of fiber terminal nodes.

    Returns
    -------
    capex_costs : float
            The capital expenditure costs.

    """
    unit_costs = ((olt_usd + civil_usd + installation_usd + rpu_usd + 
                   odf_unit_usd) * nodes) 
    transportation_cost = (transportation_usd * length_km) 
    capex_costs = (unit_costs + transportation_cost)


    return capex_costs


def opex_cost(rent_usd, staff_usd, cost_kWh, regulatory_usd,
              customer_usd, other_costs_usd, nodes, assessment_years, 
              node_power_kWh_per_km_gbps, fiber_speed_gbps, length_km):
    """
    This function calculates operating expenditures

    Parameters
    ----------
    rent_usd : int.
        Annual land rental cost.
    staff_usd : int.
        Total staff costs.
    cost_kWh : int.
        Cost of electricity in USD per kWh.
    power_usd : int.
        Total power cost.
    regulatory_usd : int.
        Total regulatory cost.
    customer_usd : int.
        Total cost of customer acquisition.
    other_costs_usd : int.
        All other costs.
    nodes : int.
        Total number of fiber terminal nodes.
    length_km : float.
        Total length fiber optic cable.
    assessment_years : int.
        assessment period of the infrastructure.
    node_power_kWh_per_km_gbps : float.
        Power consumption per Gbps per km.
    fiber_speed_gbps : float
        Speed of the fiber broadband

    Returns
    -------
    annual_opex : float
            The operating expenditure costs annually.

    """
    power_cost = (cost_kWh * fiber_speed_gbps * assessment_years 
                  * node_power_kWh_per_km_gbps * length_km
                  * 24 * 365) # 24 hours in a day # 365 days a year
    annual_opex = (((rent_usd + staff_usd + other_costs_usd) * nodes) 
                 + regulatory_usd + customer_usd) + power_cost
    

    return annual_opex


def total_cost_ownership(total_capex, total_opex, discount_rate, 
                         assessment_period):
    """
    Calculate the total cost of ownership(TCO) in US$:

    Parameters
    ----------
    total_capex : int.
        Total initial capital expenditures.
    total_opex : int.
        Total annual operating expenditures.
    discount_rate : float.
        discount rate.
    assessment_period : int.
        assessment period of the infrastructure.

    Returns
    -------
    total_cost_ownership : float
            The total cost of ownership.

    """

    year_costs = []

    for time in np.arange(1, assessment_period):  

        yearly_opex = total_opex / (((discount_rate / 100) + 1) ** time)
        year_costs.append(yearly_opex)

    total_cost_ownership = total_capex + sum(year_costs) + total_opex


    return total_cost_ownership


#################################
######## EMISSIONS MODEL ########
#################################

def lca_manufacturing(fiber_cable_kg_per_km, pcb_kg, pvc_kg, steel_kg, 
                      concrete_kg, glass_kg_co2e, pcb_carbon_factor, 
                      steel_kg_co2e, concrete_kg_co2e, pvc_carbon_factor, 
                      length_km, nodes):
    """
    This function calculates the total GHG emissions in the manufacturing 
    phase LCA of fiber broadband using carbon emission factors.

    Parameters
    ----------
    fiber_cable_kg_per_km : float.
        Mass of fiber optic cable per km.
    pcb_kg : float.
        Mass of printed circuit board.
    pvc_kg : float.
        Mass of PVC material used in building node components.
    steel_kg : float.
        Mass of steel metal used in building node componentsa.
    concrete_kg : float.
        Mass of concrete for every terminal node.
    length_km : float.
        Total length fiber optic cable.
    nodes : int.
        Total number of fiber terminal nodes.

    glass_kg_co2e, pcb_carbon_factor, steel_kg_co2e, pvc_carbon_factor : float.
        Carbon emission factors sof PCB, alumnium, PVC, and concrete respectively.

    Returns
    -------
    mfg_emissions : float
        Manufacturing GHG emissions.

    """
    glass_ghg = (fiber_cable_kg_per_km * length_km * glass_kg_co2e)

    pcb_ghg = (pcb_kg * pcb_carbon_factor) * length_km
    
    steel_ghg = (steel_kg * steel_kg_co2e) * length_km

    concrete_ghg = (concrete_kg * concrete_kg_co2e)
    
    pvc_ghg = (pvc_kg * pvc_carbon_factor) * length_km

    mfg_emissions = (((steel_ghg + concrete_ghg + pcb_ghg + pvc_ghg) * nodes) + 
                     glass_ghg)


    return mfg_emissions


def lca_transportation(distance_km, consumption_lt_per_km, diesel_factor_kgco2e,
                       maritime_km, container_ship_kgco2e):
    """
    This function calculates the total GHG emissions in the transportation 
    LCA phase of fiber broadband deployment.

    Parameters
    ----------
    distance_km : float.
        Distance travelled by the vehicle.
    consumption_lt_per_km : float.
        Fuel consumption of the vehicle per distance.
    diesel_factor_kgco2e : float.
        Carbon emission factor of diesel fuel.
    maritime_km : float
        Distance between the port of China and SSA country.
    container_ship_kgco2e : float
        Carbon emission factor of a container ship.

    Returns
    -------
    trans_emissions : float
        Transportation GHG emissions.
    """

    maritime_ghg = maritime_km * container_ship_kgco2e

    road_ghg = (distance_km * consumption_lt_per_km * diesel_factor_kgco2e)

    trans_emissions = maritime_ghg + road_ghg


    return trans_emissions


def maritime_distance(iso3, maritime_dict):
    """
    This function calculates the distance between the origin Port of China and 
    any SSA country

    Parameters
    ----------
    iso3 : string.
        Country ISO3.
    maritime_dict : dict
        Dictionary containing ISO3 codes as keys and distances as values.

    Returns
    -------
    distance_km : float
        Distance between the two ports
    """

    return maritime_dict.get(iso3, None)


def lca_construction(fuel_efficiency, machine_operating_hours, 
                     diesel_factor_kgco2e, nodes):
    """
    This function calculates the total GHG emissions in the construction 
    LCA phase of fiber broadband deployment.

    Parameters
    ----------
    fuel_efficiency : float.
        Fuel efficiency of the machine.
    machine_operating_hours : float.
        Number of hours the machine operated.
    diesel_factor_kgco2e : float.
        Carbon emission factor of diesel fuel.
    nodes : int.
        Total number of fiber terminal nodes.

    Returns
    -------
    construction_emissions : float
        Construction GHG emissions.
    """

    construction_emissions = (fuel_efficiency * machine_operating_hours 
                     * diesel_factor_kgco2e) * nodes


    return construction_emissions


def electricity_cost(iso3, electricity_dict):
    """
    This function calculates the cost of electricity in each SSA country

    Parameters
    ----------
    iso3 : string.
        Country ISO3.
    electricity_dict : dict
        Dictionary containing ISO3 codes as keys and distances as values.

    Returns
    -------
    cost_kWh : float
        Cost of electricity
    """

    return electricity_dict.get(iso3, None)


def lca_operations(node_power_kWh_per_km_gbps, fiber_speed_gbps, cost_kWh, 
                   assessment_years, electricity_kg_co2e, length_km):
    """
    This function calculates the total GHG emissions due to operation of the 
    fiber broadband

    Parameters
    ----------
    fiber_point_pwr_kwh : float.
        Total power consumption of fiber node station.
    electricity_kg_co2e : float.
        Carbon emission factor of electricity.
    length_km : float.
        Total length fiber optic cable.
    assessment_years : int.
        assessment period of the infrastructure.
    node_power_kWh_per_km_gbps : float.
        Power consumption per Gbps per km.
    fiber_speed_gbps : float
        Speed of the fiber broadband

    Returns
    -------
    operations_emissions : float
        Operations GHG emissions.
    """

    operations_ghg_kg = (node_power_kWh_per_km_gbps * fiber_speed_gbps * 
                         assessment_years * cost_kWh * 24 * 365 * 
                         electricity_kg_co2e)

    operations_emissions = operations_ghg_kg * length_km


    return operations_emissions


def lca_eolt(fiber_cable_kg_per_km, pcb_kg, pvc_kg, steel_kg, router, 
             glass_eolt_kg_co2e, plastics_factor_kgco2e, metals_factor_kgco2e, 
             length_km, nodes):
    """
    This function calculates the total GHG emissions in the end-of-life treatment 
    phase LCA of fiber broadband using carbon emission factors.

    Parameters
    ----------
    fiber_cable_kg_per_km : float.
        Mass of fiber optic cable per km.
    pcb_kg : float.
        Mass of printed circuit board.
    pvc_kg : float.
        Mass of PVC material used in building node components.
    steel_kg : float.
        Mass of steel metal used in building node componentsa.
    router : float.
        Mass of router for every terminal node.
    plastics_factor_kgco2e : float.
        Carbon emissions factor of plastics.
    metals_factor_kgco2e : float.
        Carbon emissions factor of metals.
    length_km : float.
        Total length fiber optic cable.
    nodes : int.
        Total number of fiber terminal nodes.

    Returns
    -------
    eolt_emissions : dict
        Dictionary containing GHG emissions by type.

    """
    glass_ghg = (fiber_cable_kg_per_km * length_km * glass_eolt_kg_co2e)

    plastics_ghg = ((pcb_kg + pvc_kg) * plastics_factor_kgco2e) * length_km

    steel_ghg = (steel_kg * metals_factor_kgco2e) * length_km

    eolt_emissions =  plastics_ghg + glass_ghg + steel_ghg


    return eolt_emissions


def social_carbon_cost(total_emissions, cost_per_tonne):
    """
    This function calculates the social carbon cost of GHG emissions.

    Parameters
    ----------
    total_emissions : float.
        Total GHG emissions.
    cost_per_tonne : int.
        Dollar cost per tonne of carbon emission.

    Returns
    -------
    social_carbon_cost : float
        Social carbon cost.
    """

    social_carbon_cost = ((total_emissions / 1e3) * cost_per_tonne) 


    return social_carbon_cost