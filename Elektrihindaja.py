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
Uuendatud:	15/10/2022
'''



####################################################################################################
#	TEEGID																						   #
####################################################################################################
import requests										# Eleringi APIga Ühendumiseks
from datetime import datetime, timezone, timedelta	# API Kellaaja konverteerimiseks
from dateutil import tz								# API Kellaaja konverteerimiseks
import dateutil										# API Kellaaja konverteerimiseks
import matplotlib.pyplot as joonesta				# Elektrihinna joonestamiseks
import os											# Failide Salvestamiseks ja Lugemiseks
import csv											# Failide Salvestamiseks ja Lugemiseks





####################################################################################################
#	SÄTTED																						   #
####################################################################################################
akudeMaht = 2 #Kauaks elektri võib välja lülitada
#võrguAadress ="https://dashboard.elering.ee/api/nps/price/EE/current"	#Eleringi Praeguse Elektrihinna API
võrguAadress ="https://dashboard.elering.ee/api/nps/price?start=" #+ 2022-09-22T09%3A40%3A00.000Z&end=2022-09-23T00%3A00%3A00.000Z"
jooksevFail = "Elektri_Jooksev_Kasutus.csv"
arhiiviKaust = "Elektri_TuruHind"
#Ajavahemik Elektrihindade Vaatamiseks:
algAeg = datetime.now(tz=tz.gettz('Europe/Tallinn'))-timedelta(hours=akudeMaht+1) #lahutame kaks tundi, et hetke hinnamuutust näha
lõppAeg = algAeg+timedelta(days=2)





####################################################################################################
#	TUGIFUNKTSIOONID																			   #
####################################################################################################
def teisendaTekstAjaks(tekst):
	'''
	"aasta-kuu-päev tund:minut:sekund" -> datetime
	Näide: 2022-09-28 21:00:00
	'''
	return dateutil.parser.parse(tekst)



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
	print("Küsin elektrihinda vahemikus "+algKuupäev.strftime("%d.%m.%Y(%H:%M)")+" - "+lõppKuupäev.strftime("%d.%m.%Y(%H:%M)"))
	APIvastus = requests.get(võrguAadress+vormiKuupäevadAadressi(algKuupäev, lõppKuupäev)).json()
	if APIvastus["success"]:
		elektriHinnad = {}
		for aeg in APIvastus["data"]["ee"]:
			elektriHinnad[datetime.fromtimestamp(aeg["timestamp"])]={"hind":aeg["price"],"sees":True}
		print("Sain elektrihinna vahemikus "+list(elektriHinnad.keys())[0].strftime("%d.%m.%Y(%H:%M)")+" - "+list(elektriHinnad.keys())[-1].strftime("%d.%m.%Y(%H:%M)\n"))
		return elektriHinnad
	else:
		print("Viga: "+requests.get(võrguAadress).status_code+" (Kontrolli Eleringi API't)")
		
		
		
def salvestaJooksevInfo(failiNimi, salvestamataAndmed):
	# Elektrihinna CSV Faili Formaat:
	def salvesta():
		with open(failiNimi, mode='w', encoding='utf-8') as elektriHinnaFail:
			csvFail = csv.writer(elektriHinnaFail, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			csvFail.writerow(["Kuupäev", "Hind", "Lüliti"])
			for aeg in range(len(salvestamataAndmed)):
				csvFail.writerow([str(list(salvestamataAndmed.keys())[aeg]), (salvestamataAndmed[list(salvestamataAndmed.keys())[aeg]]["hind"]), salvestamataAndmed[list(salvestamataAndmed.keys())[aeg]]["sees"]])
	# Võrdleb Antud Infot Salvestatuga
	if os.path.exists(failiNimi):
		with open(failiNimi, mode ='r', encoding='utf-8')as elektriHinnaFail:
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



def salvestaArhiiviInfo(kaustaNimi, salvestamataAndmed):
	def looFail(failiNimi):
		with open(failiNimi, mode='w', encoding='utf-8') as elektriHinnaFail:
			csvFail = csv.writer(elektriHinnaFail, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			csvFail.writerow(["Kuupäev", "Hind", "Lüliti"])
			for aeg in range(len(salvestamataAndmed)):
				csvFail.writerow([str(list(salvestamataAndmed.keys())[aeg]), (salvestamataAndmed[list(salvestamataAndmed.keys())[aeg]]["hind"]), salvestamataAndmed[list(salvestamataAndmed.keys())[aeg]]["sees"]])
	def otsiJärg(failiNimi):
		with open(failiNimi, mode ='r', encoding='utf-8')as elektriHinnaFail:
			csvFail = list(csv.reader(elektriHinnaFail))
		return teisendaTekstAjaks(csvFail[-1][0])
	def lisaFaili(failiNimi, järg):
		with open(failiNimi, mode='a', encoding='utf-8') as elektriHinnaFail:
			csvFail = csv.writer(elektriHinnaFail, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		lisandused = 0
		for aeg in range(len(salvestamataAndmed)):
			if järg < list(salvestamataAndmed.keys())[aeg]:
				lisandused += 1
				csvFail.writerow([str(list(salvestamataAndmed.keys())[aeg]), (salvestamataAndmed[list(salvestamataAndmed.keys())[aeg]]["hind"]), salvestamataAndmed[list(salvestamataAndmed.keys())[aeg]]["sees"]])
		return lisandused
	# Otsi õige kaust ja fail!
	if os.path.exists(kaustaNimi):
		if os.path.exists(kaustaNimi+"/"+str(list(salvestamataAndmed.keys())[0].year)):
			if os.path.exists(kaustaNimi+"/"+str(list(salvestamataAndmed.keys())[0].year)+"/"+list(salvestamataAndmed.keys())[0].strftime("Elektri_turuhind_%m-%Y.csv")):
				viimaneInfo = otsiJärg(kaustaNimi+"/"+str(list(salvestamataAndmed.keys())[0].year)+"/"+list(salvestamataAndmed.keys())[0].strftime("Elektri_turuhind_%m-%Y.csv"))
				if viimaneInfo < list(salvestamataAndmed.keys())[-1]:
					print("Lisasin "+lisaFaili(kaustaNimi+"/"+str(list(salvestamataAndmed.keys())[0].year)+"/"+list(salvestamataAndmed.keys())[0].strftime("Elektri_turuhind_%m-%Y.csv"),viimaneInfo)+" näitu "+kaustaNimi+"/"+str(list(salvestamataAndmed.keys())[0].year)+"/"+list(salvestamataAndmed.keys())[0].strftime("Elektri_turuhind_%m-%Y.csv")+" faili")
				else:
					print("Viimane info on juba hoiustatud! "+viimaneInfo.strftime("[%H:%M (%d.%m.%Y)]"))
			else:
				looFail(kaustaNimi+"/"+str(list(salvestamataAndmed.keys())[0].year)+"/"+list(salvestamataAndmed.keys())[0].strftime("Elektri_turuhind_%m-%Y.csv"))
		else:
			os.mkdir(kaustaNimi+"/"+str(list(salvestamataAndmed.keys())[0].year))
			looFail(kaustaNimi+"/"+str(list(salvestamataAndmed.keys())[0].year)+"/"+list(salvestamataAndmed.keys())[0].strftime("Elektri_turuhind_%m-%Y.csv"))
	else:
		os.mkdir(kaustaNimi)
		os.mkdir(kaustaNimi+"/"+str(list(salvestamataAndmed.keys())[0].year))
		looFail(kaustaNimi+"/"+str(list(salvestamataAndmed.keys())[0].year)+"/"+list(salvestamataAndmed.keys())[0].strftime("Elektri_turuhind_%m-%Y.csv"))



def lülitaHinnaTeravikulElekterVälja(elektriAndmed, teravikuKõrgus, akuMaht):
	'''
	Otsib millal hind tõuseb järsult hetkeks!
	teravikuKõrgus on €/MWh
	akuMaht on tundides
	'''
	for aeg in range(len(elektriAndmed)):
		if aeg>0 and aeg<(len(elektriAndmed)-1):
			if elektriAndmed[list(elektriAndmed.keys())[aeg]]["hind"] > (elektriAndmed[list(elektriAndmed.keys())[aeg-1]]["hind"]+teravikuKõrgus):
				print("Järsk Hinna Tõus kell "+list(elektriAndmed.keys())[aeg].strftime("%H:%M (%d.%m.%Y) - ")+str(round(elektriMaksustamine(elektriAndmed[list(elektriAndmed.keys())[aeg-1]]["hind"]),2))+"¢/kWh -> "+str(round(elektriMaksustamine(elektriAndmed[list(elektriAndmed.keys())[aeg]]["hind"]),2))+"¢/kWh!")	
				for teravikuAeg in range(1, akuMaht+1):
					if aeg+teravikuAeg<(len(elektriAndmed)-1):
						#print("Võrdlen kas "+str(elektriMaksustamine(elektriAndmed[list(elektriAndmed.keys())[aeg+teravikuAeg]]["hind"]+teravikuKõrgus))+" on väiksem, kui "+str(elektriMaksustamine(elektriAndmed[list(elektriAndmed.keys())[aeg]]["hind"])))
						if (elektriAndmed[list(elektriAndmed.keys())[aeg+teravikuAeg]]["hind"]+teravikuKõrgus) < (elektriAndmed[list(elektriAndmed.keys())[aeg]]["hind"]):
							print(str(teravikuAeg)+" tunniks, Lülitan Elektri Välja")
							for muudetavAeg in range(aeg, aeg+teravikuAeg):
								elektriAndmed[list(elektriAndmed.keys())[muudetavAeg]]["sees"]=False
							break



def lülitaElekterVälja(elektriAndmed, kuupäev):
	elektriAndmed[list(elektriAndmed.keys())[kuupäev]]["sees"]=False
	
	
	
def statistika(elektriAndmed):
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
	print("Saadaval on järgneva "+str(keskmineHind["kogus"])+" tunni elektrihinnad\n")
	if keskmineHind["kogus"] > 0:
		keskmineHind["tulemus"]=elektriMaksustamine(keskmineHind["summa"]/keskmineHind["kogus"])
		print("Sellel ajal on keskmine elektrihind: "+str(round(keskmineHind["tulemus"],2))+"¢/kWh")
	if seesHind["kogus"] > 0:
		seesHind["tulemus"]=elektriMaksustamine(seesHind["summa"]/seesHind["kogus"])
		print("Kasutuse ajal on keskmine elektrihind: "+str(round(seesHind["tulemus"],2))+"¢/kWh")
	if väljasHind["kogus"] > 0:
		väljasHind["tulemus"]=elektriMaksustamine(väljasHind["summa"]/väljasHind["kogus"])
		print("Väljalülitamise ajal on keskmine elektrihind: "+str(round(väljasHind["tulemus"],2))+"¢/kWh")





####################################################################################################
#	PÕHI KOOD																					   #
####################################################################################################
if __name__ == '__main__':
	print("\nTere Tulemast Elektrihindajasse\n")
	print("--------------------------------------------------")
	print("LAADIMINE")
	print("--------------------------------------------------")
	kõikHinnad = elektriHindVahemikus(algAeg,lõppAeg,võrguAadress)
	print("\n--------------------------------------------------")
	print("KÕRGE HINNA OTSING")
	print("--------------------------------------------------")
	lülitaHinnaTeravikulElekterVälja(kõikHinnad,30,akudeMaht)
	print("\n--------------------------------------------------")
	print("STATISTIKA")
	print("--------------------------------------------------")
	statistika(kõikHinnad)
	print("\n--------------------------------------------------")
	print("SALVESTAMINE")
	print("--------------------------------------------------")
	salvestaJooksevInfo(jooksevFail,kõikHinnad)
	print("\n--------------------------------------------------")
	print("ARHIVEERIN")
	print("--------------------------------------------------")
	salvestaArhiiviInfo(arhiiviKaust,kõikHinnad)
