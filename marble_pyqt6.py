#!/usr/bin/python3
#############################
# Modul: marble_pyqt6.py
# Autor: Jaroslav Porplycia
# Datum: 2022/10/27
# Verze: 0.01
"""
Hra na čtvercové desce o několika polích
V každém kole přibude několik kuliček několika barev
Hráč vybere kuličku a posune ji na jiné místo
Pokud kuličky vytvoří řadu vodorovnou, svislou nebo šikmou, o předem daném počtu kuliček nebo větším, tak kuličky zmizí a hráči se připíšou body
Hra končí v okamžiku, kdy je celé hrací pole obsazené

Až bude hra hotova, měla by splňovat tyto požadavky:
možnost tvořit jazykové mutace
možnost úpravy všech parametrů
možnost změn vzhledu
možnost hrát na různých platformách (windows, linux, apple, webovky, android, ios)
"""
###############################
# Log:
# # 2022/10/27 JP - založení projektu
# # 2022/10/31 JP - první testovací rozložení
# # 2022/11/01 JP - vytvoření grafického rozhraní, vytvořeni první sady image (a) pro základní funkčnost, zprovoznění startu hry a prvního přidání kuliček 
# # 2022/11/04 JP - vytvoření akcí kliknutí na herní pole, funkce vyber_kulicky_stisk a prekresli_obraz
# # 2022/11/06 JP - přidání pauzy při nenalezení cesty pomocí QTimer a vytvoření funkce animuj
# # 2022/11/07 JP - dokončení a vytvoření funkcí nova_hra_stisk, animuj, krok_presun, herni_kolo
# # 2022/11/08 JP - ladění chyb
# # 2022/11/09 JP - výměna labelů pro zobrazování bodů za LCD
# # 2022/12/01 JP - animace zmizení řady
################################

import marble_funkce
import language

import sys, time
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, QLCDNumber
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QTimer

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        # vytvoření okna
        self.setFixedWidth(sirka_okna)
        self.setFixedHeight(vyska_okna)
        self.setWindowTitle(text_hlavni_okno)
        # vytvoření layoutů kvůli rozložení na ploše
        self.layout_svisly = QVBoxLayout()
        self.layout_vodorovny = QHBoxLayout()
        self.layout_mrizka = QGridLayout()
        self.layout_mrizka.setContentsMargins(0,0,0,0)
        self.layout_mrizka.setSpacing(0)
        # vytvoření tlačítek a popisků
        self.Nova_hra_button = QPushButton(text_nova_hra)
        self.Nova_hra_button.clicked.connect(self.nova_hra_stisk)
        self.lcd = QLCDNumber()
        self.Nastaveni_button = QPushButton(text_nastaveni)
        #vytvoření časovačů
        self.pauza=QTimer()
        self.pauza.timeout.connect(self.konec_pauzy)
        self.pauza_presun=QTimer()
        self.pauza_presun.timeout.connect(self.krok_presun)
        self.pauza_az= QTimer()
        self.pauza_az.timeout.connect(self.animuj_zmizeni)
        
        # načtení obrázků barev
        for i in range(pocet_barev + 1):
            adresa = adresa_obrazku + str(i).zfill(2) + '.png'
            barva.append(QPixmap(adresa).scaledToWidth(sirka_pole))
        
        # načtení obrázků barev při výběru
        for i in range(pocet_barev + 1):
            adresa = adresa_vybranych_obrazku + str(i).zfill(2) + '.png'
            barva_vyber.append(QPixmap(adresa).scaledToWidth(sirka_pole))
            
        # vytvoření herní mřížky
        for i in range(sirka_matice):
            radek=[]
            for j in range(sirka_matice):
                self.kulicka = QLabel(self)
                self.kulicka.mouseReleaseEvent = self.vyber_kulicky_stisk
                self.kulicka.setPixmap(barva[pole[i][j]])
                self.layout_mrizka.addWidget(self.kulicka, i, j)
                radek.append(self.kulicka)
            kulicky.append(radek)
            
        # umístění do layoutů
        self.layout_vodorovny.addWidget(self.Nova_hra_button)
        self.layout_vodorovny.addWidget(self.lcd)
        self.layout_vodorovny.addWidget(self.Nastaveni_button)
        self.layout_svisly.addLayout(self.layout_vodorovny)
        self.layout_svisly.addLayout(self.layout_mrizka)
        widget = QWidget()
        widget.setLayout(self.layout_svisly)
        self.setCentralWidget(widget)
        
    def nova_hra_stisk(self):
        # Přepiš tlačítko na ukonči hru, deaktivuj tlačítko nastavení, přidej na desku první kuličky
        global hra, body, pole
        if hra:
            hra = False
            self.Nova_hra_button.setText(text_nova_hra)
            self.Nastaveni_button.setEnabled(True)
        else:
            # start hry
            body = 0
            self.lcd.display(body)
            self.Nova_hra_button.setText(text_konec_hry)
            self.Nastaveni_button.setEnabled(False)
            pole = marble_funkce.vytvor_pole(sirka_matice)
            self.prekresli_obraz()
            hra = True
            self.herni_kolo()
        
    def prekresli_obraz(self):
        # překreslí kuličky v přížce
        for i in range(sirka_matice):
            for j in range(sirka_matice):
                kulicky[i][j].setPixmap(barva[pole[i][j]])
    
    def vyber_kulicky_stisk(self, event):
        global pole, vybrana_kulicka, vybrana_kulicka_pozice, cil_pozice, cesta, hrac_je_na_tahu
        # akce při výběru kuličky nebo prázdného pole
        if hra and hrac_je_na_tahu:
            # pokud probíhá hra a hráč je na tahu tak pokračuj, jinak nic
            hrac_je_na_tahu = False
            point = event.scenePosition()
            i = int((point.y()-odsazeni_shora)/sirka_pole)
            j = int((point.x()-odsazeni_zleva)/sirka_pole)
            if vybrana_kulicka:
                # je vybraná kulička, kterou chceme přesunout, nyní vybíráme kam
                if pole[i][j] > 0:
                    # změna výběru kuličky, původní dej zpět, označ novou
                    kulicky[vybrana_kulicka_pozice[0]][vybrana_kulicka_pozice[1]].setPixmap(barva[pole[vybrana_kulicka_pozice[0]][vybrana_kulicka_pozice[1]]])
                    vybrana_kulicka_pozice = [i, j]
                    kulicky[i][j].setPixmap(barva_vyber[pole[i][j]])
                    hrac_je_na_tahu = True
                else:
                    # označ cíl a zavolej animaci
                    cil_pozice = [i, j]
                    kulicky[i][j].setPixmap(barva_vyber[0])
                    je_cesta, cesta = marble_funkce.najdi_cestu(pole, vybrana_kulicka_pozice, cil_pozice)
                    if je_cesta:
                        self.animuj(cesta)
                    else:
                        # cesta nenalezena, zruš výběr kuliček
                        self.pauza.start(cas_pauzy)
            else:
                # vybíráme kuličku, kterou chceme přesunout
                if pole[i][j] > 0:
                    vybrana_kulicka_pozice = [i, j]
                    vybrana_kulicka = True
                    kulicky[i][j].setPixmap(barva_vyber[pole[i][j]])
                hrac_je_na_tahu = True
                    
    def konec_pauzy(self):
        # dokončení zrušení výběru kuliček při nenalezení cesty, je vyžadována pauza před tímto krokem, aby byl vidět výběr a jeho zrušení, bez pauzy to zanikalo
        global vybrana_kulicka, hrac_je_na_tahu
        self.pauza.stop()
        kulicky[vybrana_kulicka_pozice[0]][vybrana_kulicka_pozice[1]].setPixmap(barva[pole[vybrana_kulicka_pozice[0]][vybrana_kulicka_pozice[1]]])
        kulicky[cil_pozice[0]][cil_pozice[1]].setPixmap(barva[pole[cil_pozice[0]][cil_pozice[1]]])
        vybrana_kulicka = False
        hrac_je_na_tahu = True
    
    def animuj(self, cesta):
        # přesun kuličky do cíle
        global pole, presun
        pole[cesta[-1][0]][cesta[-1][1]] = pole[cesta[0][0]][cesta[0][1]]
        pole[cesta[0][0]][cesta[0][1]] = 0
        presun = 0
        self.pauza_presun.start(cas_posunu)
    
    def krok_presun(self):
        global presun
        if presun == len(cesta)-1:
            self.pauza_presun.stop()
            self.herni_kolo()
        else:
            kulicky[cesta[presun][0]][cesta[presun][1]].setPixmap(barva[0])
            kulicky[cesta[presun+1][0]][cesta[presun+1][1]].setPixmap(barva[pole[cesta[-1][0]][cesta[-1][1]]])        
            presun += 1
    
    def animuj_zmizeni(self):
        # animace smazání řady
        global hrac_je_na_tahu, krok_animace_zmizeni
        if krok_animace_zmizeni < len(smazat_mista):
            kulicky[smazat_mista[krok_animace_zmizeni][0]][smazat_mista[krok_animace_zmizeni][1]].setPixmap(barva[0])
            krok_animace_zmizeni += 1
        else:
            self.pauza_az.stop()      
            hrac_je_na_tahu = True
    
    def herni_kolo(self):
        global pole, smazat_mista, pocet_bodu, body, hrac_je_na_tahu, hra, dokoncena_animace, krok_animace_zmizeni
        smazat_mista, pocet_bodu = marble_funkce.zkontroluj_rady(pole, min_rada, zisk)
        if pocet_bodu == 0:
            pole = marble_funkce.pridej_kulicky(pole, prirustek, pocet_barev)
            self.prekresli_obraz()
            smazat_mista, pocet_bodu = marble_funkce.zkontroluj_rady(pole, min_rada, zisk)
        body += pocet_bodu
        self.lcd.display(body)
        if len(smazat_mista) > 0:
            # smazání řady
            for misto in smazat_mista:
                pole[misto[0]][misto[1]] = 0
            krok_animace_zmizeni = 0
            self.pauza_az.start(rychlost_animace)
        else:
            # pokud se pole zaplnilo, ukonči hru
            if marble_funkce.je_pole_plne(pole):
                print(body)
                hra = False
                self.Nova_hra_button.setText(text_nova_hra)
                self.Nastaveni_button.setEnabled(True)
            else:
                hrac_je_na_tahu = True

sirka_matice, pocet_barev, prirustek, min_rada, zisk, jazyk = marble_funkce.nacti_data()   # načtení proměnných které je možné měnit v nastavení
pole = marble_funkce.vytvor_pole(sirka_matice)  # vytvoření pole
# Prvotní nastavení proměnných pro vzhled a běh programu
adresa_obrazku = 'images/a'
adresa_vybranych_obrazku = 'images/a1'
sirka_pole = 50
body, presun, krok_animace_zmizeni = 0, 0, 0
cas_posunu, cas_pauzy, rychlost_animace = 50, 500,50
odsazeni_shora, odsazeni_zleva = 39, 9
barva, barva_vyber, kulicky, vybrana_kulicka_pozice, cil_pozice = [], [], [], [], []
hra, hrac_je_na_tahu, vybrana_kulicka = False, False, False
# Výpočty rozměrů
sirka_okna = sirka_pole * sirka_matice + 2 * odsazeni_zleva
vyska_okna = sirka_pole * sirka_matice + odsazeni_shora + odsazeni_zleva

# Nastavení popisků, dodělat tak, aby se načítaly z jazykového souboru
text_nova_hra = "Začni hrát"
text_konec_hry = "Ukonči hru"
text_hlavni_okno = "Marble"
text_pocet_bodu = "Počet bodů: "
text_nastaveni = "Nastavení"

# a jedeeem
app = QApplication(sys.argv)

window = MainWindow()
window.show()


app.exec()

# CO DODĚLAT
# občas nepřesune kuličku a jede dál - prověřit