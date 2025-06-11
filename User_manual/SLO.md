Za nalaganje datotek na platformo uporabimo SD kartico za glasbo in USB ključek za video/slikovne vsebine.
***

# Zvočni učinki
Datoteke za zvočne učinke se bodo predvajale, ko stopimo na stopnico. V primeru, da se trenutna skladba še ni končala, in stopimo na naslednjo stopnico, potem bo trenutna skladba prekinjena in nova se bo predjvala.

## SD kartica
Opozorila:
- Na SD kartici naj bo največ 25 skladb (ker je 25 stopnic vse skupaj).
  - SD kartico je potrebno v primeru nakupa nova SD kartice ponastaviti s pomočjo "SD Card Formatter".
- Skladbe morajo biti v formatu MP3.
  - To lahko preverite tako, da:
    * kliknete enkrat na datoteko (skladbo) z levim klikom
    * nato enkrat z desnim klikom
    * na dnu okenca kliknete "Lastnosti".
    * Če vidite kje napisano ".mp3", potem je datoteka pripravljena
  - V primeru, da vaša datoteka ni v formatu MP3, lahko vašo datoteko pretvorite v MP3 s pomočjo https://online-audio-converter.com/
***
# Vizualni učinki
Datoteke za vizualne učinke se bodo predvajale glede na vaša navodila na USB ključku.
Možni vizualni učinki oz. aplikacije so:
- Enostavno mešanje barv
  - Vsak korak na stopnico doda eno barvo. Ko dosežemo mejo za barve, je prikazan rezultat. 
- Kompleksno mešanje barv
  - Vsak korak na stopnico doda eno barvo. Rezultat je prikazan sproti, aplikacija se ne konča, razen če uporabnik to zahteva
- Enačba
  - Korak na primerno stopnico predstavlja vnos rešitve. Pri tem lahko uporabimo le prvih deset stopnic (za vnos številk 0-9).
  - V primeru, da želimo vnesti večmestno številko, to storimo tako, da stopimo na stopnico za vnos vsake števke od leve proti desni.
- Povezovanje slik in besed
- Stopmotion
- Slideshow

Opozorilo: Za izbiro barve uporabite: https://g.co/kgs/LrNHnkX . S pomočjo okna in drsnika izberite barvo in prekopirajte napis zapisan pod "HEX" (npr. #fcba03).

## Ukazi za vizualne učinke
Svoja navodila napišete tako, da v tekstovno datoteko "izvedba" vpišete ukaze v obliki, ki je primerna za aplikacijo:
- Enostavno mešanje barv: `barve:simple;število_možnih_vnosov!barva_hex_1,barva_hex_2`
  - Do vsake izmed napisanih HEX barv lahko dostopamo z eno stopnico.
  - primer: `barve:simple;3!#eb4034,#eb4034,#495446,#aba295,#8a6a91`
- Kompleksno mešanje barv: `barve:complex;število_možnih_vnosov!barva_hex_1,barva_hex_2`
  - Do vsake izmed napisanih HEX barv lahko dostopamo z eno stopnico.
  - primer: `barve:complex;3!#eb4034,#eb4034,#495446,#aba295,#8a6a91`
- Enačba:
  - primer: enacba:naloga1;1+49__=50$49
- Povezovanje slik in besed:
  - primer: besedilna:naloga1;papagaj$3
- Stopmotion:
  - primer: stopmotion:prva_animacija;1
- Slideshow:
  - slideshow:ponedeljek;3$3

## Preikus ukazov za vizualne učinke

## USB ključek
Opozorila:
- USB ključek mora biti imenovan "stopnice"
  - USB ključek lahko preimenujete tako, da:
    * odprete Raziskovalec (ikona z mapico)
    * na levi strani najdete vstavljen USB ključek
    * enkrat z levim klikom kliknete na USB ključek
    * enkrat z desnim klikom kliknete na USB ključek
    * v oknu izberete "Preimenuj"
    * preminujete v "stopnice". Vse z majhnimi črkami!

Prekinitev delovanja aplikacije brez konca (kompleksno mešanje barv, stopmotion, slideshow) dosežemo tako, da petkrat stopmino na zadnjo (25.) stopnico. Program ponovno zaženemo tako, da petkrat stopimo na tretjo (3.) stopnico. 
