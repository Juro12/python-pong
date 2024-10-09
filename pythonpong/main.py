import numpy as np
import cv2
import time

# wymiary boiska
szerokosc = 400
wysokosc = 600

# wymiary paletki
dlugosc_paletki = 100
szerokosc_paletki = 5
promien_pilki = 10

# punktacja
pc = 0
gamer = 0

# zmienne ruchu pilki
ruch_pilki = False
czas_startu = time.time()

# paletki
pozycja_gornej = [szerokosc // 2 - dlugosc_paletki // 2, 60]
pozycja_dolnej = [szerokosc // 2 - dlugosc_paletki // 2, wysokosc - 70]
predkosc_paletki = 1

# pilka
pozycja_pilki = [szerokosc // 2, wysokosc // 2]
predkosc_pilki = [2, 3]  # Prędkość w osi x i y

trudnosc = [1, 1]

if __name__ == '__main__':
    while True:
        # stworz plansze
        img = np.zeros((wysokosc, szerokosc), dtype=np.uint8)

        # wyswietl wynik
        wynik = str(gamer)+":"+str(pc)
        cv2.putText(img, wynik, (szerokosc // 2 - 20, 30), cv2.FONT_HERSHEY_SIMPLEX,1, (255, 255, 255), 2, cv2.LINE_AA)

        # Ruch paletki przeciwnika
        if pozycja_pilki[1] < wysokosc // 2:
            # Obliczanie odległości do piłki
            odleglosc_do_pilki = pozycja_pilki[0] - (pozycja_gornej[0] + dlugosc_paletki / 2)

            if abs(odleglosc_do_pilki) > 20:  # Jeśli piłka jest dalej niż 20 pikseli
                if odleglosc_do_pilki < 0:
                    pozycja_gornej[0] -= trudnosc[0]  # Szybszy ruch w lewo
                else:
                    pozycja_gornej[0] += trudnosc[0]   # Szybszy ruch w prawo
            else:  # Wolniejsze ruchy, gdy blisko
                if odleglosc_do_pilki < 0:
                    pozycja_gornej[0] -= trudnosc[1]
                else:
                    pozycja_gornej[0] += trudnosc[1]

            # Zapewnienie, że paletka górna nie wyjdzie poza ekran
            pozycja_gornej[0] = max(0, min(pozycja_gornej[0], szerokosc - dlugosc_paletki))

        # ruch paletki przeciwnika gdy pilka na polowie gracza
        elif pozycja_pilki[1] >= wysokosc // 2:
            pozycja_gornej[0] += predkosc_paletki
            if pozycja_gornej[0]+dlugosc_paletki == szerokosc:
                predkosc_paletki = -predkosc_paletki
            elif pozycja_gornej[0] == 0:
                predkosc_paletki = -predkosc_paletki

            # Zapewnienie, że paletka górna nie wyjdzie poza ekran
            pozycja_gornej[0] = max(0, min(pozycja_gornej[0], szerokosc - dlugosc_paletki))

        # rysowanie paletek na ekranie
        cv2.rectangle(img, pozycja_gornej, (pozycja_gornej[0] + dlugosc_paletki, pozycja_gornej[1] + szerokosc_paletki), 255, -1)
        cv2.rectangle(img, pozycja_dolnej, (pozycja_dolnej[0] + dlugosc_paletki, pozycja_dolnej[1] + szerokosc_paletki), 255, -1)

        # reset pozycji pilki i czas oczekiwania na rozpoczecie tury
        if not ruch_pilki:
            #pozycja_pilki = [szerokosc // 2, wysokosc // 2]
            if time.time() - czas_startu >= 2:
                ruch_pilki = True

        # ruch pilki
        if ruch_pilki:
            pozycja_pilki[0] += predkosc_pilki[0]
            pozycja_pilki[1] += predkosc_pilki[1]

        # system kolizji ze scianami bocznymi
        if pozycja_pilki[0] - promien_pilki <= 0 or pozycja_pilki[0] + promien_pilki >= szerokosc:
            predkosc_pilki[0] = -predkosc_pilki[0]
        # system kolizji ze scianami dolna i gorna, liczenie punktow i resetowanie pilki
        if pozycja_pilki[1] - promien_pilki <= 0:
            gamer += 1
            if gamer % 2 == 0:
                trudnosc[0] += 1
            czas_startu = time.time()
            pozycja_pilki = [szerokosc // 2, 100]
            ruch_pilki = False
        if pozycja_pilki[1] + promien_pilki >= wysokosc:
            pc += 1
            czas_startu = time.time()
            pozycja_pilki = [szerokosc // 2, wysokosc - 100]
            ruch_pilki = False

        # system kolizji gornej paletki
        if (pozycja_pilki[1] - promien_pilki <= pozycja_gornej[1] + szerokosc_paletki and
                pozycja_gornej[0] <= pozycja_pilki[0] <= pozycja_gornej[0] + dlugosc_paletki):
            # Sprawdzamy, czy piłka jest już powyżej paletki
            if pozycja_pilki[1] >= pozycja_gornej[1] + szerokosc_paletki:
                predkosc_pilki[1] = -predkosc_pilki[1]
                pozycja_pilki[1] = pozycja_gornej[1] + szerokosc_paletki + promien_pilki

        # system kolizji dolnej paletki
        if (pozycja_pilki[1] + promien_pilki >= pozycja_dolnej[1] and
                pozycja_dolnej[0] <= pozycja_pilki[0] <= pozycja_dolnej[0] + dlugosc_paletki):
            # Sprawdzamy, czy piłka jest już poniżej paletki
            if pozycja_pilki[1] <= pozycja_dolnej[1]:
                predkosc_pilki[1] = -predkosc_pilki[1]
                pozycja_pilki[1] = pozycja_dolnej[1] - promien_pilki

        # rysowanie pilki na ekranie czemu blad chuj wi
        cv2.circle(img, pozycja_pilki, promien_pilki, 255, -1)

        #wyswietlenie okna
        cv2.imshow('Pong', img)

        # oczekiwanie na wcisniecie przycisku
        key = cv2.waitKey(1) & 0xFF
        if key == 97:
            if pozycja_dolnej[0] > 0:
                pozycja_dolnej[0] -= 10
            if pozycja_dolnej[0] < 0:
                pozycja_dolnej[0] = 0
        if key == 100:
            if pozycja_dolnej[0] + dlugosc_paletki < szerokosc:
                pozycja_dolnej[0] += 10
            if pozycja_dolnej[0] + dlugosc_paletki >= szerokosc:
                pozycja_dolnej[0] = szerokosc - dlugosc_paletki
        if key == 27:  # Escape
            break

    cv2.destroyAllWindows()