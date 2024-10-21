import sys
import pygame
from functions import *


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
            version_surface = self.ver_font.render("Ver. 0.6.2", True, (255, 255, 255))
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


class Souls:
    def __init__(self, text, szerokosc=400, wysokosc=600):
        self.text = text
        self.szerokosc = szerokosc
        self.wysokosc = wysokosc

        # Inicjalizacja Pygame
        pygame.init()

        # Ustawienie ekranu
        self.screen = pygame.display.set_mode((self.szerokosc, self.wysokosc))
        pygame.display.set_caption('Pong - Wyniki')

        # Ustawienia czcionek
        self.font = pygame.font.Font(None, 48)

    def wyswietl(self):

        while True:
            self.screen.fill((0, 0, 0))  # Wypełnij ekran czernią

            # Nagłówek
            title_surface = self.font.render(self.text, True, (255, 255, 255))
            self.screen.blit(title_surface, (self.szerokosc // 2 - title_surface.get_width() // 2, 100))

            pygame.display.flip()  # Aktualizacja ekranu

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:  # esc
                        return False
