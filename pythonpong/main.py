import numpy as np
import cv2
import time


def czytaj_plik_do_listy(nazwa_pliku):
    dane = []
    with open('wyniki.txt', 'r') as plik:
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


class Paletka:
    def __init__(self, x, y, czy='d', dlugosc=100, szerokosc=5, predkosc=1):
        self.x = x // 2 - dlugosc // 2
        if czy == 'g':
            self.y = 60
        else:
            self.y = y - 70
        self.dlugosc = dlugosc
        self.szerokosc = szerokosc
        self.predkosc = predkosc

    def ruch_w_lewo(self, predkosc):
        self.x = max(0, self.x - predkosc)

    def ruch_w_prawo(self, predkosc, szerokosc_planszy):
        self.x = min(szerokosc_planszy - self.dlugosc, self.x + predkosc)

    def rysuj(self, plansza):
        cv2.rectangle(plansza, (self.x, self.y), (self.x + self.dlugosc, self.y + self.szerokosc), 255, -1)


class Pilka:
    def __init__(self, x, y, predkosc_x, predkosc_y, promien=10):
        self.x = x // 2
        self.y = y // 2
        self.promien = promien
        self.predkosc_x = predkosc_x
        self.predkosc_y = predkosc_y

    def ruch(self):
        self.x += self.predkosc_x
        self.y += self.predkosc_y

    def odbicie_od_scian(self, szerokosc_planszy):
        if self.x - self.promien <= 0 or self.x + self.promien >= szerokosc_planszy:
            self.predkosc_x = -self.predkosc_x

    def reset(self, x, y):
        self.x = x
        self.y = y

    def rysuj(self, plansza):
        cv2.circle(plansza, (self.x, self.y), self.promien, 255, -1)


class Pong:
    def __init__(self, poziom, szerokosc=400, wysokosc=600):
        self.poziom = poziom
        self.szerokosc = szerokosc
        self.wysokosc = wysokosc
        self.pc = 0
        self.gamer = 0
        self.ruch_pilki = False
        self.czas_startu = time.time()
        self.trudnosc = [1 + poziom, 1]

        # obiekty gry
        self.paletka_gorna = Paletka(szerokosc, wysokosc, 'g')
        self.paletka_dolna = Paletka(szerokosc, wysokosc)
        self.pilka = Pilka(szerokosc, wysokosc, poziom + 1, poziom + 2)

    def wyswietl_wynik(self, plansza):
        wynik = str(self.gamer) + ":" + str(self.pc)
        cv2.putText(plansza, wynik, (self.szerokosc // 2 - 25, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2,
                    cv2.LINE_AA)

    def ruch_gornej_paletki(self):
        # Ruch paletki przeciwnika
        if self.pilka.y < self.wysokosc // 2:
            # Obliczanie odległości do piłki
            self.odleglosc_do_pilki = self.pilka.x - (self.paletka_gorna.x + self.paletka_gorna.dlugosc / 2)

            if abs(self.odleglosc_do_pilki) > 20:  # Jeśli piłka jest dalej niż 20 pikseli
                if self.odleglosc_do_pilki < 0:
                    self.paletka_gorna.ruch_w_lewo(self.trudnosc[0])  # Szybszy ruch w lewo
                else:
                    self.paletka_gorna.ruch_w_prawo(self.trudnosc[0], self.szerokosc)  # Szybszy ruch w prawo
            else:  # Wolniejsze ruchy, gdy blisko
                if self.odleglosc_do_pilki < 0:
                    self.paletka_gorna.ruch_w_lewo(self.trudnosc[1])
                else:
                    self.paletka_gorna.ruch_w_prawo(self.trudnosc[1], self.szerokosc)

            # Zapewnienie, że paletka górna nie wyjdzie poza ekran
            self.paletka_gorna.x = max(0, min(self.paletka_gorna.x, self.szerokosc - self.paletka_gorna.dlugosc))

        # ruch paletki przeciwnika gdy pilka na polowie gracza
        elif self.pilka.y >= self.wysokosc // 2:
            self.paletka_gorna.x += self.paletka_gorna.predkosc
            if self.paletka_gorna.x + self.paletka_gorna.dlugosc == self.szerokosc or self.paletka_gorna.x == 0:
                self.paletka_gorna.predkosc = -self.paletka_gorna.predkosc

            self.paletka_gorna.x = max(0, min(self.paletka_gorna.x, self.szerokosc - self.paletka_gorna.dlugosc))

    def punktacja(self):
        if self.pilka.y - self.pilka.promien <= 0:
            self.gamer += 1
            if self.gamer % 5 == 0:
                self.trudnosc[0] += 1
            self.czas_startu = time.time()
            self.pilka.reset(self.szerokosc // 2, 100)
            self.ruch_pilki = False
        if self.pilka.y + self.pilka.promien >= self.wysokosc:
            self.pc += 1
            self.czas_startu = time.time()
            self.pilka.reset(self.szerokosc // 2, self.wysokosc - 100)
            self.ruch_pilki = False

    def kolizje(self):
        # system kolizji gornej paletki
        if (self.pilka.y - self.pilka.promien <= self.paletka_gorna.y + self.paletka_gorna.szerokosc and
                self.paletka_gorna.x <= self.pilka.x <= self.paletka_gorna.x + self.paletka_gorna.dlugosc):
            if self.pilka.y >= self.paletka_gorna.y + self.paletka_gorna.szerokosc:
                self.pilka.predkosc_y = -self.pilka.predkosc_y
                self.pilka.y = self.paletka_gorna.y + self.paletka_gorna.szerokosc + self.pilka.promien

        # system kolizji dolnej paletki
        if (self.pilka.y + self.pilka.promien >= self.paletka_dolna.y and
                self.paletka_dolna.x <= self.pilka.x <= self.paletka_dolna.x + self.paletka_dolna.dlugosc):
            if self.pilka.y <= self.paletka_dolna.y:
                self.pilka.predkosc_y = -self.pilka.predkosc_y
                self.pilka.y = self.paletka_dolna.y - self.pilka.promien

    def gra(self):

        # stworz plansze
        img = np.zeros((self.wysokosc, self.szerokosc), dtype=np.uint8)

        self.wyswietl_wynik(img)
        self.ruch_gornej_paletki()

        self.paletka_gorna.rysuj(img)
        self.paletka_dolna.rysuj(img)

        # reset pozycji pilki i czas oczekiwania na rozpoczecie tury
        if not self.ruch_pilki:
            if time.time() - self.czas_startu >= 2:
                self.ruch_pilki = True

        # ruch pilki
        if self.ruch_pilki:
            self.pilka.ruch()

        # system kolizji ze scianami bocznymi
        self.pilka.odbicie_od_scian(self.szerokosc)

        # system kolizji ze scianami gorna i dolna oraz liczenie punktow
        self.punktacja()
        self.kolizje()

        # rysowanie pilki na ekranie
        self.pilka.rysuj(img)

        # wyswietlenie okna
        cv2.imshow('Pong', img)

        # oczekiwanie na wcisniecie przycisku
        key = cv2.waitKey(1) & 0xFF
        if key == 97:  # A
            self.paletka_dolna.ruch_w_lewo(10)
        if key == 100:  # D
            self.paletka_dolna.ruch_w_prawo(10, self.szerokosc)
        if key == 27:  # Escape
            return False
        return True


class Menu:
    def __init__(self, szerokosc=400, wysokosc=600, tlo='menu.jpg'):
        self.szerokosc = szerokosc
        self.wysokosc = wysokosc
        self.sciezka = tlo
        self.tlo = cv2.imread(self.sciezka)

    def wyswietl(self):
        self.tlo = cv2.resize(self.tlo, (self.szerokosc, self.wysokosc))
        cv2.putText(self.tlo, "PONG", (self.szerokosc // 2 - 80, 60), cv2.FONT_HERSHEY_SIMPLEX,
                    2, (255, 255, 255), 8, cv2.LINE_AA)
        cv2.putText(self.tlo, "Autor: Patryk Jureczko", (self.szerokosc // 2 - 20, self.wysokosc - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(self.tlo, "Ver. 0.3.1", (5, self.wysokosc - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA)

        menu_options = ["START", "SETTING", "EXIT"]
        selected_option = 0
        while True:
            for i, option in enumerate(menu_options):
                color = (255, 255, 255) if i == selected_option else (100, 100, 100)
                cv2.putText(self.tlo, option, (self.szerokosc // 2 - 50, 175 + i * 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            color, 2, cv2.LINE_AA)

            cv2.imshow('Pong', self.tlo)

            key = cv2.waitKey(0) & 0xFF
            if key == 13:  # enter
                print(selected_option)
                return selected_option
            elif key == 27:  # esc
                return 2
            elif key == 119:  # w
                selected_option = (selected_option - 1) % len(menu_options)
            elif key == 115:  # s
                selected_option = (selected_option + 1) % len(menu_options)


class Settings:
    def __init__(self, szerokosc=400, wysokosc=600):
        self.szerokosc = szerokosc
        self.wysokosc = wysokosc

    def wyswietl(self):
        menu_options = ["EASY", "MEDIUM", "HARD"]
        selected_option = 0
        while True:
            img = np.zeros((self.wysokosc, self.szerokosc), dtype=np.uint8)
            for i, option in enumerate(menu_options):
                color = (255, 255, 255) if i == selected_option else (100, 100, 100)
                cv2.putText(img, option, (self.szerokosc // 2 - 50, 150 + i * 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color,
                            2, cv2.LINE_AA)

            cv2.imshow('Pong', img)

            key = cv2.waitKey(0) & 0xFF
            if key == 13:  # enter
                return selected_option
            elif key == 119:  # w
                selected_option = (selected_option - 1) % len(menu_options)
            elif key == 115:  # s
                selected_option = (selected_option + 1) % len(menu_options)


class Wyniki:
    def __init__(self, szerokosc=400, wysokosc=600):
        self.szerokosc = szerokosc
        self.wysokosc = wysokosc

    def wyswietl(self):

        dane = czytaj_plik_do_listy('dane.txt')
        dane_posortowane = posortuj_dane(dane)

        img = np.zeros((self.wysokosc, self.szerokosc), dtype=np.uint8)
        cv2.putText(img, "Top 10", (self.szerokosc // 2 - 50, 35), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255),
                    2, cv2.LINE_AA)

        cv2.putText(img, f"Miejsce", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(img, f"Imie", (self.szerokosc // 2 - 60, 80), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(img, f"Punkty", (self.szerokosc - 115, 80), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (255, 255, 255), 2, cv2.LINE_AA)
        i = 1
        for imie, wynik in dane_posortowane:
            cv2.putText(img, f"{i}", (10, 80 + i * 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                        (255, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(img, f"{imie}", (self.szerokosc // 2 - 60, 80 + i * 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                        (255, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(img, f"{wynik}", (self.szerokosc - 115, 80 + i * 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                        (255, 255, 255), 2, cv2.LINE_AA)
            i += 1
            if i == 11:
                break

        cv2.imshow('Pong', img)

        key = cv2.waitKey(0) & 0xFF
        if key == 27:  # esc
            return False


class NazwaUzytkownika:
    def __init__(self, szerokosc=400, wysokosc=600):
        self.szerokosc = szerokosc
        self.wysokosc = wysokosc
        self.imie = ""

    def wyswietl(self):
        img = np.zeros((self.wysokosc, self.szerokosc), dtype=np.uint8)
        cv2.putText(img, "Podaj swoje imie:", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(img, "Enter - zapisz", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(img, "Esc - wyjdz", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 1, cv2.LINE_AA)

        while True:
            img_copy = img.copy()
            cv2.putText(img_copy, self.imie, (85, 300), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.imshow('Pong', img_copy)

            key = cv2.waitKey(0) & 0xFF
            if key == 13:  # Enter
                return self.imie
            elif key == 8:  # Backspace
                self.imie = self.imie[:-1]
            elif key == 27:  # Escape
                return None
            elif 32 <= key <= 126:  # Printable characters
                if len(self.imie) < 10:
                    self.imie += chr(key)


if __name__ == '__main__':
    menu = Menu()
    poziom = 1

    while True:
        option = menu.wyswietl()
        if option == 2:  # Exit
            break
        elif option == 0:  # Start
            game = Pong(poziom)
            while True:
                if not game.gra():
                    nazwa_uzytkownika = NazwaUzytkownika()
                    imie = nazwa_uzytkownika.wyswietl()
                    if imie is not None:
                        zapisz_wynik_do_pliku(imie, game.gamer - game.pc, "wyniki.txt")
                    break
            wyniki = Wyniki()
            while True:
                if not wyniki.wyswietl():
                    break
        elif option == 1:  # Setting
            difficult = Settings()
            while True:
                poziom = difficult.wyswietl()
                break

    cv2.destroyAllWindows()
