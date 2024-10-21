import sys
import pygame
import time
import random


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


class Paletka:
    def __init__(self, x, y, czy='d', predkosc=1, dlugosc=100, szerokosc=5, erozja_szybkosc=5):
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

    def ruch_w_lewo(self, predkosc):
        self.x = max(0, self.x - predkosc)
        if self.x <= 0:
            self.x = 1

    def ruch_w_prawo(self, predkosc, szerokosc_planszy):
        self.x = min(szerokosc_planszy - self.dlugosc, self.x + predkosc)

    def rysuj(self, plansza):
        pygame.draw.rect(plansza, (255, 255, 255), (self.x, self.y, self.dlugosc, self.szerokosc))

    def kolizje(self, pilka_klasa):
        self.pilka = pilka_klasa
        if (self.pilka.y + self.pilka.promien >= self.y and
                self.pilka.y - self.pilka.promien <= self.y + self.szerokosc and
                self.pilka.x + self.pilka.promien >= self.x and
                self.pilka.x - self.pilka.promien <= self.x + self.dlugosc):

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

            # Dzielimy paletkę na dwie części: lewą i prawą, od miejsca uderzenia
            if lokalizacja_na_palecie < self.dlugosc // 2:
                # Zmniejszamy lewą część paletki
                self.dlugosc -= self.erozja_szybkosc
                self.x += self.erozja_szybkosc  # Przesuwamy paletkę, aby skracała się od lewej
            else:
                # Zmniejszamy prawą część paletki
                self.dlugosc -= self.erozja_szybkosc


class Przeszkoda(Paletka):
    def __init__(self, x, y, czy, predkosc=1, dlugosc=20, szerokosc=20):
        super().__init__(x, y, czy=czy, dlugosc=dlugosc, szerokosc=szerokosc, predkosc=predkosc)

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
        self.paletka_gorna = Paletka(szerokosc, wysokosc, 'g')
        self.paletka_dolna = Paletka(szerokosc, wysokosc)
        self.pilka = Pilka(szerokosc, wysokosc)

        self.przeszkoda1 = Przeszkoda(szerokosc, wysokosc, 'gp', poziom)
        self.przeszkoda2 = Przeszkoda(szerokosc, wysokosc, 'dp', poziom)
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
        if self.pilka.y + self.pilka.promien >= self.wysokosc:
            self.pc += 1
            self.czas_startu = time.time()
            self.pilka.reset(self.szerokosc // 2, self.wysokosc - 100)
            self.ruch_pilki = False

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


class Menu:
    def __init__(self, szerokosc=400, wysokosc=600, tlo='menu.jpg'):
        self.szerokosc = szerokosc
        self.wysokosc = wysokosc
        self.sciezka = tlo

        # Inicjalizacja Pygame
        pygame.init()

        # Ustawienie ekranu
        self.screen = pygame.display.set_mode((self.szerokosc, self.wysokosc))
        pygame.display.set_caption('Pong')

        # Wczytanie tła
        self.tlo = pygame.image.load(self.sciezka)
        self.tlo = pygame.transform.scale(self.tlo, (self.szerokosc, self.wysokosc))

        # Ustawienia czcionek
        self.font = pygame.font.Font(None, 36)
        self.title_font = pygame.font.Font(None, 72)
        self.ver_font = pygame.font.Font(None, 24)

    def wyswietl(self):
        menu_options = ["START", "SETTING", "EXIT"]
        selected_option = 0

        while True:
            self.screen.blit(self.tlo, (0, 0))

            # Rysowanie tytułu
            title_surface = self.title_font.render("PONG", True, (255, 255, 255))
            self.screen.blit(title_surface, (self.szerokosc // 2 - title_surface.get_width() // 2, 20))

            # Rysowanie autora
            author_surface = self.ver_font.render("Autor: Patryk Jureczko", True, (255, 255, 255))
            self.screen.blit(author_surface,
                             (self.szerokosc // 2 + 15, self.wysokosc - 20))

            # Rysowanie wersji
            version_surface = self.ver_font.render("Ver. 0.4.4", True, (255, 255, 255))
            self.screen.blit(version_surface, (5, self.wysokosc - 20))

            # Rysowanie opcji menu
            for i, option in enumerate(menu_options):
                color = (255, 255, 255) if i == selected_option else (100, 100, 100)
                option_surface = self.font.render(option, True, color)
                self.screen.blit(option_surface, (self.szerokosc // 2 - option_surface.get_width() // 2, 160 + i * 50))

            # Aktualizacja ekranu
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:  # enter
                        return selected_option
                    elif event.key == pygame.K_ESCAPE:  # esc
                        return 2
                    elif event.key == pygame.K_w:  # w
                        selected_option = (selected_option - 1) % len(menu_options)
                    elif event.key == pygame.K_s:  # s
                        selected_option = (selected_option + 1) % len(menu_options)


class Settings:
    def __init__(self, szerokosc=400, wysokosc=600):
        self.szerokosc = szerokosc
        self.wysokosc = wysokosc

        # Inicjalizacja Pygame
        pygame.init()

        # Ustawienie ekranu
        self.screen = pygame.display.set_mode((self.szerokosc, self.wysokosc))
        pygame.display.set_caption('Pong - Settings')

        # Ustawienia czcionek
        self.font = pygame.font.Font(None, 48)

    def wyswietl(self):
        menu_options = ["EASY", "MEDIUM", "HARD"]
        selected_option = 0

        while True:
            self.screen.fill((0, 0, 0))  # Wypełnij ekran czernią

            # Rysowanie opcji menu
            for i, option in enumerate(menu_options):
                color = (255, 255, 255) if i == selected_option else (100, 100, 100)
                option_surface = self.font.render(option, True, color)
                self.screen.blit(option_surface, (self.szerokosc // 2 - option_surface.get_width() // 2, 150 + i * 50))

            # Aktualizacja ekranu
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:  # enter
                        return selected_option
                    elif event.key == pygame.K_w:  # w
                        selected_option = (selected_option - 1) % len(menu_options)
                    elif event.key == pygame.K_s:  # s
                        selected_option = (selected_option + 1) % len(menu_options)


class Wyniki:
    def __init__(self, szerokosc=400, wysokosc=600):
        self.szerokosc = szerokosc
        self.wysokosc = wysokosc

        # Inicjalizacja Pygame
        pygame.init()

        # Ustawienie ekranu
        self.screen = pygame.display.set_mode((self.szerokosc, self.wysokosc))
        pygame.display.set_caption('Pong - Wyniki')

        # Ustawienia czcionek
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 28)

    def wyswietl(self):
        dane = czytaj_plik_do_listy('wyniki.txt')
        dane_posortowane = posortuj_dane(dane)

        while True:
            self.screen.fill((0, 0, 0))  # Wypełnij ekran czernią

            # Nagłówek
            title_surface = self.font_large.render("Top 10", True, (255, 255, 255))
            self.screen.blit(title_surface, (self.szerokosc // 2 - title_surface.get_width() // 2, 20))

            # Nagłówki kolumn
            self.screen.blit(self.font_medium.render("Miejsce", True, (255, 255, 255)), (10, 70))
            self.screen.blit(self.font_medium.render("Imie", True, (255, 255, 255)), (self.szerokosc // 2 - 60, 70))
            self.screen.blit(self.font_medium.render("Punkty", True, (255, 255, 255)), (self.szerokosc - 115, 70))

            # Rysowanie wyników
            for i, (imie, wynik) in enumerate(dane_posortowane):
                if i >= 10:  # Ograniczenie do 10 wyników
                    break

                self.screen.blit(self.font_small.render(f"{i + 1}", True, (255, 255, 255)), (10, 70 + (i + 1) * 50))
                self.screen.blit(self.font_small.render(imie, True, (255, 255, 255)),
                                 (self.szerokosc // 2 - 60, 70 + (i + 1) * 50))
                self.screen.blit(self.font_small.render(str(wynik), True, (255, 255, 255)),
                                 (self.szerokosc - 115, 70 + (i + 1) * 50))

            pygame.display.flip()  # Aktualizacja ekranu

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:  # esc
                        return False


class NazwaUzytkownika:
    def __init__(self, szerokosc=400, wysokosc=600):
        self.szerokosc = szerokosc
        self.wysokosc = wysokosc
        self.imie = ""

        # Inicjalizacja Pygame
        pygame.init()

        # Ustawienie ekranu
        self.screen = pygame.display.set_mode((self.szerokosc, self.wysokosc))
        pygame.display.set_caption('Pong - Nazwa Użytkownika')

        # Ustawienia czcionek
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 28)

    def wyswietl(self):
        while True:
            self.screen.fill((0, 0, 0))  # Wypełnij ekran czernią

            # Wyświetlanie instrukcji
            self.screen.blit(self.font_large.render("Podaj swoje imie:", True, (255, 255, 255)), (50, 100))
            self.screen.blit(self.font_small.render("Enter - zapisz", True, (255, 255, 255)), (50, 150))
            self.screen.blit(self.font_small.render("Esc - wyjdz", True, (255, 255, 255)), (50, 200))

            # Wyświetlanie wprowadzonego imienia
            input_surface = self.font_large.render(self.imie, True, (255, 255, 255))
            self.screen.blit(input_surface, (85, 300))

            pygame.display.flip()  # Aktualizacja ekranu

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:  # Enter
                        return self.imie
                    elif event.key == pygame.K_BACKSPACE:  # Backspace
                        self.imie = self.imie[:-1]
                    elif event.key == pygame.K_ESCAPE:  # Escape
                        return None
                    elif event.unicode:  # Printable characters
                        if len(self.imie) < 10:
                            self.imie += event.unicode


def main():
    pygame.init()
    poziom = 1

    while True:
        menu = Menu()
        option = menu.wyswietl()
        if option == 2:
            break
        elif option == 0:
            gra = Pong(poziom)
            gra.gra()
            nazwa = NazwaUzytkownika()
            imie = nazwa.wyswietl()
            if imie is not None and imie != "":
                zapisz_wynik_do_pliku(imie, gra.gamer - gra.pc, "wyniki.txt")
            wyniki = Wyniki()
            wyniki.wyswietl()
        elif option == 1:
            setting = Settings()
            poziom = setting.wyswietl()

    pygame.quit()


if __name__ == "__main__":
    main()
