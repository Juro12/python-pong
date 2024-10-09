import numpy as np
import cv2
import time


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
    def __init__(self, x, y, promien=10, predkosc_x=2, predkosc_y=3):
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
    def __init__(self, szerokosc=400, wysokosc=600):
        self.szerokosc = szerokosc
        self.wysokosc = wysokosc
        self.pc = 0
        self.gamer = 0
        self.ruch_pilki = False
        self.czas_startu = time.time()
        self.trudnosc = [1, 1]

        # obiekty gry
        self.paletka_gorna = Paletka(szerokosc, wysokosc, 'g')
        self.paletka_dolna = Paletka(szerokosc, wysokosc)
        self.pilka = Pilka(szerokosc, wysokosc)

    def wyswietl_wynik(self, plansza):
        wynik = str(self.gamer) + ":" + str(self.pc)
        cv2.putText(plansza, wynik, (self.szerokosc // 2 - 20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2,
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
        cv2.putText(self.tlo, "PONG", (self.szerokosc // 2 - 80, 90), cv2.FONT_HERSHEY_SIMPLEX,
                    2, (255, 255, 255), 8, cv2.LINE_AA)
        cv2.putText(self.tlo, "Wcisnij Enter aby zagrac", (self.szerokosc // 2 - 155, self.wysokosc - 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(self.tlo, "Autor: Patryk Jureczko", (self.szerokosc // 2 - 20, self.wysokosc - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(self.tlo, "Ver. 0.3.1", (5, self.wysokosc - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA)

        cv2.imshow('Pong', self.tlo)

        while True:
            key = cv2.waitKey(0) & 0xFF
            if key == 13:  # Enter
                return True
            elif key == 27:  # Escape
                return False
            else:
                continue


if __name__ == '__main__':
    menu = Menu()

    while True:
        if not menu.wyswietl():
            break
        else:
            game = Pong()
            while True:
                if not game.gra():
                    break
            break

    cv2.destroyAllWindows()
