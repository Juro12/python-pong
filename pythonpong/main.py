import sys
import pygame
import numpy as np
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
        if self.x <= 0:
            self.x = 1

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
            version_surface = self.ver_font.render("Ver. 0.4.2", True, (255, 255, 255))
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
        dane = czytaj_plik_do_listy('dane.txt')
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
