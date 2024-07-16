import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def load_atmospheric_data(filename):
    """Carica i dati atmosferici da un file CSV."""
    df = pd.read_csv(filename)
    print("Colonne in atmospheric_data:")
    print(df.columns)
    return df

def load_extremophile_data(filename):
    """Carica i dati dei microrganismi estremofili da un file CSV."""
    df = pd.read_csv(filename)
    print("Colonne in extremophile_data:")
    print(df.columns)
    return df

def analyze_habitability(atmosphere, extremophiles):
    """Analizza l'abitabilità per ciascun microrganismo in ciascuna atmosfera."""
    results = []
    for _, atmo in atmosphere.iterrows():
        for _, microbe in extremophiles.iterrows():
            try:
                habitable = (
                    (microbe['Pressione_min(atm)'] <= atmo['Pressione(atm)'] <= microbe['Pressione_max(atm)']) and
                    (microbe['Temperatura_min(°C)'] <= atmo['Temperatura(°C)'] <= microbe['Temperatura_max(°C)']) and
                    (microbe['Umidita_min(%)'] <= atmo['Umidita(%)'] <= microbe['Umidita_max(%)']) and
                    (microbe['pH_min'] <= atmo['pH'] <= microbe['pH_max']) and
                    (atmo['Radiazioni_X(mSv/anno)'] <= microbe['Radiazioni_X_max(mSv/anno)']) and
                    (atmo['Radiazioni_UV(W/m2)'] <= microbe['Radiazioni_UV_max(W/m2)'])
                )
            except KeyError as e:
                print(f"Errore: Colonna mancante - {e}")
                print("Colonne in microbe:")
                print(microbe.index)
                print("Colonne in atmo:")
                print(atmo.index)
                return pd.DataFrame()
            
            results.append({
                'Corpo_celeste': atmo['Nome'],
                'Altitudine': atmo['Altitudine(km)'],
                'Microrganismo': microbe['Nome'],
                'Abitabile': habitable
            })
    return pd.DataFrame(results)

def plot_habitability(atmosphere, extremophiles, results):
    """Crea un grafico di abitabilità."""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    for name, group in atmosphere.groupby('Nome'):
        ax.scatter(group['Pressione(atm)'], group['Temperatura(°C)'], label=name)
    
    for _, microbe in extremophiles.iterrows():
        rect = plt.Rectangle((microbe['Pressione_min(atm)'], microbe['Temperatura_min(°C)']),
                             microbe['Pressione_max(atm)'] - microbe['Pressione_min(atm)'],
                             microbe['Temperatura_max(°C)'] - microbe['Temperatura_min(°C)'],
                             fill=False, edgecolor='red', alpha=0.5)
        ax.add_patch(rect)
        ax.annotate(microbe['Nome'], 
                    ((microbe['Pressione_min(atm)'] + microbe['Pressione_max(atm)'])/2,
                     (microbe['Temperatura_min(°C)'] + microbe['Temperatura_max(°C)'])/2),
                    fontsize=8)
    
    ax.set_xscale('log')
    ax.set_xlabel('Pressione (atm)')
    ax.set_ylabel('Temperatura (°C)')
    ax.set_title('Abitabilità atmosferica per microrganismi estremofili')
    ax.legend()
    ax.grid(True)
    plt.tight_layout()
    plt.savefig('ExoBIOMA_graph.png')
    plt.show()

def main():
    atmosphere = load_atmospheric_data('atmospheric_profiles.csv')
    extremophiles = load_extremophile_data('aerial_extremophiles.csv')
    
    print("Prime righe di atmosphere:")
    print(atmosphere.head())
    print("\nPrime righe di extremophiles:")
    print(extremophiles.head())
    
    results = analyze_habitability(atmosphere, extremophiles)
    
    if not results.empty:
        plot_habitability(atmosphere, extremophiles, results)
        
        for _, row in results.iterrows():
            if row['Abitabile']:
                print(f"{row['Microrganismo']} potrebbe sopravvivere nell'atmosfera di {row['Corpo_celeste']} a un'altitudine di {row['Altitudine']} km")

        results.to_csv('exobioma_results.csv', index=False)
    else:
        print("Non è stato possibile generare risultati a causa di errori nei dati.")

if __name__ == "__main__":
    main()