#!/usr/bin/env python3
# -*- coding: utf-8 -*-

####################################################################################################
#                                                                                                  #
#                                            GOOGLE KALENDER                                       #
#                                                                                                  #
####################################################################################################
'''
Looja:      Paul J. Aru - https://github.com/paulpall
Kuupäev:    09/05/2023
Uuendatud:  20/05/2023
------------------------------------------------------------
Tänud    Google, quickstart näite loomise eest
Link: https://developers.google.com/calendar/api/quickstart/python
'''





####################################################################################################
#    TEEGID                                                                                        #
####################################################################################################
from __future__ import print_function                   # Google Calendar APIga Ühendumiseks.
import os                                               # Failide Salvestamiseks ja Lugemiseks.
from datetime import datetime, timedelta                # Ürituste Kuupäeva Formaatimiseks.
from dateutil import tz, parser                         # Ürituste Kuupäeva Formaatimiseks.
from google.auth.transport.requests import Request      # Google Calendar APIga Ühendumiseks.
from google.oauth2.credentials import Credentials       # Google Calendar APIga Ühendumiseks.
from google_auth_oauthlib.flow import InstalledAppFlow  # Google Calendar APIga Ühendumiseks.
from googleapiclient.discovery import build             # Google Calendar APIga Ühendumiseks.
from googleapiclient.errors import HttpError            # Google Calendar APIga Ühendumiseks.
from Lülitaja import silumine                           # Veateate Edastamiseks Synology DSM'ile.





####################################################################################################
#    SÄTTED                                                                                        #
####################################################################################################
# API Õiguseid Muutes Kustuta Google-Volitus.json.
GOOGLE_API_VOLI = ['https://www.googleapis.com/auth/calendar']
#GOOGLE_VOLITUS = "Võtmed/Google-Volitus.json" #IDE Kaust
GOOGLE_VOLITUS = "/volume1/homes/Paul/Drive/Projektid/Elektrihind/Võtmed/Google-Volitus.json" #Pilve Kaust
#GOOGLE_API = "Võtmed/Google-API.json" #IDE Kaust
GOOGLE_API = "/volume1/homes/Paul/Drive/Projektid/Elektrihind/Võtmed/Google-API.json" #Pilve Kaust





####################################################################################################
#   GOOGLE KALENDER                                                                                #
####################################################################################################
def _ava_google_kalender():
    '''
	Loob Ühenduse Google Kalendri APIga ja Edastab Selle
    Ülejäänud Kalendrit Kasutavatele Funktsioonidele.
	'''
    mandaat = None
    if os.path.exists(GOOGLE_VOLITUS):
        mandaat = Credentials.from_authorized_user_file(GOOGLE_VOLITUS, GOOGLE_API_VOLI)
    #Google API Sisenemis/Kinnitus Leht
    if not mandaat or not mandaat.valid:
        if mandaat and mandaat.expired and mandaat.refresh_token:
            mandaat.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                GOOGLE_API, GOOGLE_API_VOLI)
            mandaat = flow.run_local_server(port=0)
        #Salvestab Mandaadi
        with open(GOOGLE_VOLITUS, 'w', encoding='utf-8') as token:
            token.write(mandaat.to_json())
    return build('calendar', 'v3', credentials=mandaat)



def kasutus_hetk(seadme_nimi:str):
    '''
	Kontrollib Google Kalendrist Kas Seadme Nimega Kalendris
    On Hetkeks Loodud Üritusi, Kus on Kättesaadavus Määratud Hõivatuks;
    Osutades Seadme Mitte Kasutamisele.
	'''
    try:
        google_kalender = _ava_google_kalender()
        kalendrite_päring = google_kalender.calendarList().list().execute()
        kalendrid = kalendrite_päring.get('items', [])
        hetke_aeg = datetime.now(tz=tz.gettz('Europe/Tallinn'))
        for kalender in kalendrid:
            if seadme_nimi not in kalender["summary"]:
                continue
            kalendri_id=[{"id": kalender["id"]}]
            hõivatud_vahemikud = google_kalender.freebusy().query(body=
                {"timeMin": (hetke_aeg
                     -timedelta(hours=1)).replace(tzinfo=None).isoformat()
                     + 'Z',
                "timeMax": (hetke_aeg
                     +timedelta(hours=1)).replace(tzinfo=None).isoformat()
                     + 'Z',
                "timeZone": 'Europe/Tallinn',
                "items": kalendri_id
                }).execute()
            for üritus in hõivatud_vahemikud["calendars"][kalender["id"]]["busy"]:
                if (parser.parse(üritus["start"]) <= hetke_aeg
                    and hetke_aeg <= parser.parse(üritus["end"])):
                    print("Google Kalender:",seadme_nimi,"Kasutuseta",
                      üritus["start"], "-", üritus["end"])
                    return False
        return True
    except HttpError as vea_teade:
        print("VIGA: Google Kalender ("+str(vea_teade)+")")
        global silumine
        silumine = True





def üritus_olemas(alg_aeg:datetime, lõpp_aeg:datetime, seadme_nimi:str, ürituse_nimi:str):
    '''
	Kontrollib Google Kalendrist Kas Seadme Nimega Kalendris
    On Antud Ajaks Juba Loodud Teavitus Üritus.
	'''
    try:
        google_kalender = _ava_google_kalender()
        kalendrite_päring = google_kalender.calendarList().list().execute()
        kalendrid = kalendrite_päring.get('items', [])
        seade_leitud = False
        for kalender in kalendrid:
            if seadme_nimi not in kalender['summary']:
                continue
            seade_leitud = True
            ürituste_päring = google_kalender.events().list(calendarId=kalender['id'],
            timeMin=alg_aeg.astimezone(tz.tzutc()).replace(tzinfo=None).isoformat()+ 'Z',
            timeMax=lõpp_aeg.astimezone(tz.tzutc()).replace(tzinfo=None).isoformat()+ 'Z',
            maxResults=1, singleEvents=True, orderBy='startTime').execute()
            üritused = ürituste_päring.get('items', [])
            if not üritused:
                print("Google Kalender:","Kell",alg_aeg.strftime("%H:%M (%d.%m.%Y)"),
                      "Üritusi Kirjas Ei Ole."+" ["+kalender['summary']+"]")
                return False
            for üritus in üritused:
                if üritus['summary'] == ürituse_nimi:
                    print("Google Kalender:", alg_aeg.strftime("%H:%M (%d.%m.%Y)"),
                          "-", lõpp_aeg.strftime("%H:%M (%d.%m.%Y)"),"on", üritus['summary'])
                    return True
            return False
        if not seade_leitud:
            print("Google Kalender:",seadme_nimi, "Kalendrit Ei Leitud!")
    except HttpError as vea_teade:
        print("VIGA: Google Kalender ("+str(vea_teade)+")")
        print(kalender['summary'],"id on",kalender['id'])
        global silumine
        silumine = True





def loo_üritus(alg_aeg:datetime, lõpp_aeg:datetime, seadme_nimi:str, väärtus:bool, kirjeldus:str, nimi:str):
    '''
	Loob Uue Kalendri Ürituse Seadme Nimega Google Kalendris.
	'''
    üritus = {
      'summary': nimi,
      'location': seadme_nimi.split('-')[0],
      'description': kirjeldus,
      'start': {
        'dateTime': alg_aeg.isoformat(),
        'timeZone': 'Europe/Tallinn',
      },
      'end': {
        'dateTime': lõpp_aeg.isoformat(),
        'timeZone': 'Europe/Tallinn',
      },
      'transparency': "transparent",
      'reminders': {
        'useDefault': False,
        'overrides': [
          {'method': 'popup', 'minutes': 10},
        ],
      },
    }
    if väärtus:
        üritus['colorId'] = 10 #Roheline
    else:
        üritus['colorId'] = 11 #Punane

    try:
        google = _ava_google_kalender()
        kalendrite_päring = google.calendarList().list().execute()
        kalendrid = kalendrite_päring.get('items', [])
        seade_leitud = False
        for kalender in kalendrid:
            if seadme_nimi not in kalender['summary']:
                continue
            seade_leitud = True

            üritus = google.events().insert(calendarId=kalender['id'], body=üritus).execute()
            print("Kalendri Üritus Loodud: "+üritus.get('htmlLink'))
        if not seade_leitud:
            print("Google Kalender:",seadme_nimi, "Kalendrit Ei Leitud!")
    except HttpError as vea_teade:
        print("VIGA: Google Kalender ("+str(vea_teade)+")")
        print(kalender['summary'],"id on",kalender['id'])
        global silumine
        silumine = True
