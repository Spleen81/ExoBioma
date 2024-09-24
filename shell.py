# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.colors import TwoSlopeNorm

def pressure_gradient_rocky(h, H, P_surface):
    """Pressure model for rocky planet atmospheres"""
    return P_surface * np.exp(-h / H)

def pressure_gradient_gas(r, R, P_center, P_surface):
    """Pressure model for gas giants"""
    return P_center * (1 - (r/R)**2) + P_surface * (r/R)**2

def pa_to_atm(pa):
    """Convert Pascal to atmospheres"""
    return pa / 101325

def create_custom_colormap(colors):
    """Create a custom colormap from a list of colors"""
    n_bins = 10000
    return LinearSegmentedColormap.from_list('custom', colors, N=n_bins)

def calculate_shell_volume(inner_radius, outer_radius):
    """Calculate the volume of a spherical shell in km^3"""
    volume = (4/3) * np.pi * (outer_radius**3 - inner_radius**3)
    return volume / 1e9  # Convert to km^3

def add_distance_scale(ax, R):
    """Add a distance scale to the plot that updates with zoom"""
    scale_line, = ax.plot([], [], 'k-', linewidth=2)
    scale_text = ax.text(0, 0, '', ha='center', va='top')
    
    def update_scale(event=None):
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        
        scale_length = (xlim[1] - xlim[0]) / 5
        scale_length = 10**np.floor(np.log10(scale_length))
        
        scale_x = xlim[1] - (xlim[1] - xlim[0]) * 0.25  # Inizia al 75% della larghezza
        scale_y = ylim[0] + (ylim[1] - ylim[0]) * 0.05  # 5% dall'altezza in basso
        
        scale_line.set_data([scale_x, scale_x + scale_length], [scale_y, scale_y])
        scale_text.set_position((scale_x + scale_length, scale_y - 0.01 * (ylim[1] - ylim[0])))  # Sposta il testo in basso di 1%
        scale_text.set_ha('right')  # Allinea il testo a destra
        scale_text.set_text(f'{scale_length/1000:.0f} km')
        
        ax.figure.canvas.draw_idle()
    
    ax.callbacks.connect('xlim_changed', update_scale)
    ax.callbacks.connect('ylim_changed', update_scale)
    
    update_scale()
    return update_scale  # Return the function for later use

def create_shell_visualization(ax, R, P_surface, name, is_rocky=True, H=None, P_center=None, cmap=None):
    if is_rocky:
        h = np.linspace(0, R*0.2, 1000)  # Atmosfera fino al 20% del raggio
        P = pressure_gradient_rocky(h, H, P_surface)
        r = R + h
    else:
        r = np.linspace(0, 1.2*R, 10000)
        P = pressure_gradient_gas(r, R, P_center, P_surface)
    
    # Gamma di pressione compatibile con la vita
    P_min, P_max = 1e-5, 1e8  # Pa, aumentato di 2 ordini di grandezza
    
    # Convertire pressione in atm e usare clip per evitare errori nel log10
    P_atm = pa_to_atm(P)
    P_atm = np.clip(P_atm, 1e-10, None)  # Evita valori <= 0 prima del log10
    
    # Calcolare log10 di min e max pressioni
    vmin, vmax = np.log10(P_atm.min()), np.log10(P_atm.max())
    vcenter = np.log10(1)  # Centro colormap a 1 atm (log10(1) = 0)

    # Controlla che vmin < vcenter < vmax, altrimenti fallback a Normalize
    if vmin < vcenter < vmax:
        norm = TwoSlopeNorm(vmin=vmin, vcenter=vcenter, vmax=vmax)
    else:
        norm = plt.Normalize(vmin=vmin, vmax=vmax)
    
    # Disegnare pianeta e atmosfera
    if is_rocky:
        planet = Circle((0, 0), R, fill=True, color='saddlebrown')
        ax.add_artist(planet)
        for i in range(len(h)-1):
            if P[i] > P_min:
                circle = Circle((0, 0), r[i], fill=False, color=cmap(norm(np.log10(P_atm[i]))), linewidth=2)
                ax.add_artist(circle)
        # Limiti di pressione compatibili con la vita
        shell_lower = R + np.interp(P_max, P[::-1], h[::-1])
        ax.add_artist(Circle((0, 0), shell_lower, fill=False, color='limegreen', linestyle='--'))
        ax.add_artist(Circle((0, 0), r[-1], fill=False, color='limegreen', linestyle='--'))
        shell_thickness = r[-1] - shell_lower
        # Calcolare il volume della shell
        shell_volume = calculate_shell_volume(shell_lower, r[-1])
    else:
        for i in range(len(r)-1):
            if P[i] > 0:
                circle = Circle((0, 0), r[i], fill=False, color=cmap(norm(np.log10(P_atm[i]))), linewidth=2)
                ax.add_artist(circle)
        # Limiti del guscio compatibile con la vita
        shell_inner = R + np.interp(P_max, P[::-1], r[::-1] - R)
        shell_outer = R + np.interp(P_min, P[::-1], r[::-1] - R)
        ax.add_artist(Circle((0, 0), shell_inner, fill=False, color='limegreen', linestyle='--', linewidth=2))
        ax.add_artist(Circle((0, 0), shell_outer, fill=False, color='limegreen', linestyle='--', linewidth=2))
        shell_thickness = shell_outer - shell_inner
        # Calcolare il volume della shell
        shell_volume = calculate_shell_volume(shell_inner, shell_outer)
    
    ax.set_xlim(-1.2*R, 1.2*R)
    ax.set_ylim(-1.2*R, 1.2*R)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(name)
    
    # Annotazione per lo spessore e il volume del guscio
    ax.annotate(f'Shell thickness: {shell_thickness/1000:.2f} km\nShell volume: {shell_volume:.2e} km³',
                xy=(0.05, 0.05), xycoords='axes fraction',
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))
    
    # Annotazione per la lunghezza del raggio
    ax.annotate(f'Radius: {R/1000:.0f} km',
                xy=(0.95, 0.95), xycoords='axes fraction',
                ha='right', va='top',
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))
    
    # Aggiungi la scala di distanza
    add_distance_scale(ax, R)


# Funzione per visualizzare un singolo pianeta con la colorbar
def plot_single_planet(planet, name, is_rocky=True, custom_cmap=None):
    fig, ax = plt.subplots(figsize=(8, 8))
    cmap = custom_cmap if custom_cmap else create_custom_colormap(['blue', 'green', 'red'])
    create_shell_visualization(ax, **planet, name=name, is_rocky=is_rocky, cmap=cmap)
    
    # Aggiungere la colorbar
    cbar_ax = fig.add_axes([0.9, 0.15, 0.03, 0.7])
    vmin, vmax = np.log10(pa_to_atm(1e-6)), np.log10(pa_to_atm(planet['P_surface']))
    
    if vmin < np.log10(1) < vmax:
        norm = TwoSlopeNorm(vmin=vmin, vcenter=np.log10(1), vmax=vmax)
    else:
        norm = plt.Normalize(vmin=vmin, vmax=vmax)
    
    cbar = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=cbar_ax)
    cbar.set_label('Log Pressure (atm)', rotation=270, labelpad=15)
    
    # Connect the update_scale function to the draw event
    update_scale = add_distance_scale(ax, planet['R'])
    fig.canvas.mpl_connect('draw_event', update_scale)
    
    plt.show()

# Parametri pianeti
Venus = {'R': 6052e3, 'P_surface': 9.2e6, 'H': 15900}
Earth = {'R': 6371e3, 'P_surface': 1.01325e5, 'H': 8500}
Jupiter = {'R': 71492e3, 'P_surface': 1e5, 'P_center': 2e11}
Saturn = {'R': 60268e3, 'P_surface': 1e5, 'P_center': 2e10}

# Visualizzare ogni pianeta separatamente
plot_single_planet(Venus, "Venus", is_rocky=True)
# Per la Terra, usa una colormap invertita (blu-verde)
earth_cmap = create_custom_colormap(['blue', 'green'])
plot_single_planet(Earth, "Earth", is_rocky=True, custom_cmap=earth_cmap)
plot_single_planet(Jupiter, "Jupiter", is_rocky=False)
plot_single_planet(Saturn, "Saturn", is_rocky=False)
