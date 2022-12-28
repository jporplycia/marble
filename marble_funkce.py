#!/usr/bin/python3
#############################
# Modul: marble_funkce.py
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
# # 2022/10/20 JP - založení projektu, vytvoření funkce nacti_data()
# # 2022/10/21 JP - vytvoření funkcí vytvor_pole(), pridej_kulicky(), zobraz_pole()
# # 2022/10/24 JP - vytvoření funkcí zkontroluj_rady() - výpočet pro vodorovný a svislý směr
# # 2022/10/25 JP - vytvoření funkcí zkontroluj_rady() - výpočet pro šikmé směry, je_pole_plne()
# # 2022/10/26 JP - dolazení komentářů a oddělení testopvacích funkcí od hlavních, vytvoření funkcí je_pole_plne(), najdi_cestu(), vypln_mapu()
# # 2022/10/27 JP - dokončení funkce najdi_cestu(), vytvoření podfunkce kontrola(), přejmenování souboru na marble_funkce.py a smazání všeho kromě potřebných funkcí
# # 2022/10/27 JP - původní soubor ponechán pod názvem marble_puvodni.py
# # 2022/11/16 JP - oprava vyhledávání řad i v krajních pozicích
# # 2022/12/02 JP - ukládání a načtení dat ze souboru
# # 2022/12/03 JP - přidání popisků do ukládání dat do souboru
# # 2022/12/05 JP - doplnění dalších proměnných k načtení a uložení
# # 2022/12/06 JP - oprava výpočtu bodů, aby se přičítali správně body při smazání řad ve více směrech
# # 2022/12/07 JP - rozdělení uložení nastavení a jazyků - každé do svého souboru a svou funkcí
# # 2022/12/08 JP - odstranění proměnných pro rychlost času, animace a posunu odstraněny z ukládání, ošetření řady zisku pro případ že je krátká, vezme se poslední hodnota
# # 2022/12/15 JP - úprava funkce načti text
# # 2022/12/16 JP - vytvoření funkce nacti_jazyky
################################

from random import sample
import random
import configparser

def nacti_data():
    # načte nastavení proměnných ze souboru
    try:
        config = configparser.ConfigParser()
        config.read('data.conf')
        sirka_matice = int(config.get('Nastaveni','sirka_matice', fallback = 8))
        pocet_barev = int(config.get('Nastaveni','pocet_barev', fallback = 8))
        prirustek = int(config.get('Nastaveni','prirustek', fallback = 3))
        min_rada = int(config.get('Nastaveni','min_rada', fallback = 5))
        zisk = [int(n) for n in config.get('Nastaveni','zisk', fallback = '1, 3, 6, 10, 15, 21, 28, 36, 45, 55, 66, 78, 91, 105, 120').split(',')]
        adresa_obrazku = config.get('Nastaveni','adresa_obrazku', fallback = 'a')
        jazyk = config.get('Nastaveni','jazyk', fallback = 'česky')
        return(sirka_matice, pocet_barev, prirustek, min_rada, zisk, adresa_obrazku, jazyk)
    except:
        print('chyba souboru, vytvořen nový')
        sirka_matice = 8
        pocet_barev = 8
        prirustek = 3
        min_rada = 5
        zisk = [1, 3, 6, 10, 15, 21, 28, 36, 45, 55, 66, 78, 91, 105, 120]
        adresa_obrazku = 'a'
        jazyk = 'česky'
        uloz_data(sirka_matice, pocet_barev, prirustek, min_rada, zisk, adresa_obrazku, jazyk)
        return(sirka_matice, pocet_barev, prirustek, min_rada, zisk, adresa_obrazku, jazyk)

def uloz_data(sirka_matice, pocet_barev, prirustek, min_rada, zisk, adresa_obrazku, jazyk):
    #uloží nastavení proměnných do souboru
    config = configparser.ConfigParser()
    config['Nastaveni'] = {'sirka_matice': sirka_matice, 
                        'pocet_barev': pocet_barev,
                        'prirustek': prirustek,
                        'min_rada': min_rada,
                        'zisk': str(zisk)[1:-1],
                        'adresa_obrazku': adresa_obrazku,
                        'jazyk': jazyk}
    with open('data.conf', 'w') as configfile:
        config.write(configfile)

def nacti_jazyky():
    # načte seznam jazyků zadaných v lang.conf
    try:
        config = configparser.ConfigParser()
        config.read('lang.conf')
        return(config.sections())
    except:
        return(['česky'])

def nacti_text(jazyk):
    # načte nastavení textových proměnných ze souboru
    texty = []
    try:
        config = configparser.ConfigParser()
        config.read('lang.conf')
        texty.append(config.get(jazyk,'t0'))
        texty.append(config.get(jazyk,'t1'))
        texty.append(config.get(jazyk,'t2'))
        texty.append(config.get(jazyk,'t3'))
        texty.append(config.get(jazyk,'t4'))
        texty.append(config.get(jazyk,'t5'))
        texty.append(config.get(jazyk,'t6'))
        texty.append(config.get(jazyk,'t7'))
        texty.append(config.get(jazyk,'t8'))
        texty.append(config.get(jazyk,'t9'))
        texty.append(config.get(jazyk,'t10'))
        texty.append(config.get(jazyk,'t11'))
        texty.append(config.get(jazyk,'t12'))
        texty.append(config.get(jazyk,'t13'))
        texty.append(config.get(jazyk,'t14'))
        return(texty)
    except:
        print('chyba jazykového souboru, vytvořen nový')
        texty = ['Marble','Začni hru','Ukonči hru','Nastavení','Konec hry','Konec hry! Počet bodů: ','Šířka hracího pole: ','Počet barev: ','Přírůstek kuliček: ','Délka řady pro smazání: ','Zisk za počet kuliček ','Adresa obrázků ','Adresa vybraných obrázků ','Jazyk ','Uložit a zavřít','Zpět bez uložení']
        #uloží nastavení textových proměnných do souboru
        config = configparser.ConfigParser()
        config['česky'] = {
                        't0': texty[0],
                        't1': texty[1],
                        't2': texty[2],
                        't3': texty[3],
                        't4': texty[4],
                        't5': texty[5],
                        't6': texty[6],
                        't7': texty[7],
                        't8': texty[8],
                        't9': texty[9],
                        't10': texty[10],
                        't11': texty[11],
                        't12': texty[12],
                        't13': texty[13],
                        't14': texty[14]
                        }
        with open('lang.conf', 'w') as configfile:
            config.write(configfile)
        return(texty)

def vytvor_pole(sirka_matice):
    # vytvoří pole a nastaví všem polím hodnotu 0
    pole = []
    for i in range(sirka_matice):
        radek=[]
        for j in range (sirka_matice):
            radek.append(0)
        pole.append(radek)
    return(pole)

def pridej_kulicky(pole, prirustek, pocet_barev):
    # přidá kuličky na hrací pole
    prazdna_mista = 0
    rozmer = len(pole)
    # spočítá počet prázdných polí
    for radek in pole:
        prazdna_mista += radek.count(0)
    # pokud je prázdných polí méně než přírůstek tak sníží počet přidaných kuliček na povolené množství a zapne ukazatel zaplnění herního pole
    if prazdna_mista < prirustek: prirustek = prazdna_mista
    # vygeneruje pořadí do kterých prázdných polí se kuličky přidají
    mista = sample(range(0, prazdna_mista), prirustek)
    mista.sort()
    # nastaví polím v daném pořadí barvy
    poradi = 0
    kulicka = 0
    for i in range(rozmer):
        for j in range(rozmer):
            if pole[i][j] == 0:
                if poradi == mista[kulicka]:
                    pole[i][j] = random.randint(1, pocet_barev)
                    kulicka += 1
                    if kulicka == prirustek: return(pole)
                poradi += 1

def kontrola(policko,i,j,predchozi,pocet_v_rade,min_rada,smazat_mista,ke_smazani):
    #kontrola daného políčka, podfunkce k funkci zkontroluj_rady()
    if policko == 0: # je políčko prázdné?
        if pocet_v_rade >= min_rada: # byla posloupnost dost dlouhá?
            smazat_mista += ke_smazani # přidej políčka ke smazání
        pocet_v_rade = 0
        ke_smazani = []
    else: # políčko prázdné není
        if policko == predchozi: # kulička je stejná jako na předchozím poli?
            pocet_v_rade += 1
            ke_smazani += [[i,j]]
        else: # kulička je jiná než na předchozím poli
            if pocet_v_rade >= min_rada:
                smazat_mista += ke_smazani # přidej políčka ke smazání
                ke_smazani = []
            pocet_v_rade = 1
            ke_smazani = [[i,j]]
    predchozi = policko
    return(pocet_v_rade,smazat_mista,ke_smazani,predchozi)

def zkontroluj_rady(pole, min_rada, zisk):
    # kontrola, zda je vytvořena jedna nebo více řad pro smazání a přičtení bodů
    rozmer = len(pole)
    smazat_mista = []
    # kontrola ve vodorovném směru
    for i in range(rozmer):
        pocet_v_rade = 0
        ke_smazani = []
        predchozi = 0
        for j in range(rozmer):
            pocet_v_rade,smazat_mista,ke_smazani,predchozi = kontrola(pole[i][j],i,j,predchozi,pocet_v_rade,min_rada,smazat_mista,ke_smazani)
        if pocet_v_rade >= min_rada:
            smazat_mista += ke_smazani # přidej políčka ke smazání

    # kontrola ve svislém směru
    for j in range(rozmer):
        pocet_v_rade = 0
        ke_smazani = []
        predchozi = 0
        for i in range(rozmer):
            pocet_v_rade,smazat_mista,ke_smazani,predchozi = kontrola(pole[i][j],i,j,predchozi,pocet_v_rade,min_rada,smazat_mista,ke_smazani)
        if pocet_v_rade >= min_rada:
            smazat_mista += ke_smazani # přidej políčka ke smazání
    
    #kontrola v šikmém směru shora doleva
    x = 0
    for y in range(min_rada-1,rozmer):
        pocet_v_rade = 0
        ke_smazani = []
        predchozi = 0
        i = x
        for j in range(y,-1,-1):
            pocet_v_rade,smazat_mista,ke_smazani,predchozi = kontrola(pole[i][j],i,j,predchozi,pocet_v_rade,min_rada,smazat_mista,ke_smazani)
            i +=1
        if pocet_v_rade >= min_rada:
            smazat_mista += ke_smazani # přidej políčka ke smazání
    for x in range(1,min_rada+1):
        pocet_v_rade = 0
        ke_smazani = []
        predchozi = 0
        i = x
        for j in range(y,x-1,-1):
            pocet_v_rade,smazat_mista,ke_smazani,predchozi = kontrola(pole[i][j],i,j,predchozi,pocet_v_rade,min_rada,smazat_mista,ke_smazani)
            i +=1
        if pocet_v_rade >= min_rada:
            smazat_mista += ke_smazani # přidej políčka ke smazání
        
    #kontrola v šimkém směru shora doprava
    x = 0
    for y in range(min_rada,-1,-1):
        pocet_v_rade = 0
        ke_smazani = []
        predchozi = 0
        i = x
        for j in range(y,rozmer):
            pocet_v_rade,smazat_mista,ke_smazani,predchozi = kontrola(pole[i][j],i,j,predchozi,pocet_v_rade,min_rada,smazat_mista,ke_smazani)
            i +=1
        if pocet_v_rade >= min_rada:
            smazat_mista += ke_smazani # přidej políčka ke smazání
    for x in range(1,min_rada+1):
        pocet_v_rade = 0
        ke_smazani = []
        predchozi = 0
        i = x
        for j in range(y,rozmer-x):
            pocet_v_rade,smazat_mista,ke_smazani,predchozi = kontrola(pole[i][j],i,j,predchozi,pocet_v_rade,min_rada,smazat_mista,ke_smazani)
            i +=1
        if pocet_v_rade >= min_rada:
            smazat_mista += ke_smazani # přidej políčka ke smazání
    
    # smazání dulicit ze seznamu ke smazání
    smazat_mista_bez_duplicit = []
    for i in smazat_mista:
        if i not in smazat_mista_bez_duplicit:
            smazat_mista_bez_duplicit.append(i)
    # zjištění počtu bodů
    if len(smazat_mista_bez_duplicit) >= min_rada:
        if len(smazat_mista_bez_duplicit) - min_rada >= len(zisk): # pokud není řada zisků dostatečně dlouhá tak použít poslední hodnotu
            pocet_bodu = zisk[-1]
        else:
            pocet_bodu = zisk[len(smazat_mista_bez_duplicit) - min_rada]
    else:
        pocet_bodu = 0
    return(smazat_mista_bez_duplicit, pocet_bodu)

def je_pole_plne(pole):
    # zkontroluje zda je na pole celé zaplněné kuličkami
    prazdna_mista = 0
    for radek in pole:
        prazdna_mista += radek.count(0)
    if prazdna_mista == 0:
        return(True)
    else:
        return(False)

def najdi_cestu(pole, start, cil):
    # najde cestu přesunu kuličky ze startu do cíle, pokud existuje
    rozmer = len(pole)
    mapa = vytvor_pole(rozmer) # vytvoří pomocné pole pro zápis kroků
    krok = 1
    nalezeno = False
    mista = [start]
    seznam_mist = []
    while not nalezeno and not mista == []:
        seznam_mist.append(mista)
        nalezeno, mista_nevycistena = vypln_mapu(mapa, pole, mista, cil, krok, rozmer-1)
        krok += 1
        # smazání duplicit
        mista = []
        for i in mista_nevycistena: 
            if i not in mista: mista.append(i)
    if nalezeno:
        # vezme seznam_mist a najde v něm cestu, kterou uloží do proměnné cesta
        cesta = [cil] # cestu zapisuje odzadu, začíná cílem
        i, j = len(seznam_mist)-1, 0
        while i >= 0:
            if abs(cil[0]-seznam_mist[i][j][0])+abs(cil[1]-seznam_mist[i][j][1]) == 1: # kontrola zda jsou políčka vedle sebe
                cesta = [seznam_mist[i][j]] + cesta # nalezený krok cesty přidá na začátek seznamu
                cil = seznam_mist[i][j]
                i -= 1
                j = 0
            else:
                j += 1
        return(True, cesta) # cesta nalezena
    else:
        return(False, []) # cesta nenalezena

def vypln_mapu(mapa, pole, seznam_pozic, cil, krok, rozmer):
    #vyplní v mapě okolní pole kolem seznamů pozic hodnotou krok, pokud narazí na cíl tak vráti True
    
    dalsi_pole = []
    
    for pozice in seznam_pozic:
        i = pozice[0]
        if pozice[1] > 0:
            j = pozice[1]-1
            if [i,j] == cil: return(True, dalsi_pole)
            if pole[i][j] == 0 and mapa[i][j] == 0: dalsi_pole.append([i,j])
        if pozice[1] < rozmer:
            j = pozice[1]+1
            if [i,j] == cil: return(True, dalsi_pole)
            if pole[i][j] == 0 and mapa[i][j] == 0: dalsi_pole.append([i,j])
        j = pozice[1]
        if pozice[0] > 0:
            i = pozice[0]-1
            if [i,j] == cil: return(True, dalsi_pole)
            if pole[i][j] == 0 and mapa[i][j] == 0: dalsi_pole.append([i,j])
        if pozice[0] < rozmer:
            i = pozice[0]+1
            if [i,j] == cil: return(True, dalsi_pole)
            if pole[i][j] == 0 and mapa[i][j] == 0: dalsi_pole.append([i,j])
    
    for pozice in dalsi_pole:
        mapa[pozice[0]][pozice[1]] = krok
    return(False, dalsi_pole)
