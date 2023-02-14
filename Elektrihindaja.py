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
Uuendatud:	14/02/2023
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
import sys											# Veateate Edastamiseks Synology DSM'ile





####################################################################################################
#	SÄTTED																						   #
####################################################################################################
akudeMaht = 1 #Kauaks elektri võib välja lülitada
#võrguAadress ="https://dashboard.elering.ee/api/nps/price/EE/current"	#Eleringi Praeguse Elektrihinna API
võrguAadress ="https://dashboard.elering.ee/api/nps/price?start=" #+ 2022-09-22T09%3A40%3A00.000Z&end=2022-09-23T00%3A00%3A00.000Z"
jooksevFail = "Elektri_Jooksev_Kasutus.csv" #IDE Kaust
arhiiviKaust = "Elektri_TuruHind" #IDE Kaust
#jooksevFail = "/volume1/homes/Paul/Drive/Ajutine/Elektri_Jooksev_Kasutus.csv" #Pilve Kaust
#arhiiviKaust = "/volume7/Arhiiv/Teave/Elektri Turuhind" #Pilve Kaust
#Ajavahemik Elektrihindade Vaatamiseks:
algAeg = datetime.now(tz=tz.gettz('Europe/Tallinn'))-timedelta(hours=akudeMaht+1) #lahutame kaks tundi, et hetke hinnamuutust näha
lõppAeg = algAeg+timedelta(days=2)
### AJUTINE ###
ajutisedSeadmed = ["Köök-Nõudepesumasin", "Paul-Kontor"]
ajutisedRadiaatorid = ["Garderoob-Radiaator", "Paul-Radiaator", "Magamis-Radiaator"]
### AJUTINE ###
silumine = False





####################################################################################################
#	TUGIFUNKTSIOONID																			   #
####################################################################################################
def elektriMaksustamine(börsiHind):
	tarbijaHind = float(börsiHind)*1.2		# Lisan Käibemaksu
	tarbijaHind = float(tarbijaHind)/10	# Konverteerin €/MWh -> ¢/kWh
	return tarbijaHind





####################################################################################################
#	ALLALAADIMISE FUNKTSIOONID																	   #
####################################################################################################
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
		silumine = True
		
		
		
def elektriHindVahemikus(algKuupäev, lõppKuupäev, apiAadress):
	print("Küsin Elektrihinda Vahemikus "+algKuupäev.strftime("%d.%m.%Y(%H:%M)")+" - "+lõppKuupäev.strftime("%d.%m.%Y(%H:%M)"))
	APIvastus = requests.get(võrguAadress+vormiKuupäevadAadressi(algKuupäev, lõppKuupäev)).json()
	if APIvastus["success"]:
		elektriHinnad = {}
		for aeg in APIvastus["data"]["ee"]:
			elektriHinnad[datetime.fromtimestamp(aeg["timestamp"])]={"Hind":aeg["price"]}
		print("Vastati Elektrihinnaga Vahemikus "+list(elektriHinnad.keys())[0].strftime("%d.%m.%Y(%H:%M)")+" - "+list(elektriHinnad.keys())[-1].strftime("%d.%m.%Y(%H:%M)"))
		return elektriHinnad
	else:
		print("Viga: "+requests.get(võrguAadress).status_code+" (Kontrolli Eleringi API't)")
		silumine = True





####################################################################################################
#	SALVESTUS FUNKTSIOONID																		   #
####################################################################################################
def booleanTekstiks(olek):
	if olek:
		tekst = "sees"
	else:
		tekst = "väljas"
	return tekst



# .csv Rea Konstrueerimine salvestamataAndmed andmesõnastikust
def csvReaKonstruktor(reaPäis, reaJärg, salvestamataAndmed):
	#Kuupäev, Hind
	rida = [str(list(salvestamataAndmed.keys())[reaJärg]), salvestamataAndmed[list(salvestamataAndmed.keys())[reaJärg]][reaPäis[1]]]
	for tulp in range(2,len(reaPäis)):
		#Jooksvad Keskmised Hinnad
		if ". Tunni Keskmine" in reaPäis[tulp]:
			rida.append(round(salvestamataAndmed[list(salvestamataAndmed.keys())[reaJärg]][reaPäis[tulp]],2))
		#Lülitite Olekud
		else:
			rida.append(booleanTekstiks(salvestamataAndmed[list(salvestamataAndmed.keys())[reaJärg]][reaPäis[tulp]]))
	return rida



def salvestaJooksevInfo(failiNimi, salvestamataAndmed):
	# Elektrihinna CSV Faili Formaat:
	def salvesta():
		with open(failiNimi, mode='w', encoding='utf-8') as elektriHinnaFail:
			csvFail = csv.writer(elektriHinnaFail, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			päis = ['Kuupäev']
			päis.extend(list(salvestamataAndmed[list(salvestamataAndmed.keys())[0]].keys()))
			csvFail.writerow(päis)
			for aeg in range(len(salvestamataAndmed)):
					csvFail.writerow(csvReaKonstruktor(päis, aeg, salvestamataAndmed))
		'''
		with open(failiNimi, mode='w', encoding='utf-8') as elektriHinnaFail:
			csvFail = csv.writer(elektriHinnaFail, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			päis = ['Kuupäev']
			päis.extend(list(salvestamataAndmed[list(salvestamataAndmed.keys())[0]].keys()))
			csvFail.writerow(päis)
			for aeg in range(len(salvestamataAndmed)):
				rida = [str(list(salvestamataAndmed.keys())[aeg]), salvestamataAndmed[list(salvestamataAndmed.keys())[aeg]][päis[1]], round(salvestamataAndmed[list(salvestamataAndmed.keys())[aeg]][päis[2]],2)]
				for seade in range(3,len(päis)):
					rida.append(booleanTekstiks(salvestamataAndmed[list(salvestamataAndmed.keys())[aeg]][päis[seade]]))
				csvFail.writerow(rida)
		'''
	# Võrdleb Antud Infot Salvestatuga
	if os.path.exists(failiNimi):
		with open(failiNimi, mode ='r', encoding='utf-8')as elektriHinnaFail:
			csvFail = list(csv.reader(elektriHinnaFail))
		print("Viimane Salvestatud Elektrihind: "+dateutil.parser.parse(csvFail[-1][0]).strftime("%H:%M (%d.%m.%Y) - ")+str(round(elektriMaksustamine(csvFail[-1][1]),2))+"¢/kWh")
		print("Viimane Mälus Elektrihind (Eleringilt): "+list(salvestamataAndmed.keys())[-1].strftime("%H:%M (%d.%m.%Y) - ")+str(round(elektriMaksustamine(list(salvestamataAndmed.values())[-1]["Hind"]),2))+"¢/kWh")
		if dateutil.parser.parse(csvFail[-1][0])<list(salvestamataAndmed.keys())[-1]:
			print("Uuendan Jooksvat Elektrihinda: "+failiNimi)
			salvesta()
		else:
			print("Ajakohane Jooksev Elektrihind on Juba Olemas: "+failiNimi)
	else:
		print("Salvestan Jooksva Elektrihinna: "+failiNimi)
		salvesta()



# This is a Horrible Mess
def salvestaArhiiviInfo(kaustaNimi, salvestamataAndmed):
	def looFail(failiNimi, järg):
		with open(failiNimi, mode='w', encoding='utf-8') as elektriHinnaFail:
			csvFail = csv.writer(elektriHinnaFail, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			päis = ['Kuupäev']
			päis.extend(list(salvestamataAndmed[list(salvestamataAndmed.keys())[0]].keys()))
			csvFail.writerow(päis)
			for aeg in range(len(salvestamataAndmed)):
				if järg <= list(salvestamataAndmed.keys())[aeg]:
					csvFail.writerow(csvReaKonstruktor(päis, aeg, salvestamataAndmed))
		print(str(len(salvestamataAndmed))+" näitu arhiveeritud faili: "+failiNimi)
		
	def loeFaili(failiNimi):
		with open(failiNimi, mode ='r', encoding='utf-8')as elektriHinnaFail:
			csvFail = list(csv.reader(elektriHinnaFail))
			return csvFail
			
	def lisaFaili(failiNimi, järg):
		päis = ['Kuupäev']
		päis.extend(list(salvestamataAndmed[list(salvestamataAndmed.keys())[0]].keys()))
		salvestatudPäis = loeFaili(failiNimi)[0]
		with open(failiNimi, mode='a', encoding='utf-8') as elektriHinnaFail:
			csvFail = csv.writer(elektriHinnaFail, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			lisandused = 0
			if not päis == salvestatudPäis:
				print("PÄIS ON MUUTUNUD???")
				print("Salvestatud: "+str(salvestatudPäis))
				print("Uus: "+str(päis))
				csvFail.writerow(päis)
			for aeg in range(len(salvestamataAndmed)):
				if järg < list(salvestamataAndmed.keys())[aeg] and list(salvestamataAndmed.keys())[aeg].month == dateutil.parser.parse(loeFaili(failiNimi)[1][0]).month:
					lisandused += 1
					csvFail.writerow(csvReaKonstruktor(päis, aeg, salvestamataAndmed))
				elif järg < list(salvestamataAndmed.keys())[aeg] and not list(salvestamataAndmed.keys())[aeg].month == dateutil.parser.parse(loeFaili(failiNimi)[1][0]).month:
					print(str(lisandused)+" näitu arhiveeritud faili: "+failiNimi)
					return list(salvestamataAndmed.keys())[aeg]
					#break
		print(str(lisandused)+" näitu arhiveeritud faili: "+failiNimi)
		return list(salvestamataAndmed.keys())[aeg]
	# Otsi õige kaust ja fail!
	if os.path.exists(kaustaNimi):
		if os.path.exists(kaustaNimi+"/"+str(list(salvestamataAndmed.keys())[0].year)):
			arhiiviFail = (kaustaNimi+"/"+str(list(salvestamataAndmed.keys())[0].year)+"/"+list(salvestamataAndmed.keys())[0].strftime("Elektri_turuhind_%m-%Y.csv"))
			if os.path.exists(arhiiviFail):
				viimaneInfo = loeFaili(arhiiviFail)
				if not dateutil.parser.parse(viimaneInfo[-1][0]) == None:
					järg = dateutil.parser.parse(viimaneInfo[-1][0])
				else:
					print("VIGA: Tühi Fail on Tekkinud! ("+arhiiviFail+")")
					silumine = True
				if dateutil.parser.parse(viimaneInfo[-1][0]) < list(salvestamataAndmed.keys())[-1]:
					kuuJärg = lisaFaili(arhiiviFail, järg)
					if not kuuJärg.month == järg.month:
						arhiiviFail = (kaustaNimi+kuuJärg.strftime("/%Y/Elektri_turuhind_%m-%Y.csv"))
						if os.path.exists(arhiiviFail):
							print("Kuu lõpp, Jätkan Uues Failis")
							lisaFaili(arhiiviFail, kuuJärg)
						else:
							if not os.path.exists(kaustaNimi+kuuJärg.strftime("/%Y")):
								os.mkdir(kaustaNimi+kuuJärg.strftime("/%Y"))
							print("Kuu lõppes, Teen Uue Faili")
							looFail(arhiiviFail, kuuJärg)
				else:
					print("Viimane info on juba hoiustatud! "+dateutil.parser.parse(viimaneInfo[-1][0]).strftime("[%H:%M (%d.%m.%Y)]"))
			else:
				print("Uus Kuu, Uus Fail!")
				looFail(kaustaNimi+"/"+str(list(salvestamataAndmed.keys())[0].year)+"/"+list(salvestamataAndmed.keys())[0].strftime("Elektri_turuhind_%m-%Y.csv"),0)
		else:
			print("Head Uut Aastat "+str(list(salvestamataAndmed.keys())[0].year)+"!")
			os.mkdir(kaustaNimi+"/"+str(list(salvestamataAndmed.keys())[0].year))
			looFail(arhiiviFail)
	else:
		print("Ei leidnud "+kaustaNimi+"! Loon uue arhiivi kausta.")
		os.mkdir(kaustaNimi)
		os.mkdir(kaustaNimi+"/"+str(list(salvestamataAndmed.keys())[0].year))
		arhiiviFail = (kaustaNimi+"/"+str(list(salvestamataAndmed.keys())[0].year)+"/"+list(salvestamataAndmed.keys())[0].strftime("Elektri_turuhind_%m-%Y.csv"))
		looFail(arhiiviFail)





####################################################################################################
#	HINNA ANALÜÜSI FUNKTSIOONID																	   #
####################################################################################################
def lülitaHinnaTeravikulElekterVälja(elektriAndmed, teravikuKõrgus, akuMaht, seade):
	'''
	(Annaks Optimeerida) Otsib millal hind tõuseb järsult hetkeks!
	teravikuKõrgus on €/MWh, tähistab millal elekter välja lülitada
	akuMaht on tundides, tähistab kaua elekter väljas on
	'''
	print(seade+": Otsin Kalleid Aegu Elektri Välja Märkimiseks")
	for aeg in range(len(elektriAndmed)):
		if aeg>0:
			if elektriAndmed[list(elektriAndmed.keys())[aeg]]["Hind"] > (elektriAndmed[list(elektriAndmed.keys())[aeg-1]]["Hind"]+teravikuKõrgus):
				print("Järsk Hinna Tõus kell "+list(elektriAndmed.keys())[aeg].strftime("%H:%M (%d.%m.%Y) - ")+str(round(elektriMaksustamine(elektriAndmed[list(elektriAndmed.keys())[aeg-1]]["Hind"]),2))+"¢/kWh -> "+str(round(elektriMaksustamine(elektriAndmed[list(elektriAndmed.keys())[aeg]]["Hind"]),2))+"¢/kWh!")	
				for teravikuAeg in range(1, akuMaht+1):
					if (aeg+teravikuAeg)<(len(elektriAndmed)-1):
						#print("Võrdlen kas "+str(elektriMaksustamine(elektriAndmed[list(elektriAndmed.keys())[aeg+teravikuAeg]]["Hind"]+teravikuKõrgus))+" on väiksem, kui "+str(elektriMaksustamine(elektriAndmed[list(elektriAndmed.keys())[aeg]]["Hind"])))
						if (elektriAndmed[list(elektriAndmed.keys())[aeg+teravikuAeg]]["Hind"]+teravikuKõrgus) < (elektriAndmed[list(elektriAndmed.keys())[aeg]]["Hind"]):
							print(str(teravikuAeg)+" tunniks, Lülitan Elektri Välja")
							for muudetavAeg in range(aeg, aeg+teravikuAeg):
								#print("Lülitan "+list(elektriAndmed.keys())[muudetavAeg].strftime("%H:%M (%d.%m.%Y) Elektri välja"))
								elektriAndmed[list(elektriAndmed.keys())[muudetavAeg]][seade]=False
							break



def lisaJooksevKeskmineHind(elektriAndmed, kasutusAeg):
	'''
	Arvutab Jooksva Keskmise Järgnevate Tundidega
	kasutusAeg on tundides, kaua elekter sees on
	'''
	for aeg in range(len(elektriAndmed)):
		keskmineHind = 0
		if aeg < (len(elektriAndmed)-(kasutusAeg-1)):
			for keskmiseHinnaTund in range(aeg, aeg+kasutusAeg):
				#print("Keskmine "+str(aeg)+": Lisan "+list(elektriAndmed.keys())[keskmiseHinnaTund].strftime("[%H:%M (%d.%m.%Y)]")+" hinna ("+str(elektriAndmed[list(elektriAndmed.keys())[keskmiseHinnaTund]]["Hind"])+")")
				keskmineHind += elektriAndmed[list(elektriAndmed.keys())[keskmiseHinnaTund]]["Hind"]
			elektriAndmed[list(elektriAndmed.keys())[aeg]]["Jooksev "+str(kasutusAeg)+". Tunni Keskmine"]=keskmineHind/kasutusAeg
			#print("Keskmine Hind: "+str(elektriAndmed[list(elektriAndmed.keys())[aeg]]["Jooksev "+str(kasutusAeg)+". Tunni Keskmine"]))
		else:
			for keskmiseHinnaTund in range(aeg, len(elektriAndmed)):
				#print("Poolik Keskmine "+str(aeg)+": Lisan "+list(elektriAndmed.keys())[keskmiseHinnaTund].strftime("[%H:%M (%d.%m.%Y)]")+" hinna ("+str(elektriAndmed[list(elektriAndmed.keys())[keskmiseHinnaTund]]["Hind"])+")")
				keskmineHind += elektriAndmed[list(elektriAndmed.keys())[keskmiseHinnaTund]]["Hind"]
			elektriAndmed[list(elektriAndmed.keys())[aeg]]["Jooksev "+str(kasutusAeg)+". Tunni Keskmine"]=keskmineHind/(len(elektriAndmed)-aeg)
			#print("Keskmine Hind: "+str(elektriAndmed[list(elektriAndmed.keys())[aeg]]["Jooksev "+str(kasutusAeg)+". Tunni Keskmine"]))



def lülitaSoodsaimalKeskmiselTunnilSisse(elektriAndmed, kasutusAeg, seadmeNimi):
	'''
	Lülitab Kõikidel Tundidel Elektri Välja Peale Jooksva Keskmise
	kasutusAeg on tundides, kaua elekter sees on
	'''
	print(seadmeNimi+": Otsin Soodsaimat Aega Elektri Sisse Märkimiseks")
	soodsaimaElektriAeg = 0
	for aeg in range(len(elektriAndmed)):
		if elektriAndmed[list(elektriAndmed.keys())[aeg]]["Jooksev "+str(kasutusAeg)+". Tunni Keskmine"] < elektriAndmed[list(elektriAndmed.keys())[soodsaimaElektriAeg]]["Jooksev "+str(kasutusAeg)+". Tunni Keskmine"] and (aeg+kasutusAeg-1) < len(elektriAndmed):
			for keskmiseAjad in range(soodsaimaElektriAeg, soodsaimaElektriAeg+kasutusAeg):
				elektriAndmed[list(elektriAndmed.keys())[keskmiseAjad]][seadmeNimi] = False
			soodsaimaElektriAeg = aeg
			for keskmiseAjad in range(aeg, aeg+kasutusAeg):
				#print("Lülitan "+list(elektriAndmed.keys())[keskmiseAjad].strftime("%H:%M (%d.%m.%Y)")+" Elektri Sisse, Kuna Jooksev Keskmine on "+str(round(elektriMaksustamine(elektriAndmed[list(elektriAndmed.keys())[aeg]]["Jooksev "+str(kasutusAeg)+". Tunni Keskmine"]),2))+"¢/kWh!")
				elektriAndmed[list(elektriAndmed.keys())[keskmiseAjad]][seadmeNimi] = True
	print("Soodsaim "+str(kasutusAeg)+"t keskmine on "+str(round(elektriMaksustamine(elektriAndmed[list(elektriAndmed.keys())[soodsaimaElektriAeg]]["Jooksev "+str(kasutusAeg)+". Tunni Keskmine"]),2))+list(elektriAndmed.keys())[soodsaimaElektriAeg].strftime("¢/kWh [%H:%M (%d.%m.%Y)]"))
	print("Lülitan Elektri "+list(elektriAndmed.keys())[soodsaimaElektriAeg].strftime("%H:%M (%d.%m.%Y) - ")+(list(elektriAndmed.keys())[soodsaimaElektriAeg+(kasutusAeg-1)]+timedelta(hours=1)).strftime("%H:%M (%d.%m.%Y) Sisse!"))



def lülitaElekter(elektriAndmed, olek, seade):
	for aeg in range(len(elektriAndmed)):
		elektriAndmed[list(elektriAndmed.keys())[aeg]][seade]=olek
	if olek:
		print(seade+": Elekter Sisse Märgitud")
	else:
		print(seade+": Elekter Välja Märgitud")





####################################################################################################
#	STATISTIKA TUGIFUNKTSIOONID																	   #
####################################################################################################
def statistika(elektriAndmed, seade):
	keskmineHind={"summa":0,"kogus":len(elektriAndmed),"tulemus":0}
	seesHind={"summa":0,"kogus":0,"tulemus":0}
	väljasHind={"summa":0,"kogus":0,"tulemus":0}
	for aeg in range(len(elektriAndmed)):
		keskmineHind["summa"]+=elektriAndmed[list(elektriAndmed.keys())[aeg]]["Hind"]
		if elektriAndmed[list(elektriAndmed.keys())[aeg]][seade]:
			seesHind["summa"]+=elektriAndmed[list(elektriAndmed.keys())[aeg]]["Hind"]
			seesHind["kogus"]+=1
		else:
			väljasHind["summa"]+=elektriAndmed[list(elektriAndmed.keys())[aeg]]["Hind"]
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
	lisaJooksevKeskmineHind(kõikHinnad,akudeMaht)
	lisaJooksevKeskmineHind(kõikHinnad,2)
	print("\n--------------------------------------------------")
	print("HINNA ANALÜÜS")
	print("--------------------------------------------------")
	lülitaElekter(kõikHinnad, True, "Paul-Kontor")
	for seade in ajutisedRadiaatorid:
		lülitaElekter(kõikHinnad, True, seade)
		lülitaHinnaTeravikulElekterVälja(kõikHinnad, 30, akudeMaht, seade)
	lülitaElekter(kõikHinnad, False, ajutisedSeadmed[0])
	lülitaSoodsaimalKeskmiselTunnilSisse(kõikHinnad,2,ajutisedSeadmed[0])
	print("\n--------------------------------------------------")
	print("STATISTIKA")
	print("--------------------------------------------------")
	statistika(kõikHinnad,ajutisedRadiaatorid[0])
	print("\n--------------------------------------------------")
	print("SALVESTAMINE")
	print("--------------------------------------------------")
	salvestaJooksevInfo(jooksevFail,kõikHinnad)
	print("\n--------------------------------------------------")
	print("ARHIVEERIN")
	print("--------------------------------------------------")
	salvestaArhiiviInfo(arhiiviKaust,kõikHinnad)
	if silumine:
		sys.exit(1)
