parameters = {                                            
    'regional': {
        'olt_low_usd' : 11000,
        'olt_high_usd' : 13000,
        'civil_low_usd' : 5000,
        'civil_high_usd' : 8000,
        'transportation_low_usd' : 80,
        'transportation_high_usd' : 120,
        'installation_low_usd' : 300,
        'installation_high_usd' : 400,
        'rpu_low_usd': 5000,
        'rpu_high_usd': 6000,
        'odf_unit_low_usd': 400,
        'odf_unit_high_usd': 600,
        'rent_low_usd': 1000, 
        'rent_high_usd': 1500,
        'staff_low_usd': 100000,
        'staff_high_usd': 150000,
        'power_low_usd': 500,
        'power_high_usd': 600,
        'regulatory_low_usd': 50000,
        'regulatory_high_usd': 60000,
        'customer_low_usd': 100000,
        'customer_high_usd': 120000,
        'other_low_costs_usd': 5000,
        'other_high_costs_usd': 8000,
        'fiber_cable_per_km_kg' : 70,
        'pcb_low_kg' : 0.5,
        'pcb_high_kg' : 0.7,
        'pvc_low_kg' : 0.8,
        'pvc_high_kg' : 1.2,
        'aluminium_low_kg' : 0.8,
        'aluminium_high_kg' : 1.2,
        'concrete_low_kg' : 15,
        'concrete_high_kg' : 17,
        'low_router' : 8,
        'high_router' : 10,
        'discount_rate_percent': 8.33,
        'assessment_period_year': 30,
        'pcb_kg_co2e' : 29.76,
        'aluminium_kg_co2e' : 19.4,
        'copper_kg_co2e' : 4.91,
        'pvc_kg_co2e' : 3.413,
        'iron_kg_co2e' : 2.14,
        'steel_kg_co2e' : 2.56,
        'concrete_kg_co2e' : 120,
        'olnu_kg_co2e' : 0.3234,
        'electricity_kg_co2e' : 0.19338,
        'plastics_factor_kgco2' : 21.28,
        'metals_factor_kgco2' : 0.9847,
        'diesel_factor_kgco2e' : 2.68,
        'fuel_efficiency_low' : 20.23,
        'fuel_efficiency_high' : 25.23,
        'trench_percent' : 0.01,
        'hours_low_per_km' : 1,
        'hours_high_per_km' : 5,
        'fiber_point_pwr_low_kwh' : 5,
        'fiber_point_pwr_high_kwh' : 8,
        'social_carbon_cost_usd' : 75,
        'iterations' : 50,
        'seed_value' : 42,
        'mu' : 2, 
        'sigma' : 10,
        'draws' : 100 
    }
}

carbon_factors = {
    'mfg_emissions' : {
        'glass_kg_co2e' : 1.403,
        'pcb_kg_co2e' : 29.76,
        'aluminium_kg_co2e' : 19.4,
        'copper_kg_co2e' : 4.91,
        'pvc_kg_co2e' : 3.413,
        'iron_kg_co2e' : 2.14,
        'steel_kg_co2e' : 2.56,
        'concrete_kg_co2e' : 120,
        'olnu_kg_co2e' : 0.3234,
        'electricity_kg_co2e' : 0.19338
    },
    'eolt_emissions' : {
        'glass_kg_co2e' : 21.2801938,
        'pcb_kg_co2e' : 21.2801938,
        'metals_kg_co2e' : 0.98470835,
        'concrete_kg_co2e' : 0.98470835,
    },
    'trans_emissions' : {
        'olnu_router_kg_co2e' : 0.3234,
    },
    'ops_emissions' : {
        'electricity_kg_co2e' : 0.19338
    }
}

operations = {
   'power_consumption' : {
       'node_power_kwh' : 0.0132,
       'fiber_point_pwr_kwh' : 5,
       'terminal_unit_pwr_kwh' : 0.5
   }
}