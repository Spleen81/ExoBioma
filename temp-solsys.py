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

# Assegna un colore differente a ogni pianeta
planet_colors = {
    "Venus": "orange",
    "Earth": "green",
    "Mars": "red",
    "Jupiter": "purple",
    "Neptune": "blue"
}

def plot_planet_comparison(planet_name, eq_temp, min_temp, max_temp, ax, x_range, x_ticks):
    # Imposta il colore per ogni pianeta
    planet_color = planet_colors.get(planet_name, 'blue')
    
    # Linea orizzontale per il range osservato
    ax.hlines(y=0, xmin=min_temp, xmax=max_temp, color=planet_color, linewidth=2, label='Observed Temp Range')
    
    # Punto per la temperatura di equilibrio (giallo)
    ax.scatter(eq_temp, 0, color='yellow', s=50, label='Equilibrium Temp')

    ax.set_xlabel('Temperature (K)')
    ax.set_title(planet_name, color=planet_color)

    # Aggiungi etichette con i valori numerici
    ax.text(min_temp, 0, f'{min_temp}', color=planet_color, ha='right', va='bottom')
    ax.text(max_temp, 0, f'{max_temp}', color=planet_color, ha='left', va='top')
    ax.text(eq_temp, 0, f'{eq_temp}', color='black', ha='center', va='bottom')  # Scritta nera per il valore della t° di equilibrio

    # Posiziona la legenda all'interno del grafico
    ax.legend(loc='upper right', fontsize='x-small', framealpha=0.7)

    # Imposta i limiti dell'asse x e i tick
    ax.set_xlim(x_range)
    ax.set_xticks(x_ticks)

    # Rimuovi i tick dell'asse y
    ax.set_yticks([])

# Riduzione della larghezza (30% in meno rispetto all'originale)
figsize_reduced = (7, 7)

# Gruppo 1: Giove e Nettuno (range: 0-200 K)
fig, axs = plt.subplots(2, 1, figsize=figsize_reduced)

for i, (planet, eq_temp, min_temp, max_temp) in enumerate(planets_data[3:]):  # Giove e Nettuno
    plot_planet_comparison(planet, eq_temp, min_temp, max_temp, axs[i], x_range=(0, 200), x_ticks=np.arange(0, 201, 50))

plt.tight_layout(h_pad=3)
plt.savefig("jupiter_neptune_temperature_comparison.png", dpi=300, bbox_inches='tight')
plt.close()

# Gruppo 2: Terra e Marte (range: 100-400 K)
fig, axs = plt.subplots(2, 1, figsize=figsize_reduced)

for i, (planet, eq_temp, min_temp, max_temp) in enumerate(planets_data[1:3]):  # Terra e Marte
    plot_planet_comparison(planet, eq_temp, min_temp, max_temp, axs[i], x_range=(100, 400), x_ticks=np.arange(100, 401, 50))

plt.tight_layout(h_pad=3)
plt.savefig("earth_mars_temperature_comparison.png", dpi=300, bbox_inches='tight')
plt.close()

# Gruppo 3: Venere (grafico singolo, range ampio)
fig, ax = plt.subplots(1, 1, figsize=figsize_reduced)

plot_planet_comparison("Venus", 227, 437, 737, ax, x_range=(100, 800), x_ticks=np.arange(100, 801, 50))

plt.tight_layout()
plt.savefig("venus_temperature_comparison.png", dpi=300, bbox_inches='tight')
plt.close()

print("I grafici aggiornati sono stati salvati nelle rispettive immagini PNG.")
