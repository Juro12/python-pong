def czytaj_plik_do_listy(nazwa_pliku):
    dane = []
    with open(nazwa_pliku, 'r') as plik:
        linie = plik.readlines()  # Odczytuje wszystkie linie

        # Przetwarzanie linii, zakładając, że są pary: imię, wynik
        for i in range(0, len(linie), 2):
            imie = linie[i].strip()  # Usunięcie zbędnych białych znaków (np. nowych linii)
            wynik = int(linie[i + 1].strip())  # Zamiana wyniku na liczbę całkowitą

            # Dodanie pary (imię, wynik) do listy
            dane.append((imie, wynik))

    return dane


def posortuj_dane(dane):
    return sorted(dane, key=lambda x: x[1], reverse=True)


def zapisz_wynik_do_pliku(imie, wynik, nazwa_pliku):
    with open(nazwa_pliku, 'a') as plik:
        plik.write(f"{imie}\n{wynik}\n")  # Zapisz imię i wynik
