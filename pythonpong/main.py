from game import Pong
from screens import *


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
            lose = gra.gra()
            if lose == 1:
                souls = Souls("You Win")
                souls.wyswietl()
            elif lose == 2:
                souls = Souls("You Died")
                souls.wyswietl()
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
