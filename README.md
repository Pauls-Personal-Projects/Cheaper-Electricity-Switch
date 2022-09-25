# Smarter-Electricity-Usage

### 🇬🇧
##### This is an Internet of Things Electricity Market Project that combines cheap Smart Plugs with Automated Python Scripts to Minimize the Use of Electricity at Peak Price Hours.

#### 🔌 “Smart” Plugs

There are countless of Smart Plugs on the market these days and I did not conduct any research into which one would be the best. This project uses Osram/Ledvance’s [Smart+ Wifi](https://www.ledvance.com/consumer/products/smart-home/smart-components/smart-wifi/smart-indoor-components-with-wifi-technology/smart-plugs-with-wifi-technology/plug-with-smart-socket-to-control-non-smart-devices-with-wifi-technology--pairable-with-remote-controller-c6482)  Plugs, because **A:** *These work with most smart home services* and **B:** *It was widely available and cheap at 17€ in* [*Bauhaus*](https://www.bauhaus.ee/nutipistikupesa-ledvance-smart-wifi-plug-eu.html). Plus, it offered some other neat features like tracking the current and monthly power usage.

#### 🐍 Smarter Script

Since Ledvance does not provide an API for controlling their devices, I had to figure out another way. While I would have preferred using *Google Home* or *Amazon’s Alexa* as the middleman, ***Samsung’s*** [***SmartThings***](https://www.smartthings.com/) ended up offering the easiest solution. As for the price of electricity, [***Elering’s***](https://elering.ee/en) [***API***](https://dashboard.elering.ee/assets/api-doc.html) provides a quick and easy access to [*Nord Pool’s*](https://www.nordpoolgroup.com/) Day-Ahead prices. The only bit left was to figure out an algorithm that would deduce when is the price too high.

### 🇪🇪

##### See on Asjade Interneti Elektrituru Projekt, mis ühildab soodsad Nutipistikud Automatiseeritud Püütoni Skriptidega selleks, et Kasutada Vähem Elektrit Hinna Tipptundidel.

#### 🔌 “Nutipistikud”

Kuigi tänaseks on müügile jõudnud hulk erinevaid nutipistikuid, siis mingit uuringut parima tuvastamiseks ma läbi ei viinud. Selles projektis ma kasutasin Osram/Ledvance [Smart+ Wifi](https://www.ledvance.com/consumer/products/smart-home/smart-components/smart-wifi/smart-indoor-components-with-wifi-technology/smart-plugs-with-wifi-technology/plug-with-smart-socket-to-control-non-smart-devices-with-wifi-technology--pairable-with-remote-controller-c6482)  Nutipistikuid, kuna **A:** *Need töötavad enamus nutikodu teenustega* ja **B:** *need on laialdaselt saadaval ja soodsad 17€ kandis* [*Bauhausis*](https://www.bauhaus.ee/nutipistikupesa-ledvance-smart-wifi-plug-eu.html). Lisaks, on neil paar kasulikku lisafunktsiooni, nagu hetke ja kuu elektritarbimise jälgimine.

#### 🐍 Nutikam Skript

Kuna Ledvance ei paku rakenduseliidest seadmete juhtimiseks, pidin leidma teise tee. Kuigi ma oleksin eelistanud *Google Home* või *Amazoni Alexat* vahendajana, siis ***Samsungi*** [***SmartThings***](https://www.smartthings.com/) pakkus kõige lihtsamat lahendust. Elektrihinna saamiseks kasutan [***Eleringi***](https://elering.ee/) [***rakenduseliidest***](https://dashboard.elering.ee/assets/api-doc.html), mis pakub kiire ja lihtsa ligipääsu [*Nord Pooli*](https://www.nordpoolgroup.com/) Päev Ette Hindadele. Viimane pusletükk oli välja mõelda algoritm mis otsustaks millal on hind liiga kõrge tarbimiseks.

## Images / Pildid

![Price_Script](/Price_Script.PNG)

## Contributing / Toetamine
Open to any tips and feedback!

## Credits / Tänusõnad
- [elektrikell](https://www.elektrikell.ee/) tool by [Gridio](https://www.gridio.io/) where I discovered the Elering API
- [pysmartthings](https://github.com/andrewsayre/pysmartthings) library by [Andrew Sayre](https://github.com/andrewsayre)
- [light-control](https://github.com/grantlemons/light-control) example by [Grant Lemons](https://github.com/grantlemons)

## License / Litsents
[MIT](https://choosealicense.com/licenses/mit/)
