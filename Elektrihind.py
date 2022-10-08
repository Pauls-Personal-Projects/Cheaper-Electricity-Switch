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
import dateutil										# API Kellaaja konverteerimiseks
import matplotlib.pyplot as joonesta				# Elektrihinna joonestamiseks
import os.path										# Failide Salvestamiseks ja Lugemiseks
import csv											# Failide Salvestamiseks ja Lugemiseks





####################################################################################################
#	SÄTTED																						   #
####################################################################################################
#Ajavahemik Elektrihindade Vaatamiseks:
algAeg = datetime.now(tz=tz.gettz('Europe/Tallinn'))-timedelta(hours=1) #lahutame ühe tunni, et hetke hinda ka näha
lõppAeg = algAeg+timedelta(days=1)
#võrguAadress ="https://dashboard.elering.ee/api/nps/price/EE/current"	#Eleringi Praeguse Elektrihinna API
võrguAadress ="https://dashboard.elering.ee/api/nps/price?start=" #+ 2022-09-22T09%3A40%3A00.000Z&end=2022-09-23T00%3A00%3A00.000Z"
jooksevFail = "Elektri_Jooksev_Kasutus.csv"
arhiiviFail = "Elektri_TuruHind.csv"





####################################################################################################
#	TUGIFUNKTSIOONID																			   #
####################################################################################################
def teisendaTekstAjaks(tekst):
	'''
	"aasta-kuu-päev tund:minut:sekund" -> datetime
	Näide: 2022-09-28 21:00:00
	'''
	return dateutil.parser.parse(tekst)
	#return datetime(int(tekst[:4]),int(tekst[5:7]),int(tekst[8:10]),int(tekst[11:13]),int(tekst[14:16]),int(tekst[17:19]), tzinfo=tz.gettz('Europe/Tallinn'))



def elektriMaksustamine(börsiHind):
	tarbijaHind = float(börsiHind)*1.2		# Lisan Käibemaksu
	tarbijaHind = float(tarbijaHind)/10	# Konverteerin €/MWh -> ¢/kWh
	return tarbijaHind		
		
		
		
def vormiKuupäevadAadressi(algKuupäev, lõppKuupäev):
	eraldaja = "%%3A"
	algusKuupäev=algKuupäev.astimezone().replace(tzinfo=tz.gettz('Europe/Tallinn')).astimezone(tz.tzutc())
	lõpuKuupäev=lõppKuupäev.astimezone().replace(tzinfo=tz.gettz('Europe/Tallinn')).astimezone(tz.tzutc())
	kuupäevad = algusKuupäev.strftime("%Y-%m-%dT%H"+eraldaja+"%M"+eraldaja+"00.000Z&end=")+lõpuKuupäev.strftime("%Y-%m-%dT%H"+eraldaja+"%M"+eraldaja+"00.000Z")
	return kuupäevad



def viimaneElektriHind(apiAadress):
	APIvastus = requests.get(võrguAadress).json()
	if APIvastus["success"]:
		kuupäev=datetime.fromtimestamp(APIvastus["data"][0]["timestamp"])
		hind=elektriMaksustamine(APIvastus["data"][0]["price"])
		print("Kuupäev: "+kuupäev.strftime("%d.%m.%Y (%H:%M)"))
		print("Hind: "+str(hind)+"¢/kWh")
	else:
		print("Viga: "+requests.get(võrguAadress).status_code+" (Kontrolli Eleringi API't)")
		
		
		
def elektriHindVahemikus(algKuupäev, lõppKuupäev, apiAadress):
	print("--------------------------------------------------")
	print("LAADIMINE")
	print("--------------------------------------------------")
	print("Küsin elektrihinda vahemikus "+algKuupäev.strftime("%d.%m.%Y(%H:%M)")+" - "+lõppKuupäev.strftime("%d.%m.%Y(%H:%M)\n"))
	APIvastus = requests.get(võrguAadress+vormiKuupäevadAadressi(algKuupäev, lõppKuupäev)).json()
	if APIvastus["success"]:
		elektriHinnad = {}
		for aeg in APIvastus["data"]["ee"]:
			elektriHinnad[datetime.fromtimestamp(aeg["timestamp"])]={"hind":aeg["price"],"sees":True}
		return elektriHinnad
	else:
		print("Viga: "+requests.get(võrguAadress).status_code+" (Kontrolli Eleringi API't)")
		
		
		
def salvestaJooksevInfo(failiNimi, salvestamataAndmed):
	print("--------------------------------------------------")
	print("SALVESTAMINE")
	print("--------------------------------------------------")
	# Elektrihinna CSV Faili Formaat:
	def salvesta():
		with open(failiNimi, mode='w') as elektriHinnaFail:
			csvFail = csv.writer(elektriHinnaFail, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			for aeg in range(len(salvestamataAndmed)):
				csvFail.writerow([str(list(salvestamataAndmed.keys())[aeg]), (salvestamataAndmed[list(salvestamataAndmed.keys())[aeg]]["hind"]), salvestamataAndmed[list(salvestamataAndmed.keys())[aeg]]["sees"]])
	
	# Võrdleb Antud Infot Salvestatuga
	if os.path.exists(failiNimi):
		with open(failiNimi, mode ='r')as elektriHinnaFail:
			csvFail = list(csv.reader(elektriHinnaFail))
		print("Viimane Salvestatud Elektrihind: "+teisendaTekstAjaks(csvFail[-1][0]).strftime("%H:%M (%d.%m.%Y) - ")+str(round(elektriMaksustamine(csvFail[-1][1]),2))+"¢/kWh")
		print("Viimane Elektrihind Eleringilt: "+list(salvestamataAndmed.keys())[-1].strftime("%H:%M (%d.%m.%Y) - ")+str(round(elektriMaksustamine(list(salvestamataAndmed.values())[-1]["hind"]),2))+"¢/kWh")
		if teisendaTekstAjaks(csvFail[-1][0])<list(salvestamataAndmed.keys())[-1]:
			print("Salvestan Uue Info "+failiNimi+" Faili!")
			salvesta()
		else:
			print("Kõige Uuem Info on Juba Olemas "+failiNimi+" Failis!")
	else:
		print("Salvestan Elektrihinna "+failiNimi+" Faili!")
		salvesta()
		
		
		
def lülitaHinnaTeravikulElekterVälja(elektriAndmed, teravikuKõrgus, akuMaht):
	'''
	Otsib millal hind tõuseb järsult hetkeks!
	teravikuKõrgus on €/MWh
	akuMaht on tundides
	'''
	print("--------------------------------------------------")
	print("HINNA TERAVIKU OTSING")
	print("--------------------------------------------------")
	for aeg in range(len(elektriAndmed)):
		if aeg>0 and aeg<(len(elektriAndmed)-1):
			if elektriAndmed[list(elektriAndmed.keys())[aeg]]["hind"] > (elektriAndmed[list(elektriAndmed.keys())[aeg-1]]["hind"]+teravikuKõrgus):
				print("Järsk Hinna Tõus kell "+list(elektriAndmed.keys())[aeg].strftime("%H:%M (%d.%m.%Y) - ")+str(round(elektriMaksustamine(elektriAndmed[list(elektriAndmed.keys())[aeg-1]]["hind"]),2))+"¢/kWh -> "+str(round(elektriMaksustamine(elektriAndmed[list(elektriAndmed.keys())[aeg]]["hind"]),2))+"¢/kWh!")	
				for teravikuAeg in range(1, akuMaht+1):
					if aeg+teravikuAeg<(len(elektriAndmed)-1):
						if (elektriAndmed[list(elektriAndmed.keys())[aeg+teravikuAeg]]["hind"]+teravikuKõrgus) < (elektriAndmed[list(elektriAndmed.keys())[aeg]]["hind"]):
							print(str(teravikuAeg)+" tunniks, Lülitan Elektri Välja")
							for muudetavAeg in range(aeg, aeg+teravikuAeg):
								elektriAndmed[list(elektriAndmed.keys())[muudetavAeg]]["sees"]=False
							break



def lülitaElekterVälja(elektriAndmed, kuupäev):
	elektriAndmed[list(elektriAndmed.keys())[kuupäev]]["sees"]=False
	
	
	
def statistika(elektriAndmed):
	print("--------------------------------------------------")
	print("STATISTIKA")
	print("--------------------------------------------------")
	keskmineHind={"summa":0,"kogus":len(elektriAndmed),"tulemus":0}
	seesHind={"summa":0,"kogus":0,"tulemus":0}
	väljasHind={"summa":0,"kogus":0,"tulemus":0}
	for aeg in range(len(elektriAndmed)):
		keskmineHind["summa"]+=elektriAndmed[list(elektriAndmed.keys())[aeg]]["hind"]
		if elektriAndmed[list(elektriAndmed.keys())[aeg]]["sees"]:
			seesHind["summa"]+=elektriAndmed[list(elektriAndmed.keys())[aeg]]["hind"]
			seesHind["kogus"]+=1
		else:
			väljasHind["summa"]+=elektriAndmed[list(elektriAndmed.keys())[aeg]]["hind"]
			väljasHind["kogus"]+=1
	keskmineHind["tulemus"]=elektriMaksustamine(keskmineHind["summa"]/keskmineHind["kogus"])
	seesHind["tulemus"]=elektriMaksustamine(seesHind["summa"]/seesHind["kogus"])
	väljasHind["tulemus"]=elektriMaksustamine(väljasHind["summa"]/väljasHind["kogus"])
	print("Saadaval on järgneva "+str(keskmineHind["kogus"])+" tunni elektrihinnad\n")
	print("Sellel ajal on keskmine elektrihind: "+str(round(keskmineHind["tulemus"],2))+"¢/kWh")
	print("Kasutuse ajal on keskmine elektrihind: "+str(round(seesHind["tulemus"],2))+"¢/kWh")
	print("Väljalülitamise ajal on keskmine elektrihind: "+str(round(väljasHind["tulemus"],2))+"¢/kWh")
		




####################################################################################################
#	PÕHI KOOD																					   #
####################################################################################################
if __name__ == '__main__':
	print("\n\n")
	kõikHinnad = elektriHindVahemikus(algAeg,lõppAeg,võrguAadress)
	lülitaHinnaTeravikulElekterVälja(kõikHinnad,30,2)
	### TESTIMATA ###
	for aeg in range(len(kõikHinnad)):
		if list(kõikHinnad.keys())[aeg].weekday() < 5 and list(kõikHinnad.keys())[aeg].hour > 5 and list(kõikHinnad.keys())[aeg].hour < 17:
			lülitaElekterVälja(kõikHinnad, aeg)
	### TESTIMATA ###
	statistika(kõikHinnad)
	salvestaJooksevInfo(jooksevFail,kõikHinnad)
	
	#Joonestus
	'''
	print("Joonestus andmed: "+str(list(kõikHinnad.values())[0]["hind"]))
	joonesta.bar(list(kõikHinnad.keys()),list(map(elektriMaksustamine,list(kõikHinnad.values())["hind"])), width=0.03, color='royalblue')
	joonesta.title("Elektrihind vahemikus "+list(kõikHinnad.keys())[0].strftime("%d.%m.%Y(%H:%M)")+" - "+list(kõikHinnad.keys())[-1].strftime("%d.%m.%Y(%H:%M)"))
	joonesta.ylabel("¢/kWh")
	joonesta.xlabel("Kell")
	joonesta.show()
	'''
