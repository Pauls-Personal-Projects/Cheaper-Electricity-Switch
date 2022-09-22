#!/usr/bin/env python3
# -*- coding: utf-8 -*-

####################################################################################################
#																								   #
#											ELEKTRIHIND											   #
#																								   #
####################################################################################################
'''
Looja:		Paul J. Aru		-	https://github.com/paulpall
Kuupäev:	25/06/2022
Uuendatud:	22/09/2022
'''



####################################################################################################
#	TEEGID																						   #
####################################################################################################
import requests										# Eleringi APIga Ühendumiseks
from datetime import datetime, timezone, timedelta	# API Kellaaja konverteerimiseks
from dateutil import tz								# API Kellaaja konverteerimiseks
import matplotlib.pyplot as plt						# Elektrihinna joonestamiseks



####################################################################################################
#	SÄTTED																						   #
####################################################################################################
#Ajavahemik Elektrihindade Vaatamiseks
algAeg = datetime.utcnow().astimezone().replace(tzinfo=tz.tzutc()).astimezone(tz.gettz('Europe/Tallinn'))-timedelta(hours=1)
lõppAeg = algAeg+timedelta(days=1)
#võrguAadress ="https://dashboard.elering.ee/api/nps/price/EE/current"	#Eleringi Praeguse Elektrihinna API
võrguAadress ="https://dashboard.elering.ee/api/nps/price?start=" #+ 2022-09-22T09%3A40%3A00.000Z&end=2022-09-23T00%3A00%3A00.000Z"



####################################################################################################
#	TUGIFUNKTSIOONID																			   #
####################################################################################################



def elektriMaksustamine(börsiHind):
	tarbijaHind = börsiHind*1.2		# Lisan Käibemaksu
	tarbijaHind = tarbijaHind/10	# Konverteerin €/MWh -> ¢/kWh
	return tarbijaHind



def viimaneElektriHind(apiAadress):
	APIvastus = requests.get(võrguAadress).json()
	if APIvastus["success"]:
		kuupäev=datetime.fromtimestamp(APIvastus["data"][0]["timestamp"])
		hind=elektriMaksustamine(APIvastus["data"][0]["price"])
		print("Kuupäev: "+kuupäev.strftime("%d.%m.%Y (%H:%M)"))
		print("Hind: "+str(hind)+"¢/kWh")
	else:
		print("Viga: "+requests.get(võrguAadress).status_code+" (Kontrolli Eleringi API't)")
		
		
		
def vormiKuupäevadAadressi(algKuupäev, lõppKuupäev):
	eraldaja = "%%3A"
	algusKuupäev=algKuupäev.astimezone().replace(tzinfo=tz.gettz('Europe/Tallinn')).astimezone(tz.tzutc())
	lõpuKuupäev=lõppKuupäev.astimezone().replace(tzinfo=tz.gettz('Europe/Tallinn')).astimezone(tz.tzutc())
	kuupäevad = algusKuupäev.strftime("%Y-%m-%dT%H"+eraldaja+"%M"+eraldaja+"00.000Z&end=")+lõpuKuupäev.strftime("%Y-%m-%dT%H"+eraldaja+"%M"+eraldaja+"00.000Z")
	return kuupäevad
		
		
		
def elektriHindVahemikus(algKuupäev, lõppKuupäev, apiAadress):
	print("Küsin elektrihinda vahemikus "+algKuupäev.strftime("%d.%m.%Y(%H:%M)")+" - "+lõppKuupäev.strftime("%d.%m.%Y(%H:%M)"))
	APIvastus = requests.get(võrguAadress+vormiKuupäevadAadressi(algKuupäev, lõppKuupäev)).json()
	if APIvastus["success"]:
		elektriHinnad = {}
		for aeg in APIvastus["data"]["ee"]:
			elektriHinnad[datetime.fromtimestamp(aeg["timestamp"])]=elektriMaksustamine(aeg["price"])
		
		for aeg in range(len(elektriHinnad)):
			print(list(elektriHinnad.keys())[aeg].strftime("%d.%m.%Y (%H:%M) - ")+str(elektriHinnad[list(elektriHinnad.keys())[aeg]])+"¢/kWh")
		
		plt.plot(list(elektriHinnad.keys()),list(elektriHinnad.values()))
		plt.title("Elektrihind vahemikus "+list(elektriHinnad.keys())[0].strftime("%d.%m.%Y(%H:%M)")+" - "+list(elektriHinnad.keys())[-1].strftime("%d.%m.%Y(%H:%M)"))
		plt.ylabel("¢/kWh")
		plt.xlabel("Kell")
		plt.show()
	else:
		print("Viga: "+requests.get(võrguAadress).status_code+" (Kontrolli Eleringi API't)")



####################################################################################################
#	PÕHI KOOD																					   #
####################################################################################################



if __name__ == '__main__':
	#viimaneElektriHind(võrguAadress)
	elektriHindVahemikus(algAeg,lõppAeg,võrguAadress)
