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
import aiohttp										#SmartThings APIga Ühendumiseks
import pysmartthings								#SmartThings APIga Ühendumiseks
import asyncio										#SmartThings APIga Ühendumiseks
import os.path										# Failide Salvestamiseks ja Lugemiseks
import csv											# Failide Salvestamiseks ja Lugemiseks
from datetime import datetime, timezone, timedelta	# API Kellaaja konverteerimiseks
from dateutil import tz, parser						# API Kellaaja konverteerimiseks
import dateutil										# API Kellaaja konverteerimiseks





####################################################################################################
#    SÄTTED                                                                                        #
####################################################################################################
### PEIDA ENNE GIT'i LAADIMIST ###
SmartThingsi_Ligipääsu_Token = ''
### PEIDA ENNE GIT'i LAADIMIST ###
jooksevFail = "Elektri_Jooksev_Kasutus.csv"
graafikuteKaust = "Graafikud"





####################################################################################################
#	TUGIFUNKTSIOONID																			   #
####################################################################################################
def eestiKeelesString(olek):
	if olek == "True":
		return "sees"
	else:
		return "väljas"



def eestiKeelesBoolean(olek):
	if olek:
		return "sees"
	else:
		return "väljas"



def loeHinnaGraafikut(failiNimi):
	if os.path.exists(failiNimi):
		with open(failiNimi, mode='r', encoding='utf-8') as elektriHinnaFail:
			csvFail = list(csv.reader(elektriHinnaFail))
		praeguneAeg = datetime.now(tz=tz.gettz('Europe/Tallinn'))
		print("Elektrihinnad on saadaval kuni kella "+parser.parse(csvFail[-1][0]).strftime("%H:%M (%d.%m.%Y)"))
		for näit in csvFail:
			if not näit[0] == "Kuupäev":
				if parser.parse(näit[0]).year == praeguneAeg.year and parser.parse(näit[0]).month == praeguneAeg.month and parser.parse(näit[0]).day == praeguneAeg.day and parser.parse(näit[0]).hour == praeguneAeg.hour:
					print("Kell on "+praeguneAeg.strftime("%H:%M (%d.%m.%Y)"))
					print("Elektrihind on "+näit[1]+"€/MWh")
					print("Elekter peaks "+eestiKeelesString(näit[2])+" olema! ("+näit[2]+")")
					if näit[2] == "True":
						return True
					else:
						return False
	else:
		print("Ei Leidnud Elektrihinna Graafikut! ("+failiNimi+")")
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
				return True
		else:
			print("Leidsin "+graafikuAsukoht+" faili, kuid formaat tundub vale!")
			return True
	else:
		print("Ei Leidnud Nädalapäeva Graafikut! ("+graafikuAsukoht+")")
		return True


async def loetleAsukohad(rakendusliides):
	asukohad = await rakendusliides.locations()
	for asukoht in asukohad:
		print("Leidsin "+str(len(asukohad))+". Asukoha: "+asukoht.name)



async def loetleSeadmed(rakendusliides, lülitaSisse):
	seadmed = await rakendusliides.devices()
	print("* * * * * * * * * * * * * * * * * * * * * * * * * ")
	print(str(len(seadmed))+" Seade(t)")
	for seade in seadmed:
		print("- - - - - - - - - - - - - - - - - - - - - - - - - ")
		await seade.status.refresh()
		print("Nimi: "+seade.label)
		print("Elekter: "+eestiKeelesBoolean(seade.status.switch)+" ("+str(seade.status.switch)+")")
		#print(f'Võimed: {seade.capabilities}')

		# Lülita Radiaatorid välja
		if "Radiaator" in seade.label:
			if lülitaSisse and loeNädalapäevaGraafikut(graafikuteKaust,seade.label):
				print("Lülitan sisse")
				#await seade.switch_on()
			else:
				print("Lülitan välja")
				#await seade.switch_off()
			
			print("Nüüd on elekter "+eestiKeelesBoolean(seade.status.switch)+". ("+str(seade.status.switch)+")")



async def ühendaSmartThingsi(seadmeteOlek):
	async with aiohttp.ClientSession() as session:
		api = pysmartthings.SmartThings(session, SmartThingsi_Ligipääsu_Token)
		await loetleAsukohad(api)
		await loetleSeadmed(api, seadmeteOlek)





####################################################################################################
#	PÕHI KOOD																					   #
####################################################################################################
if __name__ == "__main__":
	print("\nTere Tulemast Lülitajasse\n")
	print("--------------------------------------------------")
	print("GRAAFIKU LUGEMINE")
	print("--------------------------------------------------")
	lülitiOlek = loeHinnaGraafikut(jooksevFail)
	print("--------------------------------------------------")
	print("LÜLITITELE VAJUTAMINE")
	print("--------------------------------------------------")
	loop = asyncio.get_event_loop()
	loop.run_until_complete( ühendaSmartThingsi(lülitiOlek) )
	print("--------------------------------------------------")
