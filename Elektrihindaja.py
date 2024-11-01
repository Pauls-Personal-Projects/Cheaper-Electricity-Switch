#!/usr/bin/env python3
# -*- coding: utf-8 -*-

####################################################################################################
#                                                                                                  #
#                                           ELEKTRIHIND                                            #
#                                                                                                  #
####################################################################################################
'''
Looja:        Paul J. Aru        -    https://github.com/paulpall
Kuupäev:      25/06/2022
Uuendatud:    01/11/2024

TODO:
Vaata Muutuja nimed üle
Vaata Meetodi Kirjeldused üle
'''





####################################################################################################
#    SÄTTED/TEEGID                                                                                 #
####################################################################################################
# Eleringi Elektrihinna Vahemiku Aadress API
ELERINGI_LINK = "https://dashboard.elering.ee/api/nps/price?start="
#+ 2022-09-22T09%3A40%3A00.000Z&end=2022-09-23T00%3A00%3A00.000Z"
# Kaust Kuhu Arhiveeritakse Kõik Andmed
#ANDMEKAUST = "Elektri_TuruHind" #IDE Kaust
ANDMEKAUST = "/volume7/Arhiiv/Teave/Elektri Turuhind" #Pilve Kaust
API_ERALDAJA = "%%3A"
TABELI_ÄÄRIS = " "
TABELI_TULBAJOON = "║"
TABELI_REAJOON = "═"
TABELI_NURK_1 = "╔"
TABELI_NURK_2 = "╗"
TABELI_NURK_3 = "╝"
TABELI_NURK_4 = "╚"
TABELI_KÜLGNURK_1 = "╦"
TABELI_KÜLGNURK_2 = "╣"
TABELI_KÜLGNURK_3 = "╩"
TABELI_KÜLGNURK_4 = "╠"
TABELI_RISTNURK = "╬"
import math                                 # ElektriAndmed Tabeli Laiuste Ümardamiseks.
from pytz import timezone					# Ajatsooni määramiseks.
AJATSOON = timezone('Europe/Tallinn')
import requests								# Eleringi APIga Ühendumiseks.
from datetime import datetime, timedelta	# API Kellaaja konverteerimiseks.
from dateutil import tz, parser				# API Kellaaja konverteerimiseks.
import os									# Failide Salvestamiseks ja Lugemiseks.
import csv									# Failide Salvestamiseks ja Lugemiseks.
from inspect import signature				# Algoritmide Parameetritele Ligipääsemiseks.
from Lülitaja import silumine				# Veateate Edastamiseks Synology DSM'ile.
import GoogleKalender





####################################################################################################
#    ALLALAADIMISE FUNKTSIOONID                                                                    #
####################################################################################################
def _kuupäevad_API_vormingus(alg_aeg:datetime, lõpp_aeg:datetime):
    '''
    Vormib Kuupäevad Eleringi API Päringu Aadressis Oodatud Formaati.
    '''
    alg_kuupäev=alg_aeg.astimezone().replace(tzinfo=tz.gettz('Europe/Tallinn')).astimezone(tz.tzutc())
    lõpp_kuupäev=lõpp_aeg.astimezone().replace(tzinfo=tz.gettz('Europe/Tallinn')).astimezone(tz.tzutc())
    vormitud_kuupäev = alg_kuupäev.strftime("%Y-%m-%dT%H"
        +API_ERALDAJA+"%M"+API_ERALDAJA+"00.000Z&end=")+lõpp_kuupäev.strftime("%Y-%m-%dT%H"
        +API_ERALDAJA+"%M"+API_ERALDAJA+"00.000Z")
    return vormitud_kuupäev



def _elektri_hind_vahemikus(alg_aeg:datetime, lõpp_aeg:datetime, api_aadress:str):
    '''
    Saadab Eleringi APIle Päringu Elektrituru Hindade Kohta Antud Ajavahemikus.
    '''
    print("Küsin Elektrihinda Vahemikus "+alg_aeg.strftime("%d.%m.%Y(%H:%M)")+
          " - "+lõpp_aeg.strftime("%d.%m.%Y(%H:%M)"))
    try:
        api_päring = requests.get(api_aadress+_kuupäevad_API_vormingus(alg_aeg, lõpp_aeg)).json()
    except:
        print("VIGA: Eleringiga Ühenduse Loomisel!")
        silumine = True
        return
    if api_päring["success"]:
        elektri_hinnad = []
        for aeg in api_päring["data"]["ee"]:
            elektri_hinnad.append(
                {"Kuupäev":AJATSOON.localize(datetime.fromtimestamp(aeg["timestamp"])), "Hind":aeg["price"]})
        print("Vastati Elektrihinnaga Vahemikus "+
              elektri_hinnad[0]["Kuupäev"].strftime("%d.%m.%Y(%H:%M)")+" - "+
              elektri_hinnad[-1]["Kuupäev"].strftime("%d.%m.%Y(%H:%M)"))
        return elektri_hinnad
    else:
        print("VIGA: Elering ("+requests.get(api_aadress).status_code+")")
        silumine = True





####################################################################################################
#    ANDMETÖÖTLUS                                                                                  #
####################################################################################################
class ElektriAndmed:
    '''
    Kõik Elektri Hinna ja Voolu Lülititega Andmetega Seonduv.
    ''' 
    def __init__(oma):
        '''
        #Loob Uue ElektriAndmed Andmetüübi.
        '''
        oma._tabel = []
        oma._rea_järg = None



    def __repr__(oma):
        '''
        Tõlgendab ElektriAndmed Teksti Vormingusse.
        '''
        if oma._tabel is None or not (len(oma._tabel) > 0):
            return "VIGA: Elektri Andmed Puuduvad - "+str(oma._tabel)
        # TULBA LAIUSTE ARVUTAMINE
        päised = set()
        for rida in oma._tabel:
            päis = tuple(rida.keys())
            if päis not in päised:
                päised.add(päis)
        võimalikud_tulbad=set()
        for päis in päised:
            võimalikud_tulbad.update(päis)
        tulba_laiused = {str(võimalik_tulp): len(str(võimalik_tulp)) for võimalik_tulp in võimalikud_tulbad}
        for tulba_nimi in tulba_laiused.keys():
            tulba_väärtuse_laius = max(len(str(rida[tulba_nimi])) for rida in oma._tabel if tulba_nimi in rida.keys())
            if tulba_väärtuse_laius > tulba_laiused[tulba_nimi]:
                tulba_laiused[tulba_nimi] = tulba_väärtuse_laius
        # TEKSTI KONSTRUKTOR
        # ┌─────────────┬─────────────┐
        tekst = TABELI_NURK_1
        for tulba_arv, tulba_laius in enumerate(tulba_laiused.values()):
            joone_laius = tulba_laius+(2*len(TABELI_ÄÄRIS))
            tekst+=TABELI_REAJOON*joone_laius
            if tulba_arv < len(tulba_laiused) - 1:
                tekst += TABELI_KÜLGNURK_1
            else:
                tekst += TABELI_NURK_2+"\n"
        # │ andmetüüp1 │ andmetüüp2 │
        tekst += TABELI_TULBAJOON
        for tulba_nimi, tulba_laius in tulba_laiused.items():
            äärise_laius = tulba_laius-len(tulba_nimi)+(2*len(TABELI_ÄÄRIS))
            tekst+=TABELI_ÄÄRIS*math.ceil(äärise_laius / 2)
            tekst+=tulba_nimi
            tekst+=TABELI_ÄÄRIS*math.floor(äärise_laius / 2)+TABELI_TULBAJOON
        tekst+="\n"
        # ├─────────────┼──────────────┤
        tekst += TABELI_KÜLGNURK_4
        for tulba_arv, tulba_laius in enumerate(tulba_laiused.values()):
            joone_laius = tulba_laius+(2*len(TABELI_ÄÄRIS))
            tekst+=TABELI_REAJOON*joone_laius
            if tulba_arv < len(tulba_laiused) - 1:
                tekst += TABELI_RISTNURK
            else:
                tekst += TABELI_KÜLGNURK_2+"\n"
        # │  väärtus1  │  väärtus2  │
        for rida in oma._tabel:
            tekst+=TABELI_TULBAJOON
            for tulba_nimi, tulba_laius in tulba_laiused.items():
                if tulba_nimi not in rida.keys():
                    sisu=""
                elif isinstance(rida[tulba_nimi], float):
                    sisu=f'{rida[tulba_nimi]:6.2f}'
                elif isinstance(rigda[tulba_nimi], bool):
                    sisu=oma._booleani_tõlge(rida[tulba_nimi])
                elif isinstance(rida[tulba_nimi], datetime):
                    sisu=rida[tulba_nimi].strftime("%H:%M(%z) [%d.%m.%Y]")
                else:
                    sisu=str(rida[tulba_nimi])
                äärise_laius = tulba_laius-len(sisu)+(2*len(TABELI_ÄÄRIS))
                tekst+=TABELI_ÄÄRIS*math.ceil(äärise_laius / 2)
                tekst+=sisu
                tekst+=TABELI_ÄÄRIS*math.floor(äärise_laius / 2)+TABELI_TULBAJOON
            tekst+="\n"
        # └─────────────┴─────────────┘
        tekst += TABELI_NURK_4
        for tulba_arv, tulba_laius in enumerate(tulba_laiused.values()):
            joone_laius = tulba_laius+(2*len(TABELI_ÄÄRIS))
            tekst+=TABELI_REAJOON*joone_laius
            if tulba_arv < len(tulba_laiused) - 1:
                tekst += TABELI_KÜLGNURK_3
            else:
                tekst += TABELI_NURK_3+"\n"
        return tekst



    def loe_võrgust(oma, alg_aeg:datetime, lõpp_aeg:datetime):
        '''
        Andes Ajavahemiku, Määrab ElektriAndmete Väärtuseks
        Eleringi Elektrihinnad Antud Ajavahemikust.
        '''
        oma._tabel = _elektri_hind_vahemikus(alg_aeg, lõpp_aeg, ELERINGI_LINK)



    def _loe_failist(oma, fail:str, alg_aeg:datetime, lõpp_aeg:datetime):
        '''
        Lisab Ühe Kuu ElektriAndmed Antud .csv Failist.
        '''
        with open(fail, mode ='r', newline='', encoding='utf-8')as csv_fail:
            csv_tabel = list(csv.reader(csv_fail))
            #PÄIS
            try:
                päis = csv_tabel[0]
            except:
                print("VIGA:", fail, "On Tühi!")
                silumine = True
            #ANDMED
            for rida in csv_tabel:
                if rida[0] == "Kuupäev":
                    if rida != päis:
                        päis = rida
                elif parser.parse(rida[0]) < alg_aeg or parser.parse(rida[0]) > lõpp_aeg:
                    continue
                else:
                    andmepunkt = {}
                    for tulba_arv, _ in enumerate(rida):
                        if päis[tulba_arv] == "Kuupäev":
                            andmepunkt[päis[tulba_arv]]=parser.parse(rida[tulba_arv])
                        elif päis[tulba_arv] == "Hind" or "Tunni Keskmine" in päis[tulba_arv]:
                            andmepunkt[päis[tulba_arv]]=float(rida[tulba_arv])
                        else:
                            andmepunkt[päis[tulba_arv]]=oma._booleani_tõlge(rida[tulba_arv])
                    oma._tabel.append(andmepunkt)



    def loe_ajavahemik(oma, kaust:str, alg_aeg:datetime, lõpp_aeg:datetime):
        '''
        Andes Ajavahemiku, Määrab ElektriAndmete Väärtuseks
        Antud Kaustast ning Antud Ajavahemikust Andmed.
        '''
        for aasta in range(alg_aeg.year, lõpp_aeg.year+1):
            if lõpp_aeg.month < alg_aeg.month:
                lõpp_kuu = 12
            else:
                lõpp_kuu = lõpp_aeg.month
            for kuu in range(alg_aeg.month, lõpp_kuu+1):
                kuu_fail = (kaust+"/"+str(aasta)+"/Elektri_turuhind_"
                			+f'{kuu:02d}'+"-"+str(aasta)+".csv")
                if os.path.exists(kuu_fail):
                    oma._loe_failist(kuu_fail, alg_aeg, lõpp_aeg)



    def _kirjuta_faili(oma, fail:str, alg_rida:int, lõpp_rida:int):
        '''
        Kirjutab Antud Ridade ElektriAndmed Antud .csv Faili.
        '''
        with open(fail, mode='w', newline='', encoding='utf-8') as csv_fail:
            csv_tabel = csv.writer(csv_fail, delimiter=',',
                                   quotechar='"', quoting=csv.QUOTE_MINIMAL)
            #PÄIS
            päis = list(oma._tabel[0].keys())
            csv_tabel.writerow(päis)
            #ANDMED
            for rida in range(alg_rida, lõpp_rida):
                csv_rida=[]
                if list(oma._tabel[rida].keys()) != päis:
                    päis = list(oma._tabel[rida].keys())
                    csv_tabel.writerow(päis)
                for väärtus in list(oma._tabel[rida].values()):
                    if isinstance(väärtus, bool):
                        csv_rida.append(oma._booleani_tõlge(väärtus))
                    else:
                        csv_rida.append(väärtus)
                csv_tabel.writerow(csv_rida)



    def hoiusta_ajavahemik(oma, kaust:str, alg_aeg:datetime, lõpp_aeg:datetime):
        '''
        Andes Ajavahemiku, Kirjutab Kõik ElektriAndmed Antud Kausta, Aasta ning Kuu Kaupa.
        '''
        alg_järg = 0
        lõpp_järg = 0
        if not os.path.exists(kaust):
            print("Ei leidnud "+kaust+"! Loon uue arhiivi kausta.")
            os.mkdir(kaust)
        for aasta in range(alg_aeg.year, lõpp_aeg.year+1):
            if not os.path.exists(kaust+"/"+str(aasta)):
                print("Lisan "+str(aasta)+" Kausta!")
                os.mkdir(kaust+"/"+str(aasta))
            if lõpp_aeg.month < alg_aeg.month:
                lõpp_kuu = 12
            else:
                lõpp_kuu = lõpp_aeg.month
            for kuu in range(alg_aeg.month, lõpp_kuu+1):
                fail = kaust+"/"+str(aasta)+"/Elektri_turuhind_"+f'{kuu:02d}'+"-"+str(aasta)+".csv"
                while lõpp_järg < len(oma._tabel) and oma._tabel[lõpp_järg]['Kuupäev'].month == kuu:
                    lõpp_järg += 1
                oma._kirjuta_faili(fail, alg_järg, lõpp_järg)
                alg_järg = lõpp_järg



    def sisaldab_andmetüüpi(oma, rida, andmetüüp):
        '''
        Kontrollib Kas Antud Andmetüüp on Olemas Oma ElektriAndmete Hulgas.
        '''
        if andmetüüp in list(oma._tabel[rida].keys()):
            return True
        else:
            return False



    def sisaldab_andmeid(oma, võrdlus_andmed, andmetüüp:str):
        '''
        Kontrollib Kas Mingi Andmetüüp Antud ElektriAndmetest on Olemas Oma ElektriAndmete Hulgas.
        '''
        if võrdlus_andmed._tabel is None:
            return False
        võrdlus_järg = 0
        for rida in oma._tabel:
            if rida["Kuupäev"] == võrdlus_andmed._tabel[võrdlus_järg]["Kuupäev"]:
                if rida[andmetüüp] != võrdlus_andmed._tabel[võrdlus_järg][andmetüüp]:
                    return False
                võrdlus_järg+=1
        if võrdlus_järg == len(võrdlus_andmed._tabel):
            return True
        else:
            return False



    def lisa_andmeid(oma, kopeeritavad_andmed):
        '''
        Lisab Andmed Antud ElektriAndmetest Oma ElektriAndmete Juurde.
        '''
        oma._rea_järg = None	#Kiirendab Andmete Uuendamist
        muudetud_väljade_hulk = 0	#Huvi/Silumise Pärast

        if kopeeritavad_andmed._tabel is None:
            return muudetud_väljade_hulk

        # Otsi Vanematest Andmetest Rida
        def _leia_rida(dubleeritav_rida:dict):
            '''
            Otsib Oma ElektriAndmetest Üles Antud Rea.
            '''
            if oma._rea_järg is None:
                oma._rea_järg = 0
            for olemas_rida in range(oma._rea_järg,len(oma._tabel)):
                if oma._tabel[olemas_rida]['Kuupäev'] == dubleeritav_rida['Kuupäev']:
                    for tulp in list(dubleeritav_rida.keys()):
                        if oma._tabel[olemas_rida][tulp]!=dubleeritav_rida[tulp]:
                            oma._tabel[olemas_rida][tulp]=dubleeritav_rida[tulp]
                            nonlocal muudetud_väljade_hulk
                            muudetud_väljade_hulk+=1
                    return olemas_rida
            return None
        
        # Iga Uue Andmerea Kohta
        for kopeeritav_rida in kopeeritavad_andmed._tabel:
            oma._rea_järg = _leia_rida(kopeeritav_rida)
            if oma._rea_järg is None:
                oma._tabel.append(kopeeritav_rida)
                muudetud_väljade_hulk+=len(kopeeritav_rida)
        return muudetud_väljade_hulk



    def _booleani_tõlge(oma, olek):
        '''
        Tõlgib Booleani Väärtuse Eesti Keelde, CSV Faili Jaoks.
        OLEK võib olla kas tõeväärtus või sõne.
        '''
        if olek == "sees":
            return True
        elif olek == "väljas":
            return False
        elif olek:
            return "sees"
        elif not olek:
            return "väljas"



    def rakenda_rea_kaupa(oma, korraga:int, algoritm, parameetrid:list=[]):
        '''
        Töötleb Kõiki ElektriAndmete Ridu, Pakkudes Ligipääsu Mitmele Reale Korraga.
        '''
        if 1+len(parameetrid) != len(signature(algoritm).parameters):
            print("VIGA: Küsitud Parameetrid "+str(list(signature(algoritm).parameters.keys()))+
                  ", Antud Parameetrid "+str(parameetrid))
            silumine = True
            return
        for rea_arv in range(len(oma._tabel)):
            if (rea_arv+korraga) < len(oma._tabel):
                algoritmi_parameetrid = [oma._tabel[rea_arv:(rea_arv+korraga)]] + parameetrid
                algoritm(*algoritmi_parameetrid)



    def rakenda_reale(oma, alg_rida:int, lõpp_rida:int, algoritm, parameetrid:list=[]):
        '''
        Töötleb ElektriAndmete Ridu Ühekaupa.
        '''
        if 1+len(parameetrid) != len(signature(algoritm).parameters):
            print("VIGA: Küsitud Parameetrid "+str(list(signature(algoritm).parameters.keys()))+
                  ", Antud Parameetrid "+str(parameetrid))
            silumine = True
            return
        for rea_arv in range(alg_rida,lõpp_rida):
            algoritmi_parameetrid = [[oma._tabel[rea_arv]]] + parameetrid
            algoritm(*algoritmi_parameetrid)



    def päevade_väikseimad(oma, andmetüüp:str, hulk):
        '''
        Otsib Päeva Kaupa Antud Andmetüübi, Antud Hulga Väikseimaid Väärtusi.
        '''
        väikseima_väärtuse_read={}
        for rea_arv in range(len(oma._tabel)):
            if not andmetüüp in oma._tabel[rea_arv].keys():
                continue
            if not oma._tabel[rea_arv]["Kuupäev"].day in list(väikseima_väärtuse_read.keys()):
                väikseima_väärtuse_read[oma._tabel[rea_arv]["Kuupäev"].day] = [rea_arv]
            # Uuenda Väikseimaid
            if len(väikseima_väärtuse_read[oma._tabel[rea_arv]["Kuupäev"].day]) == hulk:
                suurima_väärtuse_rida=väikseima_väärtuse_read[oma._tabel[rea_arv]["Kuupäev"].day][0]
                # Leia Suurim-Väikseim Väärtus
                for kandidaat in väikseima_väärtuse_read[oma._tabel[rea_arv]["Kuupäev"].day]:
                    if oma._tabel[kandidaat][andmetüüp]>oma._tabel[suurima_väärtuse_rida][andmetüüp]:
                        suurima_väärtuse_rida=kandidaat
                # Vaheta kui Suurem
                if oma._tabel[suurima_väärtuse_rida][andmetüüp] > oma._tabel[rea_arv][andmetüüp]:
                    väikseima_väärtuse_read[oma._tabel[rea_arv]["Kuupäev"].day][väikseima_väärtuse_read[oma._tabel[rea_arv]["Kuupäev"].day].index(suurima_väärtuse_rida)]=rea_arv
            # Lisa Hulk
            elif (len(väikseima_väärtuse_read[oma._tabel[rea_arv]["Kuupäev"].day]) < hulk) and (rea_arv not in väikseima_väärtuse_read[oma._tabel[rea_arv]["Kuupäev"].day]):
                väikseima_väärtuse_read[oma._tabel[rea_arv]["Kuupäev"].day].append(rea_arv)
        return väikseima_väärtuse_read



    def väärtus_ajal(oma, kuupäev:datetime, andmetüüp:str):
        '''
        Annab Kuupäeva Järgi Antud Andmetüübi Väärtuse.
        '''
        #Paku Asukohta (Kiire):
        ajavahe = kuupäev-oma._tabel[0]["Kuupäev"]
        võimalik_järg = (ajavahe.days * 24 + ajavahe.seconds // 3600)-1
        if võimalik_järg < len(oma._tabel):
            if oma._tabel[võimalik_järg]["Kuupäev"] == kuupäev:
                return oma._tabel[võimalik_järg][andmetüüp]
        #Otsi Asukohta (Aeglane):
        for rida in oma._tabel:
            if rida["Kuupäev"] == kuupäev:
                if andmetüüp in list(rida.keys()):
                    return rida[andmetüüp]
                else:
                    print("VIGA: Antud Ajal ("+kuupäev.strftime("%H:%M - %d.%m.%Y")+") "+andmetüüp+" Väärtust Ei Leitud!")
                    silumine = True
                    return None



    def väärtus_real(oma, rida:int, andmetüüp:str):
        '''
        Annab Rea Järgi Antud Andmetüübi Väärtuse.
        '''
        if rida < len(oma._tabel):
            väärtus = oma._tabel[rida][andmetüüp]
        else:
            väärtus = None
        return väärtus





####################################################################################################
#    ELEKTRIANDMETE ANALÜÜSI ALGORITMID                                                            #
####################################################################################################
def välja_uuendamine(read, andmetüüp:str, väärtus):
    '''
    Määrab Üksiku ElektriAndmed Välja Antud Väärtuseks.
    '''
    read[0][andmetüüp]=väärtus



def välja_kustutamine(read, andmetüüp:str):
    '''
    Üksiku Välja Eemaldamine Elektriandmetest.
    '''
    for tulp in list(read[0].keys()):
        if andmetüüp in tulp:
            read[0].pop(tulp)



def välja_lisamine_keskmine(read):
    '''
    Arvutab Jooksva Keskmise Hinna Järgnevate Tundidega.
    '''
    keskmine_hind = 0
    for aeg in read:
        keskmine_hind += aeg["Hind"]
    read[0]["Jooksev "+str(len(read))+". Tunni Keskmine"]=keskmine_hind/len(read)



def välja_uuendamine_teravikul(read, andmetüüp:str, väärtus, teraviku_kõrgus:int):
    '''
    Otsib Millal Hind Tõuseb Järsult Hetkeks!
    TERAVIKUKÕRGUS on €/MWh, tähistab millal elekter välja lülitada.
    '''
    if (read[0]["Hind"]+teraviku_kõrgus) < read[1]["Hind"]:
        print("Järsk Hinnatõus kell",
              read[1]["Kuupäev"].strftime("%H:%M (%d.%m.%Y) -"),
              str(round(maksusta_hind(read[0]["Hind"]),2))+"¢/kWh ->",
              str(round(maksusta_hind(read[1]["Hind"]),2))+"¢/kWh!")
        for teraviku_lõpp in range(2, len(read)):
            if (read[1]["Hind"]-teraviku_kõrgus) > (read[teraviku_lõpp]["Hind"]):
                print(str(teraviku_lõpp-1)+" tunniks, Lülitan Elektri Välja")
                #-Nimi-
                if väärtus:
                    ürituse_nimi = andmetüüp.split('-')[1]+" Sees"
                else:
                    ürituse_nimi = andmetüüp.split('-')[1]+" Väljas"
                #-Nimi-
                #-Kirjeldus-
                keskmine_hind=0
                for teraviku_rida in range(1,teraviku_lõpp):
                    keskmine_hind+=read[teraviku_rida]["Hind"]
                keskmine_hind=keskmine_hind/(teraviku_lõpp-1)
                ürituse_kirjeldus=("📈 Järsk Hinnatõus!\n")
                if read[0] != 0:
                    ürituse_kirjeldus+=("("+str(round((keskmine_hind-read[0]["Hind"])/read[0]["Hind"]*100, 0))+"%) ")
                ürituse_kirjeldus+=(str(round(maksusta_hind(keskmine_hind-read[0]["Hind"]),2))+"¢/kWh kallim "
                                   +str(teraviku_lõpp-1)+". tunniks.\n-----------------------------------")
                ürituse_kirjeldus+=("\n"+read[0]["Kuupäev"].strftime("%H:%M ⚡ ")
                                    +str(round(maksusta_hind(read[0]["Hind"]), 2))
                                    +"¢/kWh")
                for tund in range(1,teraviku_lõpp):
                    ürituse_kirjeldus+=("\n"+read[tund]["Kuupäev"].strftime("%H:%M 🚫 ")
                                    +str(round(maksusta_hind(read[tund]["Hind"]), 2))
                                    +"¢/kWh")
                ürituse_kirjeldus+=("\n"+read[teraviku_lõpp]["Kuupäev"].strftime("%H:%M ⚡ ")
                                    +str(round(maksusta_hind(read[teraviku_lõpp]["Hind"]), 2))
                                    +"¢/kWh")
                #-Kirjeldus-
                if not GoogleKalender.üritus_olemas(read[1]["Kuupäev"],read[teraviku_lõpp]["Kuupäev"],andmetüüp,ürituse_nimi):
                    GoogleKalender.loo_üritus(read[1]["Kuupäev"],read[teraviku_lõpp]["Kuupäev"],andmetüüp,väärtus,ürituse_kirjeldus,ürituse_nimi)
                else:
                    silumine = True
                for teraviku_väli in range(1, teraviku_lõpp):
                    read[teraviku_väli][andmetüüp]=väärtus
                break



def välja_uuendamine_enne_langust(read, andmetüüp:str, väärtus, teraviku_kõrgus:int):
    '''
    Otsib Hetke Enne Järsku Hinnalangustz!
    TERAVIKUKÕRGUS on €/MWh, tähistab millal elekter välja lülitada.
    '''
    if (read[-1]["Hind"]+teraviku_kõrgus) < read[-2]["Hind"]:
        print("Järsk Hinnalangus kell",
              read[-1]["Kuupäev"].strftime("%H:%M (%d.%m.%Y) -"),
              str(round(maksusta_hind(read[-2]["Hind"]),2))+"¢/kWh ->",
              str(round(maksusta_hind(read[-1]["Hind"]),2))+"¢/kWh!")
        esimene_tund=len(read)-2
        for kõrge_hinna_rida in range(len(read)-2,1,-1):
            if kõrge_hinna_rida == 1:
                esimene_tund=1
            if (read[-1]["Hind"]+teraviku_kõrgus) > (read[kõrge_hinna_rida]["Hind"]):
                esimene_tund=kõrge_hinna_rida+1
        print("Lülitan Elektri Välja "+str(len(read)-esimene_tund)+". eelnevaks tunniks!")
        #-Nimi-
        if väärtus:
            ürituse_nimi = andmetüüp.split('-')[1]+" Sees"
        else:
            ürituse_nimi = andmetüüp.split('-')[1]+" Väljas"
        #-Nimi-
        #-Kirjeldus-
        keskmine_hind=0
        for kallim_rida in range(esimene_tund,len(read)-1):
            keskmine_hind+=read[kallim_rida]["Hind"]
        keskmine_hind=keskmine_hind/(len(read)-1-esimene_tund)
        ürituse_kirjeldus=("📉 Järsk Hinnalangus!\n")
        if read[-1] != 0:
            ürituse_kirjeldus+=("("+str(round((keskmine_hind-read[-1]["Hind"])/read[-1]["Hind"]*100, 0))+"%) ")
        ürituse_kirjeldus+=(str(round(maksusta_hind(keskmine_hind-read[-1]["Hind"]),2))
                            +"¢/kWh soodsam \n-----------------------------------")
        ürituse_kirjeldus+=("\n"+read[0]["Kuupäev"].strftime("%H:%M ⚡ ")
                            +str(round(maksusta_hind(read[0]["Hind"]), 2))
                            +"¢/kWh")
        for tund in range(esimene_tund,len(read)-1):
            ürituse_kirjeldus+=("\n"+read[tund]["Kuupäev"].strftime("%H:%M 🚫 ")
                                +str(round(maksusta_hind(read[tund]["Hind"]), 2))
                                +"¢/kWh")
        ürituse_kirjeldus+=("\n"+read[-1]["Kuupäev"].strftime("%H:%M ⚡ ")
                            +str(round(maksusta_hind(read[-1]["Hind"]), 2))
                            +"¢/kWh")
        #-Kirjeldus-
        if not GoogleKalender.üritus_olemas(read[esimene_tund]["Kuupäev"],read[-1]["Kuupäev"],andmetüüp,ürituse_nimi):
            GoogleKalender.loo_üritus(read[esimene_tund]["Kuupäev"],read[-1]["Kuupäev"],andmetüüp,väärtus,ürituse_kirjeldus,ürituse_nimi)
        else:
            silumine = True
        for kallim_väli in range(esimene_tund, len(read)-1):
            read[kallim_väli][andmetüüp]=väärtus





####################################################################################################
#    STATISTIKA TUGIFUNKTSIOONID                                                                   #
####################################################################################################
def maksusta_hind(börsihind):
    '''
    Teisendab API Börsihinna Inimloetavasse 
    '''
    tarbijaHind = float(börsihind)/10		#Konverteerin €/MWh -> ¢/kWh
    tarbijaHind = float(tarbijaHind)*1.22	#Lisan Käibemaksu
    return tarbijaHind





####################################################################################################
#    VÄLISED FUNKTSIOONID                                                                          #
####################################################################################################
def uued_hinnad(alg_aeg:datetime, lõpp_aeg:datetime):
    '''
    Kontrollib ja Salvestab Uued Elektri Hinnad kui Saadaval.
    '''
    laetud_graafik = ElektriAndmed()
    salvestatud_graafik = ElektriAndmed()
    laetud_graafik.loe_võrgust(alg_aeg, lõpp_aeg)
    print("Allalaetud Hinnad:\n"+str(laetud_graafik))
    salvestatud_graafik.loe_ajavahemik(ANDMEKAUST, alg_aeg, lõpp_aeg)
    print("Loetud Hinnad:\n"+str(salvestatud_graafik))
    if not salvestatud_graafik.sisaldab_andmeid(laetud_graafik, "Hind"):
        print(salvestatud_graafik.lisa_andmeid(laetud_graafik),"Välja Uuendatud!")
        salvestatud_graafik.hoiusta_ajavahemik(ANDMEKAUST, alg_aeg, lõpp_aeg)
        print("Salvestatud Hinnad:\n"+str(salvestatud_graafik))
        return True
    else:
        print("Uuemaid Andmeid Polnud Saadaval!")
        return False



def lülita_alati(seade:str, lüliti_asend:bool):
    '''
    Lülitab Antud Seadme Lüliti, Antud Asendisse, Terve Graafiku Ajaks.
    '''
    tund = datetime.now(tz=tz.gettz('Europe/Tallinn'))
    tund = (tund
            -timedelta(minutes=tund.minute)
            -timedelta(seconds=tund.second)
            -timedelta(microseconds=tund.microsecond))
    salvestatud_graafik = ElektriAndmed()
    salvestatud_graafik.loe_ajavahemik(ANDMEKAUST, tund, tund+timedelta(days=1))
    salvestatud_graafik.rakenda_rea_kaupa(1, välja_uuendamine, [seade, lüliti_asend])
    salvestatud_graafik.hoiusta_ajavahemik(ANDMEKAUST, tund, tund+timedelta(days=1))



def lülita_soodsaimal_järjestikku(seade:str, lüliti_asend:bool, kestus:int):
    '''
    Lülitab Antud Seadme Lüliti, Antud Asendisse, Iga Päeva Soodsaimal Ajal, Antud Kestuseks.
    '''
    tund = datetime.now(tz=tz.gettz('Europe/Tallinn'))
    tund = (tund
            -timedelta(minutes=tund.minute)
            -timedelta(seconds=tund.second)
            -timedelta(microseconds=tund.microsecond))
    salvestatud_graafik = ElektriAndmed()
    salvestatud_graafik.loe_ajavahemik(ANDMEKAUST, tund, tund+timedelta(days=1))

	#Lisa keskmised hinnad.
    salvestatud_graafik.rakenda_rea_kaupa(kestus, välja_lisamine_keskmine)
    keskmise_tulp = "Jooksev "+str(kestus)+". Tunni Keskmine"
    #Lülita soodsaimatel hindadel seade asendisse.
    soodsaimad_perioodid = salvestatud_graafik.päevade_väikseimad(keskmise_tulp, 1)
    for päeva_soodsaim_rida in [rida for päev in list(soodsaimad_perioodid.values()) for rida in päev]:
        if not salvestatud_graafik.sisaldab_andmetüüpi(päeva_soodsaim_rida, keskmise_tulp):
            continue
        #-Nimi-
        if lüliti_asend:
            ürituse_nimi = seade.split('-')[1]+" Sees"
        else:
            ürituse_nimi = seade.split('-')[1]+" Väljas"
        #-Nimi-
        #-Kirjeldus-
        ürituse_kirjeldus = ("💡 Päeva Soodsaim Elekter!\n"
                            +str(kestus)+". tunni keskmine hind: "
                            +str(round(maksusta_hind(salvestatud_graafik.väärtus_real(päeva_soodsaim_rida,keskmise_tulp)), 2))
                            +"¢/kWh.\n-----------------------------------")
        ürituse_kirjeldus+=("\n"+salvestatud_graafik.väärtus_real(päeva_soodsaim_rida-1,"Kuupäev").strftime("%H:%M 🚫 ")
                +str(round(maksusta_hind(salvestatud_graafik.väärtus_real(päeva_soodsaim_rida-1,"Hind")), 2))
                +"¢/kWh")
        for soodsaim_tund in range(0,kestus):
            ürituse_kirjeldus+=("\n"+salvestatud_graafik.väärtus_real(päeva_soodsaim_rida+soodsaim_tund,"Kuupäev").strftime("%H:%M ⚡ ")
                +str(round(maksusta_hind(salvestatud_graafik.väärtus_real(päeva_soodsaim_rida+soodsaim_tund,"Hind")), 2))
                +"¢/kWh")
        ürituse_kirjeldus+=("\n"+salvestatud_graafik.väärtus_real(päeva_soodsaim_rida+kestus,"Kuupäev").strftime("%H:%M 🚫 ")
                +str(round(maksusta_hind(salvestatud_graafik.väärtus_real(päeva_soodsaim_rida+kestus,"Hind")), 2))
                +"¢/kWh")
        #-Kirjeldus-
        if not GoogleKalender.üritus_olemas(salvestatud_graafik.väärtus_real(päeva_soodsaim_rida,"Kuupäev"),
                                  salvestatud_graafik.väärtus_real(päeva_soodsaim_rida+kestus,"Kuupäev"),
                                  seade,ürituse_nimi):
            GoogleKalender.loo_üritus(salvestatud_graafik.väärtus_real(päeva_soodsaim_rida,"Kuupäev"),
                                  salvestatud_graafik.väärtus_real(päeva_soodsaim_rida+kestus,"Kuupäev"),
                                  seade, lüliti_asend, ürituse_kirjeldus,ürituse_nimi)
        else:
            silumine = True
        salvestatud_graafik.rakenda_reale(päeva_soodsaim_rida, päeva_soodsaim_rida+kestus,
                                          välja_uuendamine, [seade, lüliti_asend])
    #Kustuta keskmised hinnad:
    salvestatud_graafik.rakenda_rea_kaupa(1, välja_kustutamine, [keskmise_tulp])

    salvestatud_graafik.hoiusta_ajavahemik(ANDMEKAUST, tund, tund+timedelta(days=1))



def lülita_soodsaimal_katkendlikku(seade:str, lüliti_asend:bool, kestus:int):
    '''
    Lülitab Antud Seadme Lüliti, Antud Asendisse, Iga Päeva Soodsaimatel Aegadel, Antud Kestuseks.
    '''
    tund = datetime.now(tz=tz.gettz('Europe/Tallinn'))
    tund = (tund
            -timedelta(minutes=tund.minute)
            -timedelta(seconds=tund.second)
            -timedelta(microseconds=tund.microsecond))
    salvestatud_graafik = ElektriAndmed()
    salvestatud_graafik.loe_ajavahemik(ANDMEKAUST, tund, tund+timedelta(days=1))

	#Lülita soodsaimatel hindadel seade asendisse.
    soodsaimad_perioodid = salvestatud_graafik.päevade_väikseimad("Hind", kestus)
    keskmised_hinnad = {}
    for päev in list(soodsaimad_perioodid.keys()):
        keskmised_hinnad[päev]=maksusta_hind(sum(salvestatud_graafik.väärtus_real(rida,"Hind") for rida in soodsaimad_perioodid[päev])/len(soodsaimad_perioodid[päev]))
    soodsaimad_perioodid = [rida for päev in list(soodsaimad_perioodid.values()) for rida in päev]
    soodsaimad_perioodid.sort()
    üritused = []
    algus = soodsaimad_perioodid[0]
    kestvus = 1
    for i in range(1, len(soodsaimad_perioodid)):
        if soodsaimad_perioodid[i] == soodsaimad_perioodid[i - 1] + 1:
            kestvus += 1
        else:
            üritused.append([algus, kestvus])
            algus = soodsaimad_perioodid[i]
            kestvus = 1
    üritused.append([algus, kestvus])
    for üritus in üritused:
        #-Nimi-
        if lüliti_asend:
            ürituse_nimi = seade.split('-')[1]+" Sees"
        else:
            ürituse_nimi = seade.split('-')[1]+" Väljas"
        #-Nimi-
        #-Kirjeldus-
        ürituse_kirjeldus = ("💡 Soodne Elekter!\n"
                            +str(kestus)+". tunni keskmine hind: "
                            +str(round(keskmised_hinnad[salvestatud_graafik.väärtus_real(üritus[0],"Kuupäev").day], 2))
                            +"¢/kWh.\n-----------------------------------")
        ürituse_kirjeldus+=("\n"+salvestatud_graafik.väärtus_real(üritus[0]-1,"Kuupäev").strftime("%H:%M 🚫 ")
                +str(round(maksusta_hind(salvestatud_graafik.väärtus_real(üritus[0]-1,"Hind")), 2))
                +"¢/kWh")
        for soodne_tund in range(0,üritus[1]):
            ürituse_kirjeldus+=("\n"+salvestatud_graafik.väärtus_real(üritus[0]+soodne_tund,"Kuupäev").strftime("%H:%M ⚡ ")
                +str(round(maksusta_hind(salvestatud_graafik.väärtus_real(üritus[0]+soodne_tund,"Hind")), 2))
                +"¢/kWh")
        if salvestatud_graafik.väärtus_real(üritus[0]+üritus[1],"Kuupäev") != None:
            ürituse_kirjeldus+=("\n"+salvestatud_graafik.väärtus_real(üritus[0]+üritus[1],"Kuupäev").strftime("%H:%M 🚫 ")
                +str(round(maksusta_hind(salvestatud_graafik.väärtus_real(üritus[0]+üritus[1],"Hind")), 2))
                +"¢/kWh")
        #-Kirjeldus-
        if not GoogleKalender.üritus_olemas(salvestatud_graafik.väärtus_real(üritus[0],"Kuupäev"),
                                  salvestatud_graafik.väärtus_real(üritus[0],"Kuupäev")+timedelta(hours=üritus[1]),
                                  seade,ürituse_nimi):
            GoogleKalender.loo_üritus(salvestatud_graafik.väärtus_real(üritus[0],"Kuupäev"),
                                  salvestatud_graafik.väärtus_real(üritus[0],"Kuupäev")+timedelta(hours=üritus[1]),
                                  seade, lüliti_asend, ürituse_kirjeldus,ürituse_nimi)
        else:
            silumine = True
        salvestatud_graafik.rakenda_reale(üritus[0], üritus[0]+üritus[1],
                                          välja_uuendamine, [seade, lüliti_asend])

    salvestatud_graafik.hoiusta_ajavahemik(ANDMEKAUST, tund, tund+timedelta(days=1))



def lülita_teravikul(seade:str, lüliti_asend:bool, kestus:int):
    '''
    Lülitab Antud Seadme Lüliti, Antud Asendisse
    Kui Järsk Hinna Tõus Jääb Antud Kestuvusega Samasse Suurusjärku.
    '''
    tund = datetime.now(tz=tz.gettz('Europe/Tallinn'))
    tund = (tund
            -timedelta(minutes=tund.minute)
            -timedelta(seconds=tund.second)
            -timedelta(microseconds=tund.microsecond))
    salvestatud_graafik = ElektriAndmed()
    salvestatud_graafik.loe_ajavahemik(ANDMEKAUST, tund, tund+timedelta(days=1))
    salvestatud_graafik.rakenda_rea_kaupa(kestus+2,
                                          välja_uuendamine_teravikul, [seade, lüliti_asend, 30])
    salvestatud_graafik.hoiusta_ajavahemik(ANDMEKAUST, tund, tund+timedelta(days=1))



def lülita_enne_langust(seade:str, lüliti_asend:bool, kestus:int):
    '''
    Lülitab Antud Seadme Lüliti, Antud Asendisse
    Antud Kestuvuseks Enne Hinnalangust.
    '''
    tund = datetime.now(tz=tz.gettz('Europe/Tallinn'))
    tund = (tund
            -timedelta(minutes=tund.minute)
            -timedelta(seconds=tund.second)
            -timedelta(microseconds=tund.microsecond))
    salvestatud_graafik = ElektriAndmed()
    salvestatud_graafik.loe_ajavahemik(ANDMEKAUST, tund, tund+timedelta(days=1))
    salvestatud_graafik.rakenda_rea_kaupa(kestus+2,
                                          välja_uuendamine_enne_langust, [seade, lüliti_asend, 50])
    salvestatud_graafik.hoiusta_ajavahemik(ANDMEKAUST, tund, tund+timedelta(days=1))



def soodne_hetk(seade:str):
    '''
    Vastab Kas Hinnagraafiku Kohaselt Peaks Antud Seade Sees Olema.
    '''
    tund = datetime.now(tz=tz.gettz('Europe/Tallinn'))
    tund = (tund
            -timedelta(minutes=tund.minute)
            -timedelta(seconds=tund.second)
            -timedelta(microseconds=tund.microsecond))
    salvestatud_graafik = ElektriAndmed()
    salvestatud_graafik.loe_ajavahemik(ANDMEKAUST, tund, tund+timedelta(days=1))
    # Kui Väärtus Puudub Antud Ajal, Lülita Sisse.
    if salvestatud_graafik.väärtus_ajal(tund, seade)==True or salvestatud_graafik.väärtus_ajal(tund, seade)==None:
        return True
    else:
        return False





####################################################################################################
#    PÕHI KOOD                                                                                     #
####################################################################################################
if __name__ == '__main__':
    '''
    # TESTIMISEKS:
    AKUDEMAHT = 1 #Kauaks elektri võib välja lülitada
    algAeg = (datetime.now(tz=tz.gettz('Europe/Tallinn'))
    -timedelta(hours=AKUDEMAHT+1)) #lahutame kaks tundi, et hetke hinnamuutust näha
    lõppAeg = algAeg+timedelta(days=2)
    uuedHinnad(algAeg, lõppAeg)
    lülitaAlati("Garderoob-Radiaator",False)
    lülitaSoodsaimal("Paul-Radiaator",True,2)
    lülitaTeravikul("Magamis-Radiaator",False,2)
    '''
