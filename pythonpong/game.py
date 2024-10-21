import time
from elements import *


class Pong:
    def __init__(self, poziom, szerokosc=400, wysokosc=600):
        self.poziom = poziom
        self.szerokosc = szerokosc
        self.wysokosc = wysokosc
        self.pc = 0
        self.gamer = 0
        self.ruch_pilki = False
        self.czas_startu = time.time()
        self.ostatni_czas_repair = time.time()
        self.trudnosc = [1 + poziom, 1]
        self.odleglosc_do_pilki = 0

        # obiekty gry
        self.paletka_gorna = Paletka(szerokosc, wysokosc, random.randint(0, 4), 'g')
        self.paletka_dolna = Paletka(szerokosc, wysokosc, random.randint(0, 4))
        self.pilka = Pilka(szerokosc, wysokosc)

        self.przeszkoda1 = Przeszkoda(szerokosc, wysokosc, random.randint(0, 4), 'gp', poziom)
        self.przeszkoda2 = Przeszkoda(szerokosc, wysokosc, random.randint(0, 4), 'dp', poziom)
        self.naprawa1 = Naprawa(self.szerokosc, self.wysokosc)
        self.naprawa2 = Naprawa(self.szerokosc, self.wysokosc, predkosc=-2)

    def wyswietl_wynik(self, plansza):
        wynik = str(self.gamer) + ":" + str(self.pc)
        font = pygame.font.Font(None, 48)
        text = font.render(wynik, True, (255, 255, 255))
        plansza.blit(text, (self.szerokosc // 2 - 25, 15))

    def ruch_gornej_paletki(self):
        # Ruch paletki przeciwnika
        if self.paletka_gorna.dlugosc < 80 and self.szerokosc // 2 - 30 > self.naprawa2.y > 0:
            # Obliczanie odległości do złotej piłki
            odleglosc_do_zlotej_pilki = self.naprawa2.x - (
                    self.paletka_gorna.x + self.paletka_gorna.dlugosc / 2)

            if abs(odleglosc_do_zlotej_pilki) > 30:  # Jeśli złota piłka jest dalej niż 30 pikseli
                if odleglosc_do_zlotej_pilki < 0:
                    self.paletka_gorna.ruch_w_lewo(self.trudnosc[0])  # Szybszy ruch w lewo
                else:
                    self.paletka_gorna.ruch_w_prawo(self.trudnosc[0], self.szerokosc)  # Szybszy ruch w prawo
            else:  # Wolniejsze ruchy, gdy blisko
                if odleglosc_do_zlotej_pilki < 0:
                    self.paletka_gorna.ruch_w_lewo(self.trudnosc[1])
                else:
                    self.paletka_gorna.ruch_w_prawo(self.trudnosc[1], self.szerokosc)

            self.paletka_gorna.x = max(0, min(self.paletka_gorna.x, self.szerokosc - self.paletka_gorna.dlugosc))

        elif self.pilka.y < self.wysokosc // 2:
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

    def ruch_przeszkody(self):
        self.przeszkoda1.x += self.przeszkoda1.predkosc
        if self.przeszkoda1.x + self.przeszkoda1.dlugosc == self.szerokosc or self.przeszkoda1.x == 0:
            self.przeszkoda1.predkosc = -self.przeszkoda1.predkosc

        self.przeszkoda2.x += self.przeszkoda2.predkosc
        if self.przeszkoda2.x + self.przeszkoda2.dlugosc == self.szerokosc or self.przeszkoda2.x == 0:
            self.przeszkoda2.predkosc = -self.przeszkoda2.predkosc

    def punktacja(self):
        if self.pilka.y - self.pilka.promien <= 0:
            self.gamer += 1
            self.czas_startu = time.time()
            self.pilka.reset(self.szerokosc // 2, 100)
            self.ruch_pilki = False
            self.pilka.predkosc_y = -4
            self.pilka.predkosc_x = -3
        if self.pilka.y + self.pilka.promien >= self.wysokosc:
            self.pc += 1
            self.czas_startu = time.time()
            self.pilka.reset(self.szerokosc // 2, self.wysokosc - 100)
            self.ruch_pilki = False
            self.pilka.predkosc_y = 4
            self.pilka.predkosc_x = 3

    def repair(self, plansza):
        self.naprawa1.rysuj(plansza)
        self.naprawa2.rysuj(plansza)
        self.naprawa1.ruch()
        self.naprawa2.ruch()
        if (self.naprawa2.y - self.naprawa2.promien <= self.paletka_gorna.y + self.paletka_gorna.szerokosc and
                self.paletka_gorna.x <= self.naprawa2.x <= self.paletka_gorna.x + self.paletka_gorna.dlugosc):
            if self.naprawa2.y >= self.paletka_gorna.y + self.paletka_gorna.szerokosc:
                self.paletka_gorna.dlugosc = 100
                self.naprawa2.checked()

        if (self.naprawa1.y + self.naprawa1.promien >= self.paletka_dolna.y and
                self.paletka_dolna.x <= self.naprawa1.x <= self.paletka_dolna.x + self.paletka_dolna.dlugosc):
            if self.naprawa1.y <= self.paletka_dolna.y:
                self.paletka_dolna.dlugosc = 100
                self.naprawa1.checked()

    def gra(self):
        # stworz plansze
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

            if self.paletka_gorna.dlugosc <= 0:
                return 1
            if self.paletka_dolna.dlugosc <= 0:
                return 2

            if not self.ruch_pilki and time.time() - self.czas_startu > 1:
                self.ruch_pilki = True  # Rozpoczęcie ruchu piłki po 1 sekundzie

            if self.ruch_pilki:
                self.pilka.ruch()

            self.pilka.odbicie_od_scian(self.szerokosc)

            self.punktacja()
            self.przeszkoda1.kolizje(self.pilka)
            self.przeszkoda2.kolizje(self.pilka)
            self.paletka_gorna.kolizje(self.pilka)
            self.paletka_dolna.kolizje(self.pilka)
            self.ruch_gornej_paletki()
            self.ruch_przeszkody()

            # Rysowanie na planszy
            plansza.fill((0, 0, 0))  # Czarny kolor tła
            self.paletka_dolna.rysuj(plansza)
            self.paletka_gorna.rysuj(plansza)
            self.przeszkoda1.rysuj(plansza)
            self.przeszkoda2.rysuj(plansza)
            self.pilka.rysuj(plansza)
            self.wyswietl_wynik(plansza)
            self.repair(plansza)

            if time.time() - self.ostatni_czas_repair >= 15:
                self.naprawa1.clear()
                self.naprawa2.clear()
                self.ostatni_czas_repair = time.time()

            # Odświeżanie planszy
            pygame.display.flip()
            clock.tick(60)  # 60 klatek na sekundę
