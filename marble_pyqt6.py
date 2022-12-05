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
# # 2022/11/07 JP - dokončení a vytvoření funkcí nova_hra_stisk, animuj, krok_krok, herni_kolo
# # 2022/11/08 JP - ladění chyb
# # 2022/11/09 JP - výměna labelů pro zobrazování bodů za LCD
# # 2022/12/01 JP - animace zmizení řady
# # 2022/12/02 JP - úpravy proměnných, vylazení a příprava pro načítání ze/do souboru, vytvoření souboru a zprovoznění načítání a ukládání
# # 2022/12/03 JP - přidání popisků do ukládání dat do souboru
# # 2022/12/05 JP - přidání oznamovacího okna při skončení hry
################################

import marble_funkce

import sys, time
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, QLCDNumber, QMessageBox
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QTimer

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        # nastavení proměnných
        self.sirka_pole, self.odsazeni_shora, self.odsazeni_zleva = 50, 39, 9
        self.body, self.krok = 0, 0
        self.barva, self.barva_vyber, self.kulicky, self.pozice_vybrane_kulicky, self.cil_pozice, self.cesta, self.smazat_mista = [], [], [], [], [], [], []
        self.hra_bezi, self.hrac_je_na_tahu, self.vybrana_kulicka = False, False, False
        
        # vytvoření okna
        self.setFixedWidth(self.sirka_pole * sirka_matice + 2 * self.odsazeni_zleva)
        self.setFixedHeight(self.sirka_pole * sirka_matice + self.odsazeni_shora + self.odsazeni_zleva)
        self.setWindowTitle(text_hlavni_okno)
        # vytvoření layoutů kvůli rozložení na ploše
        self.layout_svisly = QVBoxLayout()
        self.layout_vodorovny = QHBoxLayout()
        self.layout_mrizka = QGridLayout()
        self.layout_mrizka.setContentsMargins(0,0,0,0)
        self.layout_mrizka.setSpacing(0)
        self.layout_nastaveni = QVBoxLayout()
        # vytvoření tlačítek a popisků
        self.Nova_hra_button = QPushButton(text_nova_hra)
        self.Nova_hra_button.clicked.connect(self.nova_hra_stisk)
        self.lcd = QLCDNumber()
        self.Nastaveni_button = QPushButton(text_nastaveni)
        #vytvoření časovačů
        self.pauza=QTimer()
        self.pauza.timeout.connect(self.konec_pauzy)
        self.pauza_krok=QTimer()
        self.pauza_krok.timeout.connect(self.krok_krok)
        self.pauza_az= QTimer()
        self.pauza_az.timeout.connect(self.animuj_zmizeni)
        
        # vytvoření herního pole
        self.pole = marble_funkce.vytvor_pole(sirka_matice)
        
        # načtení obrázků barev
        for i in range(pocet_barev + 1):
            adresa = adresa_obrazku + str(i).zfill(2) + '.png'
            self.barva.append(QPixmap(adresa).scaledToWidth(self.sirka_pole))
        
        # načtení obrázků barev při výběru
        for i in range(pocet_barev + 1):
            adresa = adresa_vybranych_obrazku + str(i).zfill(2) + '.png'
            self.barva_vyber.append(QPixmap(adresa).scaledToWidth(self.sirka_pole))
            
        # vytvoření herní mřížky
        for i in range(sirka_matice):
            radek=[]
            for j in range(sirka_matice):
                self.kulicka = QLabel(self)
                self.kulicka.mouseReleaseEvent = self.vyber_kulicky_stisk
                self.kulicka.setPixmap(self.barva[self.pole[i][j]])
                self.layout_mrizka.addWidget(self.kulicka, i, j)
                radek.append(self.kulicka)
            self.kulicky.append(radek)
            
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
        if self.hra_bezi:
            self.hra_bezi = False
            self.Nova_hra_button.setText(text_nova_hra)
            self.Nastaveni_button.setEnabled(True)
        else:
            # start hry
            self.body = 0
            self.lcd.display(self.body)
            self.Nova_hra_button.setText(text_konec_hry)
            self.Nastaveni_button.setEnabled(False)
            self.pole = marble_funkce.vytvor_pole(sirka_matice)
            self.prekresli_obraz()
            self.hra_bezi = True
            self.herni_kolo()
        
    def prekresli_obraz(self):
        # překreslí kuličky v přížce
        for i in range(sirka_matice):
            for j in range(sirka_matice):
                self.kulicky[i][j].setPixmap(self.barva[self.pole[i][j]])
    
    def vyber_kulicky_stisk(self, event):
        # akce při výběru kuličky nebo prázdného pole
        if self.hra_bezi and self.hrac_je_na_tahu:
            # pokud probíhá hra a hráč je na tahu tak pokračuj, jinak nic
            self.hrac_je_na_tahu = False
            point = event.scenePosition()
            i = int((point.y()-self.odsazeni_shora)/self.sirka_pole)
            j = int((point.x()-self.odsazeni_zleva)/self.sirka_pole)
            if self.vybrana_kulicka:
                # je vybraná kulička, kterou chceme přesunout, nyní vybíráme kam
                if self.pole[i][j] > 0:
                    # změna výběru kuličky, původní dej zpět, označ novou
                    self.kulicky[self.pozice_vybrane_kulicky[0]][self.pozice_vybrane_kulicky[1]].setPixmap(self.barva[self.pole[self.pozice_vybrane_kulicky[0]][self.pozice_vybrane_kulicky[1]]])
                    self.pozice_vybrane_kulicky = [i, j]
                    self.kulicky[i][j].setPixmap(self.barva_vyber[self.pole[i][j]])
                    self.hrac_je_na_tahu = True
                else:
                    # označ cíl a zavolej animaci
                    self.cil_pozice = [i, j]
                    self.kulicky[i][j].setPixmap(self.barva_vyber[0])
                    je_cesta, self.cesta = marble_funkce.najdi_cestu(self.pole, self.pozice_vybrane_kulicky, self.cil_pozice)
                    if je_cesta:
                        self.animuj()
                    else:
                        # cesta nenalezena, zruš výběr kuliček
                        self.pauza.start(cas_pauzy)
            else:
                # vybíráme kuličku, kterou chceme přesunout
                if self.pole[i][j] > 0:
                    self.pozice_vybrane_kulicky = [i, j]
                    self.vybrana_kulicka = True
                    self.kulicky[i][j].setPixmap(self.barva_vyber[self.pole[i][j]])
                self.hrac_je_na_tahu = True
                    
    def konec_pauzy(self):
        # dokončení zrušení výběru kuliček při nenalezení cesty, je vyžadována pauza před tímto krokem, aby byl vidět výběr a jeho zrušení, bez pauzy to zanikalo
        self.pauza.stop()
        self.kulicky[self.pozice_vybrane_kulicky[0]][self.pozice_vybrane_kulicky[1]].setPixmap(self.barva[self.pole[self.pozice_vybrane_kulicky[0]][self.pozice_vybrane_kulicky[1]]])
        self.kulicky[self.cil_pozice[0]][self.cil_pozice[1]].setPixmap(self.barva[self.pole[self.cil_pozice[0]][self.cil_pozice[1]]])
        self.vybrana_kulicka = False
        self.hrac_je_na_tahu = True
    
    def animuj(self):
        # přesun kuličky do cíle
        self.pole[self.cesta[-1][0]][self.cesta[-1][1]] = self.pole[self.cesta[0][0]][self.cesta[0][1]]
        self.pole[self.cesta[0][0]][self.cesta[0][1]] = 0
        self.krok = 0
        self.pauza_krok.start(cas_posunu)
    
    def krok_krok(self):
        if self.krok == len(self.cesta)-1:
            self.pauza_krok.stop()
            self.herni_kolo()
        else:
            self.kulicky[self.cesta[self.krok][0]][self.cesta[self.krok][1]].setPixmap(self.barva[0])
            self.kulicky[self.cesta[self.krok+1][0]][self.cesta[self.krok+1][1]].setPixmap(self.barva[self.pole[self.cesta[-1][0]][self.cesta[-1][1]]])        
            self.krok += 1
    
    def animuj_zmizeni(self):
        # animace smazání řady
        if self.krok < len(self.smazat_mista):
            self.kulicky[self.smazat_mista[self.krok][0]][self.smazat_mista[self.krok][1]].setPixmap(self.barva[0])
            self.krok += 1
        else:
            self.pauza_az.stop()      
            self.hrac_je_na_tahu = True
    
    def oznam_konec(self):
        # Oznámení počtu bodů na konci hry
        dlg = QMessageBox(self)
        dlg.setWindowTitle(text_oznameni_konec_tittle)
        dlg.setText(text_oznameni_konec_text + str(self.body))
        button = dlg.exec()
    
    def herni_kolo(self):
        self.smazat_mista, pocet_bodu = marble_funkce.zkontroluj_rady(self.pole, min_rada, zisk)
        if pocet_bodu == 0:
            self.pole = marble_funkce.pridej_kulicky(self.pole, prirustek, pocet_barev)
            self.prekresli_obraz()
            self.smazat_mista, pocet_bodu = marble_funkce.zkontroluj_rady(self.pole, min_rada, zisk)
        self.body += pocet_bodu
        self.lcd.display(self.body)
        if len(self.smazat_mista) > 0:
            # smazání řady
            for misto in self.smazat_mista:
                self.pole[misto[0]][misto[1]] = 0
            self.krok = 0
            self.pauza_az.start(rychlost_animace)
        else:
            # pokud se pole zaplnilo, ukonči hru
            if marble_funkce.je_pole_plne(self.pole):
                self.hra_bezi = False
                self.Nova_hra_button.setText(text_nova_hra)
                self.Nastaveni_button.setEnabled(True)
                self.oznam_konec()
            else:
                self.hrac_je_na_tahu = True


# Načtení proměnných které je možné měnit v nastavení a popisků
sirka_matice, pocet_barev, prirustek, min_rada, zisk, adresa_obrazku, adresa_vybranych_obrazku, cas_posunu, cas_pauzy, rychlost_animace, text_hlavni_okno, text_nova_hra, text_konec_hry, text_nastaveni, text_oznameni_konec_tittle, text_oznameni_konec_text = marble_funkce.nacti_data()

# a jedeeem
app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
