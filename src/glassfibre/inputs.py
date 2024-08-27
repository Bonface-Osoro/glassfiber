parameters = {
    'supply': {
        'dslam_usd' : 11000,
        'civil_usd' : 5000,
        'transportation_usd' : 1000,
        'installation_usd' : 66,
        'rpu_usd': 5000,
        'mdf_unit_usd': 500,
        'rent_usd': 5000, 
        'staff_usd': 500000,
        'power_usd': 500,
        'regulatory_usd': 50000,
        'customer_usd': 100000,
        'other_costs_usd': 300000,
        'discount_rate_percent': 5,
        'assessment_period_year': 30
    },
    'construction_emissions' : {
        'diesel_kg_co2e' : 2.68,
        'fuel_efficiency' : 24.23,
        'trench_percent' : 0.01,
        'hours_per_km' : 1,
    },
}

weights = {
    'manufacturing' : {
        'fiber_cable_per_km_kg' : 70,
        'pcb_kg' : 0.5,
        'aluminium_bru_kg' : 0,
        'copper_antenna_kg' : 0,
        'aluminium_antenna_kg' : 0,
        'pvc_antenna_kg' : 1,
        'iron_antenna_kg' : 0,
        'steel_antenna_kg' : 0,
        'aluminium_frame_kg' : 1,
        'concrete_kg' : 17,
        'aluminium_device_kg' : 0
    },
    'transportation' : {
        'onu_router' : 10
    }

}

carbon_factors = {
    'mfg_emissions' : {
        'glass_kg_co2e' : 1403,
        'pcb_kg_co2e' : 29760,
        'aluminium_kg_co2e' : 19400,
        'copper_kg_co2e' : 4910,
        'pvc_kg_co2e' : 3413,
        'iron_kg_co2e' : 2140,
        'steel_kg_co2e' : 2560,
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
       'cpe_power_kwh' : 0.0132,
       'fiber_point_pwr_kwh' : 5,
       'terminal_unit_pwr_kwh' : 0.5
   }
}