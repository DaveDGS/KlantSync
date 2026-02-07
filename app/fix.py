import os

map_naam = 'templates'

# Loop door alle bestanden in de templates map
for bestandsnaam in os.listdir(map_naam):
    # Controleer of het bestand eindigt op .txt
    if bestandsnaam.endswith('.txt'):
        # Maak de nieuwe naam (zonder de .txt aan het einde)
        nieuwe_naam = bestandsnaam[:-4]
        
        # Hernoem het bestand
        os.rename(os.path.join(map_naam, bestandsnaam), os.path.join(map_naam, nieuwe_naam))
        print(f'Gerepareerd: {bestandsnaam} ---> {nieuwe_naam}')

print('Klaar! Probeer je app nu opnieuw.')