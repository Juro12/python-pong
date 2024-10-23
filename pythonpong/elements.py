import pygame
import random


class Cechy:
    def __init__(self, flaga):
        match flaga:
            # zwykla
            case 0:
                self.kolor = (255, 255, 255)
                self.predkosc = (3, 4)

            # gabka pochlania energie
            case 1:
                self.kolor = (0, 128, 0)
                self.predkosc = (1, 2)

            # kauczuk odbija sie szybciej
            case 2:
                self.kolor = (0, 0, 255)
                self.predkosc = (4, 5)

            # elektrycznosc odbija sie bardziej na ukos
            case 3:
                self.kolor = (255, 255, 0)
                self.predkosc = (6, 3)

            # beton odbija sie bardziej prosto
            case 4:
                self.kolor = (125, 125, 125)
                self.predkosc = (2, 5)


class Paletka:
    def __init__(self, x, y, flaga=0, czy='d', predkosc=1, dlugosc=100, szerokosc=5, erozja_szybkosc=5):
        self.pilka = None
        self.x = x // 2 - dlugosc // 2
        self.czy = czy
        if self.czy == 'g':
            self.y = 60
        else:
            self.y = y - 70
        self.dlugosc = dlugosc
        self.szerokosc = szerokosc
        self.predkosc = predkosc
        self.erozja_szybkosc = erozja_szybkosc  # Jak szybko paletka będzie się zużywać
        self.flaga = flaga

        self.cechy = Cechy(flaga)

    def ruch_w_lewo(self, predkosc):
        self.x = max(0, self.x - predkosc)
        if self.x <= 0:
            self.x = 1

    def ruch_w_prawo(self, predkosc, szerokosc_planszy):
        self.x = min(szerokosc_planszy - self.dlugosc, self.x + predkosc)

    def rysuj(self, plansza):
        pygame.draw.rect(plansza, self.cechy.kolor, (self.x, self.y, self.dlugosc, self.szerokosc))

    def kolizje(self, pilka_klasa):
        self.pilka = pilka_klasa
        if (self.pilka.y + self.pilka.promien >= self.y and
                self.pilka.y - self.pilka.promien <= self.y + self.szerokosc and
                self.pilka.x + self.pilka.promien >= self.x and
                self.pilka.x - self.pilka.promien <= self.x + self.dlugosc):

            if self.pilka.predkosc_y < 0:
                self.pilka.predkosc_y = -self.cechy.predkosc[1]
            else:
                self.pilka.predkosc_y = self.cechy.predkosc[1]

            if self.pilka.predkosc_x < 0:
                self.pilka.predkosc_x = -self.cechy.predkosc[0]
            else:
                self.pilka.predkosc_x = self.cechy.predkosc[0]

            # Kolizja z górą przeszkody
            if self.pilka.y <= self.y:
                self.pilka.predkosc_y = -self.pilka.predkosc_y
                self.pilka.y = self.y - self.pilka.promien
                self.zniszcz_palete(self.pilka.x)

            # Kolizja z dołem przeszkody
            elif self.pilka.y >= self.y + self.szerokosc:
                self.pilka.predkosc_y = -self.pilka.predkosc_y
                self.pilka.y = self.y + self.szerokosc + self.pilka.promien
                self.zniszcz_palete(self.pilka.x)

            # Kolizja z lewą stroną przeszkody
            if self.pilka.x <= self.x:
                self.pilka.predkosc_x = -self.pilka.predkosc_x
                self.pilka.x = self.x - self.pilka.promien
                self.zniszcz_palete(self.pilka.x)

            # Kolizja z prawą stroną przeszkody
            elif self.pilka.x >= self.x + self.dlugosc:
                self.pilka.predkosc_x = -self.pilka.predkosc_x
                self.pilka.x = self.x + self.dlugosc + self.pilka.promien
                self.zniszcz_palete(self.pilka.x)

    def zniszcz_palete(self, punkt_uderzenia):
        if self.czy != 'dp' and self.czy != 'gp':
            # Obliczenie, w którym miejscu paletka została uderzona
            lokalizacja_na_palecie = punkt_uderzenia - self.x

            # Dzielimy paletkę na dwie części: lewą i prawą, od miejsca uderzeniaa
            if lokalizacja_na_palecie < self.dlugosc // 2:
                # Zmniejszamy lewą część paletki
                self.dlugosc -= self.erozja_szybkosc
                self.x += self.erozja_szybkosc  # Przesuwamy paletkę, aby skracała się od lewej
            else:
                # Zmniejszamy prawą część paletki
                self.dlugosc -= self.erozja_szybkosc


class Przeszkoda(Paletka):
    def __init__(self, x, y, flaga=0, czy="dp", predkosc=1, dlugosc=20, szerokosc=20):
        super().__init__(x, y, flaga=flaga, czy=czy, dlugosc=dlugosc, szerokosc=szerokosc, predkosc=predkosc)

        if czy == 'dp':
            self.x = x - 22
            self.y = y // 2 - 50
        elif czy == 'gp':
            self.x = 2
            self.y = y // 2 + 30
            self.predkosc = -self.predkosc

        if predkosc == 0:
            self.x = -50
            self.y = -50


class Pilka:
    def __init__(self, x, y, predkosc_x=3, predkosc_y=4, promien=10):
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
        pygame.draw.circle(plansza, (255, 255, 255), (self.x, self.y), self.promien)


class Naprawa:
    def __init__(self, x, y, predkosc=2, promien=12):
        self.szerokosc = x
        self.wysokosc = y
        self.x = x * 2
        self.y = y * 2
        self.promien = promien
        self.predkosc = predkosc

    def ruch(self):
        self.y += self.predkosc

    def rysuj(self, plansza):
        pygame.draw.circle(plansza, (255, 255, 0), (self.x, self.y), self.promien)

    def checked(self):
        self.x = self.wysokosc * 2
        self.y = self.wysokosc * 2

    def clear(self):
        self.x = random.randint(self.promien, self.szerokosc - self.promien)
        self.y = self.wysokosc // 2
