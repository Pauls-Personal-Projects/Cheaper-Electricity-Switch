#!/usr/bin/env python3
# -*- coding: utf-8 -*-

####################################################################################################
#                                                                                                  #
#                                            LÜLITI                                                #
#                                                                                                  #
####################################################################################################
'''
Looja:		Paul J. Aru        -    https://github.com/paulpall
Kuupäev:	21/09/2022
Uuendatud:	15/10/2022
------------------------------------------------------------
Tänud	Andrew Sayre, pysmartthings teegi loomise eest
Link: https://github.com/andrewsayre/pysmartthings
ja		Grant Lemons, light-control näite loomise eest
Link: https://github.com/grantlemons/light-control
'''



####################################################################################################
#    TEEGID                                                                                        #
####################################################################################################
import aiohttp										# SmartThings APIga Ühendumiseks
import pysmartthings								# SmartThings APIga Ühendumiseks
import asyncio										# SmartThings APIga Ühendumiseks
import os.path										# Failide Salvestamiseks ja Lugemiseks
import csv											# Failide Salvestamiseks ja Lugemiseks
from datetime import datetime, timezone, timedelta	# API Kellaaja konverteerimiseks
from dateutil import tz, parser						# API Kellaaja konverteerimiseks
import dateutil										# API Kellaaja konverteerimiseks
import time											# Sleepi jaoks mida lülitite kontrollil läheb vaja
import sys											# Veateate Edastamiseks Synology DSM'ile





####################################################################################################
#    SÄTTED                                                                                        #
####################################################################################################
### PEIDA ENNE GIT'i LAADIMIST ###
SmartThingsi_Ligipääsu_Token = ''
### PEIDA ENNE GIT'i LAADIMIST ###
jooksevFail = "Elektri_Jooksev_Kasutus.csv" # IDE Kaust
graafikuteKaust = "Graafikud" # IDE Kaust
#jooksevFail = "/volume1/homes/Paul/Drive/Ajutine/Elektri_Jooksev_Kasutus.csv" # Pilve Kaust
#graafikuteKaust = "/volume1/Failid/Elektri Kasutus Graafikud" # Pilve Kaust
silumine = True





####################################################################################################
#	TUGIFUNKTSIOONID																			   #
####################################################################################################
def eestiKeelesBoolean(olek):
	if olek:
		return "sees"
	else:
		return "väljas"



def loeHinnaGraafikut(failiNimi,seadmeNimi):
	if os.path.exists(failiNimi):
		with open(failiNimi, mode='r', encoding='utf-8') as elektriHinnaFail:
			csvFail = list(csv.reader(elektriHinnaFail))
		praeguneAeg = datetime.now(tz=tz.gettz('Europe/Tallinn'))
		#print("Elektrihinnad on saadaval kuni kella "+parser.parse(csvFail[-1][0]).strftime("%H:%M (%d.%m.%Y)"))
		kuupäevaTulp=0
		hinnaTulp=0
		päis=[]
		for näit in csvFail:
			if näit == csvFail[0]:
				päis = näit
				for tulp in range(len(päis)):
					if päis[tulp] == "Kuupäev":
						kuupäevaTulp=tulp
					elif päis[tulp] == "Hind":
						hinnaTulp=tulp
			else:
				if parser.parse(näit[kuupäevaTulp]).year == praeguneAeg.year and parser.parse(näit[kuupäevaTulp]).month == praeguneAeg.month and parser.parse(näit[kuupäevaTulp]).day == praeguneAeg.day and parser.parse(näit[kuupäevaTulp]).hour == praeguneAeg.hour:
					for seade in range(len(päis)):
						if päis[seade] == seadmeNimi:
							print("Elektrihinna Graafik: "+parser.parse(näit[kuupäevaTulp]).strftime("%d.%m.%Y kella %H:%Mst on elektrihind ")+näit[hinnaTulp]+"€/MWh ja elekter peaks "+näit[seade]+" olema!")
							if näit[seade] == "sees":
								return True
							elif näit[seade] == "väljas":
								return False
							else:
								print("Ei Tuvastanud Olekut!")
								silumine = True
								return True
	else:
		print("Ei Leidnud Elektrihinna Graafikut! ("+failiNimi+")")
		silumine = True
		return True



def loeNädalapäevaGraafikut(kaust,seadmeNimi):
	graafikuAsukoht = kaust+"/"+seadmeNimi+".graafik"
	if os.path.exists(graafikuAsukoht):
		with open(graafikuAsukoht, mode='r', encoding='utf-8') as elektriNädalaFail:
			csvFail = list(csv.reader(elektriNädalaFail, delimiter='|'))
		praeguneAeg = datetime.now(tz=tz.gettz('Europe/Tallinn'))
		if len(csvFail) == 25 and len(csvFail[-1]) == 8 and csvFail[0][0].strip() == "Tund" and dateutil.parser.parse(csvFail[praeguneAeg.hour+1][0]).hour == praeguneAeg.hour:
			if csvFail[praeguneAeg.hour+1][praeguneAeg.weekday()+1].strip() == "⚡️":
				print("Nädalapäeva Graafik: "+csvFail[0][praeguneAeg.weekday()+1].strip()+" kella "+csvFail[praeguneAeg.hour+1][0].strip()+"st peaks elekter sees olema!")
				return True
			elif csvFail[praeguneAeg.hour+1][praeguneAeg.weekday()+1].strip() == "❌️":
				print("Nädalapäeva Graafik: "+csvFail[0][praeguneAeg.weekday()+1].strip()+" kella "+csvFail[praeguneAeg.hour+1][0].strip()+"st peaks elekter väljas olema!")
				return False
			else:
				print("Nädalapäeva Graafik: Ei suutnud tuvastada mis ("+csvFail[praeguneAeg.hour+1][praeguneAeg.weekday()+1].strip()+") tähendab "+csvFail[0][praeguneAeg.weekday()+1].strip()+" kell "+csvFail[praeguneAeg.hour+1][0].strip())
				silumine = True
				return True
		else:
			print("Leidsin "+graafikuAsukoht+" faili, kuid formaat tundub vale!")
			silumine = True
			return True
	else:
		print("Ei Leidnud Nädalapäeva Graafikut! ("+graafikuAsukoht+")")
		silumine = True
		return True


async def loetleAsukohad(rakendusliides):
	asukohad = await rakendusliides.locations()
	for asukoht in asukohad:
		print("Leidsin "+str(len(asukohad))+". Asukoha: "+asukoht.name)



async def loetleSeadmed(rakendusliides):
	seadmed = await rakendusliides.devices()
	print("* * * * * * * * * * * * * * * * * * * * * * * * * ")
	print(str(len(seadmed))+" Seade(t)")
	for seade in seadmed:
		print("- - - - - - - - - - - - - - - - - - - - - - - - - ")
		await seade.status.refresh()
		print("Nimi: "+seade.label)
		print("Enne Elekter: "+eestiKeelesBoolean(seade.status.switch)+" ("+str(seade.status.switch)+")")
		#print(f'Võimed: {seade.capabilities}')
		if loeHinnaGraafikut(jooksevFail,seade.label) and loeNädalapäevaGraafikut(graafikuteKaust,seade.label):
			print("Lülitan Sisse!")
			await seade.switch_on()
		else:
			print("Lülitan Välja!")
			await seade.switch_off()
		#time.sleep(3)
		#print("Nüüd Elekter "+eestiKeelesBoolean(seade.status.switch)+". ("+str(seade.status.switch)+")")



async def ühendaSmartThingsi():
	async with aiohttp.ClientSession() as session:
		api = pysmartthings.SmartThings(session, SmartThingsi_Ligipääsu_Token)
		await loetleAsukohad(api)
		await loetleSeadmed(api)





####################################################################################################
#	PÕHI KOOD																					   #
####################################################################################################
if __name__ == "__main__":
	print("\nTere Tulemast Lülitajasse\n")
	print("--------------------------------------------------")
	print("LÜLITITELE VAJUTAMINE")
	print("--------------------------------------------------")
	loop = asyncio.get_event_loop()
	loop.run_until_complete(ühendaSmartThingsi())
	print("--------------------------------------------------")
	if silumine:
		sys.exit(1)
