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
Uuendatud:	25/09/2022
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





####################################################################################################
#    SÄTTED                                                                                        #
####################################################################################################
### PEIDA ENNE GIT'i LAADIMIST ###
SmartThingsi_Ligipääsu_Token = ''
### PEIDA ENNE GIT'i LAADIMIST ###
jooksevFail = "Elektri_Jooksev_Kasutus.csv"
arhiiviFail = "Elektri_TuruHind.csv"





####################################################################################################
#	TUGIFUNKTSIOONID																			   #
####################################################################################################
def loeHinnaGraafikut(failiNimi):
	with open(failiNimi, mode='r') as elektriHinnaFail:
		csvFail = list(csv.reader(elektriHinnaFail))
	praeguneAeg = datetime.now(tz=tz.gettz('Europe/Tallinn'))
	print("Elektrihinnad on saadaval kuni kella "+parser.parse(csvFail[-1][0]).strftime("%H:%M (%d.%m.%Y)"))
	for näit in csvFail:
		if parser.parse(näit[0]).year == praeguneAeg.year and parser.parse(näit[0]).month == praeguneAeg.month and parser.parse(näit[0]).day == praeguneAeg.day and parser.parse(näit[0]).hour == praeguneAeg.hour:
			print("Kell on "+praeguneAeg.strftime("%H:%M (%d.%m.%Y)"))
			print("Elektrihind on "+näit[1])
			if näit[2]:
				print("Elekter peaks sees olema!")
				return True
			else:
				print("Elekter peaks väljas olema!")
				return False



async def loetleAsukohad(rakendusliides):
	asukohad = await rakendusliides.locations()
	print('---------------------------------------------------------------------------------------------------------')
	print(f'{len(asukohad)} Asukoht(a)')
	for asukoht in asukohad:
		print('-----------------------------------------------------------------------')
		print(f'Nimetus: {asukoht.name}')
		print(f'\tID: {asukoht.location_id}')



async def loetleSeadmed(rakendusliides, lülitaSisse):
	seadmed = await rakendusliides.devices()
	print('---------------------------------------------------------------------------------------------------------')
	print(f'{len(seadmed)} Seade(t)')
	for seade in seadmed:
		print('-----------------------------------------------------------------------')
		await seade.status.refresh()
		print(f'Silt: {seade.label}')
		print(f'\t Tüüp: {seade.name}')
		print(f'\tID: {seade.device_id}')
		print(f'\tVõimed: {seade.capabilities}')
		print(f'\tOlek: {seade.status.switch}')

		# Kiire Test
		if seade.label == "Radiaator":
			if lülitaSisse:
				await seade.switch_on()
			else:
				await seade.switch_off()



async def ühendaSmartThingsi(seadmeteOlek):
	async with aiohttp.ClientSession() as session:
		api = pysmartthings.SmartThings(session, SmartThingsi_Ligipääsu_Token)
		await loetleAsukohad(api)
		await loetleSeadmed(api, seadmeteOlek)
		print('---------------------------------------------------------------------------------------------------------')





####################################################################################################
#	PÕHI KOOD																					   #
####################################################################################################
if __name__ == "__main__":
	lülitiOlek = loeHinnaGraafikut(jooksevFail)
	loop = asyncio.get_event_loop()
	loop.run_until_complete( ühendaSmartThingsi(lülitiOlek) )
