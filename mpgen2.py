import numpy as np
import pandas as pd

# Costanti fisiche
G = 6.67430e-11  # Costante gravitazionale in m^3 kg^-1 s^-2
k_B = 1.380649e-23  # Costante di Boltzmann in J/K
m_H = 1.6735575e-27  # Massa dell'idrogeno in kg
sigma = 5.670374419e-8  # Costante di Stefan-Boltzmann in W⋅m^−2⋅K^−4
L_sun = 3.828e26  # Luminosità solare in W

# Parametri predefiniti
DEFAULT_MASS_PLANET = 1.0 * 5.972e24  # Massa terrestre in kg
DEFAULT_RADIUS_PLANET = 1.0 * 6.371e6  # Raggio terrestre in m
DEFAULT_INSOLATION = 1.0 * 1361  # Insolazione terrestre in W/m^2
DEFAULT_STELLAR_TEMP = 5778  # Temperatura del Sole in K
DEFAULT_STELLAR_METALLICITY = 0.0  # Metallicità solare (log(Fe/H) rispetto al Sole)
DEFAULT_STELLAR_MASS = 1.0  # Massa solare in masse solari
DEFAULT_STELLAR_TYPE = "G2V"  # Tipo spettrale del Sole

# Parametri per il calcolo del GHE
alpha = 0.18  # Parametro α per il GHE
beta = 2.5  # Parametro β per il GHE

# Carica il database esoplanetario
data = pd.read_csv("database230-430.txt", delimiter='\t', comment='#')

# Aggiunta delle colonne per i gas serra, se non esistono già
data['h2o_presence'] = data.get('h2o_presence', 0)
data['co2_presence'] = data.get('co2_presence', 0)
data['ch4_presence'] = data.get('ch4_presence', 0)

# Funzione per calcolare il range di pressione
def calculate_pressure_range(mass_planet, radius_planet, temp_equilibrium, num_samples=1000):
    gravity_surface = G * mass_planet / (radius_planet**2)
    H = k_B * temp_equilibrium / (2 * m_H * gravity_surface)
    P_base = 1e5  # 1 bar in Pa
    pressure_range = np.random.lognormal(mean=np.log(P_base), sigma=2, size=num_samples)
    gravity_earth = 9.8  # m/s^2
    gravity_factor = gravity_surface / gravity_earth
    pressure_range *= gravity_factor
    pressure_range /= 1e5  # Convertire in bar
    pressure_range = np.clip(pressure_range, 1e-12, 1e4)  # da 1 pico-bar a 10000 bar
    return pressure_range

# Funzione per calcolare le temperature con il GHE dinamico
def calculate_tidal_locked_temperatures(insolation, albedo, greenhouse_effects, efficiency_factor, alpha, beta, mass_planet, radius_planet, num_samples=1000):
    temp_equilibrium = ((insolation * (1 - albedo)) / (4 * sigma))**0.25
    
    # Calcolo della velocità di fuga
    escape_velocity = np.sqrt(2 * G * mass_planet / radius_planet)
    
    # Calcolo del GHE di base con i parametri α e β
    GHE_base = alpha * (temp_equilibrium / escape_velocity)**beta
    
    # Correzione per l'effetto serra, includendo i gas rilevati
    greenhouse_correction = 1 + sum(greenhouse_effects) * GHE_base
    
    # Temperature diurne e notturne
    T_day = temp_equilibrium * ((2 * (1 - albedo)) / (2 - efficiency_factor))**0.25 * greenhouse_correction
    T_night = temp_equilibrium * (efficiency_factor / (2 - efficiency_factor))**0.25 * greenhouse_correction
    
    temperature_day = np.random.normal(loc=T_day, scale=T_day*0.05, size=num_samples)
    temperature_night = np.random.normal(loc=T_night, scale=T_night*0.05, size=num_samples)
    temperature_day = np.clip(temperature_day, 0, 2000)
    temperature_night = np.clip(temperature_night, 0, temperature_day)
    
    return temperature_day, temperature_night, temp_equilibrium

# Funzione per stimare le radiazioni X e UV
def estimate_xray_uv_radiation(stellar_mass, stellar_temp, metallicity, spectral_type):
    metallicity_factor = 10**metallicity
    spectral_factors = {'O': 1000, 'B': 100, 'A': 10, 'F': 1, 'G': 0.1, 'K': 0.01, 'M': 0.001}
    
    if isinstance(spectral_type, str):
        spectral_factor = spectral_factors.get(spectral_type[0].upper(), 1)
    else:
        spectral_factor = spectral_factors.get(DEFAULT_STELLAR_TYPE[0].upper(), 1)
    
    L_x = L_sun * 1e-6 * (stellar_mass**3) * (stellar_temp/5778)**4 * metallicity_factor * spectral_factor
    L_uv = L_sun * 1e-2 * (stellar_mass**2) * (stellar_temp/5778)**5 * metallicity_factor * spectral_factor
    return L_x, L_uv

# Lista per memorizzare i risultati
results = []

# Itera su ogni riga del database esoplanetario
for index, row in data.iterrows():
    planet_name = row['pl_name']
    
    try:
        mass_planet = float(row['pl_masse']) * 5.972e24 if not pd.isna(row['pl_masse']) else DEFAULT_MASS_PLANET
        radius_planet = float(row['pl_rade']) * 6.371e6 if not pd.isna(row['pl_rade']) else DEFAULT_RADIUS_PLANET
        insolation = float(row['pl_insol']) * 1361 if not pd.isna(row['pl_insol']) else DEFAULT_INSOLATION
        stellar_temp = row['st_teff'] if not pd.isna(row['st_teff']) else DEFAULT_STELLAR_TEMP
        stellar_metallicity = row['st_met'] if not pd.isna(row['st_met']) else DEFAULT_STELLAR_METALLICITY
        stellar_mass = row['st_mass'] if not pd.isna(row['st_mass']) else DEFAULT_STELLAR_MASS
        stellar_type = row['st_spectype'] if not pd.isna(row['st_spectype']) else DEFAULT_STELLAR_TYPE
        
        # Raccolta dei gas serra
        greenhouse_effects = []
        if row['h2o_presence'] == 1:
            greenhouse_effects.append(0.1)
        if row['co2_presence'] == 1:
            greenhouse_effects.append(0.15)
        if row['ch4_presence'] == 1:
            greenhouse_effects.append(0.2)
        
        temperature_day_min, temperature_day_max = None, None
        pressure_min, pressure_max = None, None
        F_x_min, F_x_max = None, None
        F_uv_min, F_uv_max = None, None
        
        if mass_planet and radius_planet and insolation:
            temperature_day, temperature_night, temp_equilibrium = calculate_tidal_locked_temperatures(
                insolation, albedo, greenhouse_effects, efficiency_factor, alpha, beta, mass_planet, radius_planet)
            pressure_range = calculate_pressure_range(mass_planet, radius_planet, temp_equilibrium)
            L_x, L_uv = estimate_xray_uv_radiation(stellar_mass, stellar_temp, stellar_metallicity, stellar_type)

            distance_star = np.sqrt(L_sun / (4 * np.pi * insolation))
            F_x = L_x / (4 * np.pi * distance_star**2)
            F_uv = L_uv / (4 * np.pi * distance_star**2)

            temperature_day_min, temperature_day_max = temperature_night.min(), temperature_day.max()
            pressure_min, pressure_max = pressure_range.min(), pressure_range.max()
            F_x_min, F_x_max = F_x.min(), F_x.max()
            F_uv_min, F_uv_max = F_uv.min(), F_uv.max()
        
        results.append([
            planet_name,
            temperature_day_min,
            temperature_day_max,
            pressure_min,
            pressure_max,
            F_x_min,
            F_x_max,
            F_uv_min,
            F_uv_max
        ])
    
    except ValueError:
        continue

# Salva i risultati in un file di output strutturato a colonne
output_df = pd.DataFrame(results, columns=[
    'Planet Name', 'Min Temperature [K]', 'Max Temperature [K]',
    'Min Pressure [bar]', 'Max Pressure [bar]',
    'Min X-ray Radiation [W/m^2]', 'Max X-ray Radiation [W/m^2]',
    'MinPressure', 'Max Pressure',
    'Min X-ray Radiation', 'Max X-ray Radiation',
    'Min UV Radiation', 'Max UV Radiation'
])
output_df.to_csv("exoplanet_results.csv", index=False)

print("I risultati sono stati salvati nel file exoplanet_results.csv")