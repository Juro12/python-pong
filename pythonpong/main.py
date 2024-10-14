import pygame
import numpy as np
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
        pygame.draw.rect(plansza, (255, 255, 255), (self.x, self.y, self.dlugosc, self.szerokosc))


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
        self.pilka = Pilka(szerokosc, wysokosc)

    def wyswietl_wynik(self, plansza):
        wynik = str(self.gamer) + ":" + str(self.pc)
        font = pygame.font.Font(None, 48)
        text = font.render(wynik, True, (255, 255, 255))
        plansza.blit(text, (self.szerokosc // 2 - 25, 15))

    def ruch_gornej_paletki(self):
        # Ruch paletki przeciwnika
        if self.pilka.y < self.wysokosc // 2:
            # Obliczanie odległości do piłki
            self.odleglosc_do_pilki = self.pilka.x - (self.paletka_gorna.x + self.paletka_gorna.dlugosc / 2)

            if abs(self.odleglosc_do_pilki) > 30:  # Jeśli piłka jest dalej niż 20 pikseli
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
        img = np.zeros((self.wysokosc, self.szerokosc, 3), dtype=np.uint8)  # Biała plansza
        plansza = pygame.display.set_mode((self.szerokosc, self.wysokosc))
        pygame.display.set_caption("Pong")
        clock = pygame.time.Clock()

        while True:
            # obsługa zdarzeń
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            keys = pygame.key.get_pressed()
            if keys[pygame.K_a]:
                self.paletka_dolna.ruch_w_lewo(4)
            if keys[pygame.K_d]:
                self.paletka_dolna.ruch_w_prawo(4, self.szerokosc)
            if keys[pygame.K_ESCAPE]:
                break

            if not self.ruch_pilki and time.time() - self.czas_startu > 1:
                self.ruch_pilki = True  # Rozpoczęcie ruchu piłki po 1 sekundzie

            if self.ruch_pilki:
                self.pilka.ruch()

            self.pilka.odbicie_od_scian(self.szerokosc)

            self.punktacja()
            self.kolizje()
            self.ruch_gornej_paletki()

            # Rysowanie na planszy
            plansza.fill((0, 0, 0))  # Czarny kolor tła
            self.paletka_dolna.rysuj(plansza)
            self.paletka_gorna.rysuj(plansza)
            self.pilka.rysuj(plansza)
            self.wyswietl_wynik(plansza)

            # Odświeżanie planszy
            pygame.display.flip()
            clock.tick(60)  # 60 klatek na sekundę


def main():
    pygame.init()

    poziom = 0

    # Rozpoczęcie gry
    gra = Pong(poziom)
    gra.gra()

    pygame.quit()


if __name__ == "__main__":
    main()
