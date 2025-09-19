def tausch2(zahlenliste: list) -> None:
    if not zahlenliste:
        raise ValueError("Die Liste darf nicht leer sein")
    
    mitte_index = len(zahlenliste) // 2  # Abrunden durch ganzzahlige Division
    
    # Tausche das erste Element mit dem mittleren Element
    zahlenliste[0], zahlenliste[mitte_index] = zahlenliste[mitte_index], zahlenliste[0]

# Beispielaufruf:
zahlen = [1, 2, 3, 4, 5]
tausch2(zahlen)
print(zahlen)  # Erwartete Ausgabe: [3, 2, 1, 4, 5]