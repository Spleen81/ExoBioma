import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Carica i dati
input_df = pd.read_csv('database230-430.txt', delimiter='\t')
output_df = pd.read_csv('exoplanet_results.csv')

# Seleziona un campione di pianeti (ad esempio, 5)
sample_planets = ['Kepler-1143 c', 'KIC 9663113 b', 'LTT 1445 A b', 'Proxima Cen b', 'TOI-715 b']

def plot_planet_comparison(planet_name, input_data, output_data, ax):
    input_row = input_data[input_data['pl_name'] == planet_name].iloc[0]
    output_row = output_data[output_data['Planet Name'] == planet_name].iloc[0]

    # Temperatura
    ax.hlines(y=0, xmin=output_row['Min Average Temperature'], xmax=output_row['Max Average Temperature'], 
              color='blue', linewidth=2, label='Output Temp Range')
    ax.scatter(input_row['pl_eqt'], 0, color='red', s=50, label='Input Equilibrium Temp')

    ax.set_xlabel('Temperature (K)')
    ax.set_title(planet_name)

    # Aggiungi etichette con i valori numerici
    ax.text(output_row['Min Average Temperature'], 0, f'{output_row["Min Average Temperature"]:.0f}', 
            color='blue', ha='right', va='bottom')
    ax.text(output_row['Max Average Temperature'], 0, f'{output_row["Max Average Temperature"]:.0f}', 
            color='blue', ha='left', va='top')
    ax.text(input_row['pl_eqt'], 0, f'{input_row["pl_eqt"]:.0f}', color='red', ha='center', va='bottom')

    # Aggiungi informazioni su pressione e radiazioni UV nella legenda
    pressure_range = f'Pressure: {output_row["Min Pressure"]:.2e} - {output_row["Max Pressure"]:.2e} bar'
    uv_range = f'UV Radiation: {output_row["Min UV Radiation"]:.2e} - {output_row["Max UV Radiation"]:.2e}'
    ax.plot([], [], ' ', label=pressure_range)
    ax.plot([], [], ' ', label=uv_range)

    # Posiziona la legenda all'interno del grafico
    ax.legend(loc='upper right', fontsize='x-small', framealpha=0.7)

    # Imposta i limiti dell'asse x per ridurre la lunghezza
    x_min = min(output_row['Min Average Temperature'], input_row['pl_eqt']) * 0.97
    x_max = max(output_row['Max Average Temperature'], input_row['pl_eqt']) * 1.03
    ax.set_xlim(x_min, x_max)

    # Rimuovi i tick dell'asse y
    ax.set_yticks([])

# Crea il grafico
fig, axs = plt.subplots(len(sample_planets), 1, figsize=(5, 3*len(sample_planets)))
if len(sample_planets) == 1:
    axs = [axs]

for i, planet in enumerate(sample_planets):
    plot_planet_comparison(planet, input_df, output_df, axs[i])

plt.tight_layout()

# Salva il grafico
output_file = "exoplanet_comparison.png"
plt.savefig(output_file, dpi=300, bbox_inches='tight')
plt.close()

print(f"Il grafico di confronto ottimizzato con legenda interna per il campione di pianeti è stato salvato come '{output_file}'.")