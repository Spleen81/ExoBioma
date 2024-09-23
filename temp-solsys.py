import matplotlib.pyplot as plt
import numpy as np

# Dati dei pianeti (nome, temp_equilibrio, temp_min, temp_max)
planets_data = [
    ("Venus", 227, 437, 737),
    ("Earth", 255, 184, 330),
    ("Mars", 210, 130, 308),
    ("Jupiter", 110, 165, 112),  # Temp max < min per gli strati esterni
    ("Neptune", 47, 55, 72)
]

def plot_planet_comparison(planet_name, eq_temp, min_temp, max_temp, ax):
    ax.hlines(y=0, xmin=min_temp, xmax=max_temp, color='blue', linewidth=2, label='Observed Temp Range')
    ax.scatter(eq_temp, 0, color='red', s=50, label='Equilibrium Temp')

    ax.set_xlabel('Temperature (K)')
    ax.set_title(planet_name)

    # Aggiungi etichette con i valori numerici
    ax.text(min_temp, 0, f'{min_temp}', color='blue', ha='right', va='bottom')
    ax.text(max_temp, 0, f'{max_temp}', color='blue', ha='left', va='top')
    ax.text(eq_temp, 0, f'{eq_temp}', color='red', ha='center', va='bottom')

    # Posiziona la legenda all'interno del grafico
    ax.legend(loc='upper right', fontsize='x-small', framealpha=0.7)

    # Imposta i limiti dell'asse x
    x_min = min(min_temp, eq_temp) - 10
    x_max = max(max_temp, eq_temp) + 10
    ax.set_xlim(x_min, x_max)

    # Rimuovi i tick dell'asse y
    ax.set_yticks([])

# Crea il grafico
fig, axs = plt.subplots(len(planets_data), 1, figsize=(10, 3*len(planets_data)))

for i, (planet, eq_temp, min_temp, max_temp) in enumerate(planets_data):
    plot_planet_comparison(planet, eq_temp, min_temp, max_temp, axs[i])

plt.tight_layout()

# Salva il grafico
output_file = "solar_system_planets_temperature_comparison.png"
plt.savefig(output_file, dpi=300, bbox_inches='tight')
plt.close()

print(f"Il grafico di confronto delle temperature dei pianeti del sistema solare salvato come '{output_file}' nella cartella corrente.")