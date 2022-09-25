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
import aiohttp			#SmartThings APIga Ühendumiseks
import pysmartthings	#SmartThings APIga Ühendumiseks
import asyncio			#SmartThings APIga Ühendumiseks





####################################################################################################
#    SÄTTED                                                                                        #
####################################################################################################
### PEIDA ENNE GIT'i LAADIMIST ###
SmartThingsi_Ligipääsu_Token = ''
### PEIDA ENNE GIT'i LAADIMIST ###





####################################################################################################
#	TUGIFUNKTSIOONID																			   #
####################################################################################################
async def loetleAsukohad(rakendusliides):
	asukohad = await rakendusliides.locations()
	print('---------------------------------------------------------------------------------------------------------')
	print(f'{len(asukohad)} Asukoht(a)')
	for asukoht in asukohad:
		print('-----------------------------------------------------------------------')
		print(f'Nimetus: {asukoht.name}')
		print(f'\tID: {asukoht.location_id}')



async def loetleSeadmed(rakendusliides):
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
		if seade.label == "Kodu-Kontor":
			await seade.switch_on()



async def ühendaSmartThingsi():
	async with aiohttp.ClientSession() as session:
		api = pysmartthings.SmartThings(session, SmartThingsi_Ligipääsu_Token)
		await loetleAsukohad(api)
		await loetleSeadmed(api)
		print('---------------------------------------------------------------------------------------------------------')





####################################################################################################
#	PÕHI KOOD																					   #
####################################################################################################
if __name__ == "__main__":
	loop = asyncio.get_event_loop()
	loop.run_until_complete( ühendaSmartThingsi() )
