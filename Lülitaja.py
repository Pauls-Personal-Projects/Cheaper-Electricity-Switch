#!/usr/bin/env python3
# -*- coding: utf-8 -*-

####################################################################################################
#                                                                                                  #
#                                            LÜLITI                                                #
#                                                                                                  #
####################################################################################################
'''
Looja:      Paul J. Aru - https://github.com/paulpall
Kuupäev:    21/09/2022
Uuendatud:  20/05/2023
------------------------------------------------------------
Tänud    Andrew Sayre, pysmartthings teegi loomise eest
Link: https://github.com/andrewsayre/pysmartthings
ja        Grant Lemons, light-control näite loomise eest
Link: https://github.com/grantlemons/light-control
'''





####################################################################################################
#    TEEGID                                                                                        #
####################################################################################################
import os.path                           # Failide Salvestamiseks ja Lugemiseks.
import csv                               # Failide Salvestamiseks ja Lugemiseks.
import asyncio                           # SmartThings APIga Ühendumiseks.
import sys                               # Synology DSM Veateated  / Teiste Kaustade Teekid.
from datetime import datetime, timedelta # API Kellaaja konverteerimiseks.
from dateutil import tz                  # API Kellaaja konverteerimiseks.
import aiohttp                           # SmartThings APIga Ühendumiseks.
import pysmartthings                     # SmartThings APIga Ühendumiseks.
#sys.path.append("Võtmed") #IDE Kaust
sys.path.append("/volume1/homes/Paul/Drive/Projektid/Elektrihind/Võtmed") #Pilve Kaust
import SmartThings                       # SmartThings API Võti.
import ElektriHindaja
import GoogleKalender





####################################################################################################
#    SÄTTED                                                                                        #
####################################################################################################
#REEGLITE_FAILI_ASUKOHT = "Seadmed.reeglid"  #IDE Kaust
REEGLITE_FAILI_ASUKOHT = "/volume1/homes/Paul/Drive/Projektid/Elektrihind/Seadmed.reeglid" #Pilve Kaust
silumine = False





####################################################################################################
#    TUGIFUNKTSIOONID                                                                              #
####################################################################################################
def _loe_reegleid(asukoht:str):
    '''
	Loeb omaloodud .reeglid faili sisse; mis juhendab milliseid algoritme,
    millises järjekorras, milliste seadmete jaoks jooksutada.
	'''
    juhendid = {}
    if os.path.exists(asukoht):
        with open(asukoht, mode='r', encoding='utf-8') as reeglite_fail:
            reeglid = list(csv.reader(reeglite_fail, delimiter=','))
            for seade in reeglid:
                juhendid[seade[0]]=seade[1:]
    else:
        print("VIGA: Ei Leidnud Seadmete Reegleid Asukohast: ("+asukoht+")")
        global silumine
        silumine = True
    return juhendid



def _reegel_algoritmi(seadme_nimi:str, reeglitest_juhis:str):
    '''
	Tõlgendab ja suunab omaloodud .reeglite faili juhiseid
    ElektriHindaja funktsioonidesse.
	'''
    puhastatud_juhis = reeglitest_juhis.strip().lower()
    kestvus = 0
    if puhastatud_juhis[1] != 't':
        kestvus=int(puhastatud_juhis[0])*10+int(puhastatud_juhis[1])
    else:
        kestvus=int(puhastatud_juhis[0])

    lüliti_asend = True
    if "väljas" in puhastatud_juhis:
        lüliti_asend = False

    if "alati" in puhastatud_juhis:
        ElektriHindaja.lülita_alati(seadme_nimi, lüliti_asend)
    elif "soodsaim" in puhastatud_juhis:
        ElektriHindaja.lülita_soodsaimal(seadme_nimi, lüliti_asend, kestvus)
    elif "hinna_teravikudel" in puhastatud_juhis:
        ElektriHindaja.lülita_teravikul(seadme_nimi, lüliti_asend, kestvus)
    else:
        print("VIGA: Ei oska suunata juhist ("+reeglitest_juhis+")")
        global silumine
        silumine = True





####################################################################################################
#    PÕHI KOOD                                                                                     #
####################################################################################################
async def _pea_ülesanne():
    '''
	1. Ühendab SmartThings APIga.
    2. Kontrollib Kas Elektrihinnad ja Nendel Põhinevad Juhised on Ajakohased.
    3. Lülitab Juhiste ja Graafiku Põhjal Seadmed Õigesse Asendisse.
	'''
    seadmete_reeglid = _loe_reegleid(REEGLITE_FAILI_ASUKOHT)
    alg_aeg = datetime.now(tz=tz.gettz('Europe/Tallinn'))-timedelta(hours=2)
    #lahutame kaks tundi, et hetke hinnamuutust näha
    lõpp_aeg = alg_aeg+timedelta(days=2)
    if ElektriHindaja.uued_hinnad(alg_aeg, lõpp_aeg):
        for seade in list(seadmete_reeglid.keys()):
            print("\n"+seade+" Juhiste Uuendamine:")
            for reegel in seadmete_reeglid[seade]:
                _reegel_algoritmi(seade, reegel)
    async with aiohttp.ClientSession() as ühendus:
        api = pysmartthings.SmartThings(ühendus, SmartThings.Ligipääsu_Token)
        asukohad = await api.locations()
        for asukoht in asukohad:
            print("Leidsin "+str(len(asukohad))+". Asukoha: "+asukoht.name)
            nutipistikud = await api.devices()
            for nutipistik in nutipistikud:
                await nutipistik.status.refresh()
                if (ElektriHindaja.soodne_hetk(nutipistik.label) and
                    GoogleKalender.kasutus_hetk(nutipistik.label)):
                    print("Lülitan", nutipistik.label,"Sisse!")
                    await nutipistik.switch_on()
                else:
                    print("Lülitan", nutipistik.label,"Välja!")
                    await nutipistik.switch_off()




if __name__ == "__main__":
    print("\nTere Tulemast Lülitajasse\n")
    print("--------------------------------------------------")
    print("LÜLITITELE VAJUTAMINE")
    print("--------------------------------------------------")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_pea_ülesanne())
    print("--------------------------------------------------")
    if silumine:
        sys.exit(1)
