
# Zvočni učinki
Datoteke za zvočne učinke se bodo predvajale, ko stopimo na stopnico. V primeru, da se trenutna skladba še ni končala, in stopimo na naslednjo stopnico, potem bo trenutna skladba prekinjena in nova se bo predjvala.
Za prenos datotek za zvočne učinke na napravo uporabimo SD kartico.

### SD kartica
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
  - Korak na primerno stopnico (1 do x) predstavlja vnos rešitve
  - Slike morajo biti poimenovane s številko
  - Beseda mora biti v obliki sliki in poimenovana enako kot v ukazu
- Stopmotion
  - Začnemo s prvo sliko
  - Premik na naslednjo sliko dosežemo s korakom na naslednjo stopnico
  - Sliko lahko premaknemo nazaj s korakom na prješnjo stopnico
- Slideshow
  - Samodejno predvajanje videoposnetkov in/ali slik
  - Nastavljiv način

Opozorilo: Za izbiro barve uporabite Color Picker na Googlu: https://g.co/kgs/LrNHnkX . S pomočjo okna in drsnika izberite barvo in prekopirajte napis zapisan pod "HEX" (npr. #fcba03).

### Ukazi za vizualne učinke
Svoja navodila napišete tako, da v tekstovno datoteko "izvedba" vpišete ukaze v obliki, ki je primerna za aplikacijo:
- Enostavno mešanje barv: `barve:simple;število_možnih_vnosov!barva_hex_1,barva_hex_2`
  - Do vsake izmed napisanih HEX barv lahko dostopamo z eno stopnico.
  - primer: `barve:simple;3!#eb4034,#eb4034,#495446,#aba295,#8a6a91`
**slika primera**
- Kompleksno mešanje barv: `barve:complex;število_možnih_vnosov!barva_hex_1,barva_hex_2`
  - Do vsake izmed napisanih HEX barv lahko dostopamo z eno stopnico.
  - primer: `barve:complex;3!#eb4034,#eb4034,#495446,#aba295,#8a6a91`
**slika primera**
- Enačba: `enacba:ime_mape_s_slikami_stevilk;x+y_=z$resitev`
  - pri računu nam `_` skrije rešitev, vendar mora biti toliko znakov kot števk v rešitvi.
  - skrijemo lahko katerikoli del enačbe
  - na koncu moramo zapisati rešitev po `$`
  - primer: `enacba:naloga1;1+__=50$49`
**slika primera**
- Povezovanje slik in besed: `besedilna:ime_mape_s_slikami;ime_slike_z_napisom$stevilka_slike_ki_je_pravilna`
  - primer: `besedilna:naloga1;papagaj$3`
**slika primera**
- Stopmotion: `stopmotion:ime_mape_z_vsebino;neki?`
  - primer: `stopmotion:prva_animacija;1`
- Slideshow: `slideshow:ime_mape_z_vsebino;koliko_casa_naj_prikazuje_sliko$nacin_predvajanja`
  - nacini predvajanja:
    - 1 = le enkrat predvajaj samo slike
    - 2 = le enkrat predvajaj samo videoposnetke
    - 3 = le enkrat predvajaj slike in videoposnetke
    - 4 = ponavljaj predvajanje samo slik
    - 5 = ponavljaj predvajanje samo videposnetkov
    - 6 = ponavljaj predvajanje slik in videoposnetkov
  - primer `slideshow:ponedeljek;3$3`

### Preizkus ukazov za vizualne učinke

### USB ključek
Opozorila:
- USB ključek mora biti imenovan "stopnice"
  - USB ključek lahko preimenujete tako, da:
    * odprete Raziskovalec (ikona z mapico)
    * na levi strani najdete vstavljen USB ključek
    * enkrat z levim klikom kliknete na USB ključek
    * enkrat z desnim klikom kliknete na USB ključek
    * v oknu izberete "Preimenuj"
    * preminujete v "stopnice". Vse z majhnimi črkami!

#### Gradivo za naloge
Na USB ključku morate imeti vedno mape:
- besedilna
- enacba
- stopmomtion
- slideshow

in datoteko "izvedba.txt".
To je ključno, saj ukaz za nalogo bo iskal v točno imenovani mapi gradivo. Znotraj mape za posamezno vrsto naloge morate ustvariti svoje mape s poljubnim imenom, v katere lahko shranjujete slike (ali videje), ki so poimenovane primerno za ukaze.

**slika ureditve USB ključka tukaj**

# Delovanje naprave
Naprava je sestavljena iz dveh delov:
- prvi spremlja korakanje po stopnicah in predvaja zvok
- drugi prejema podatke o korakanju po stopnicah in prikazuje vizualne učinke

### Zvok/projekcija
Oba dela naprave se ob vklopu naprave povežeta. Za vklop zvoka je potrebno stikalo za zvok premakniti na noto. Za vklop prikaza je potrebno stikalo za prikaz premakniti na projekcijo.

### Manjkajoč USB
Ob vklopu drugi del naprave prebere vsebino USB ključka in samodejno začne z izvajanjem nalog. V primeru, da USB ključek ob vklopu ni vstavljen ali pa če USB ključek med delovanjem odstranite, se bo prikazalo ozadje (PEF logo). Če USB ni bil vstavljen ob vklopu, se bo program samodejno zagnal nekaj sekund po vstavitvi USB ključka. Če ste USB ključek odstranili med delovanjem naprave ali pa po zaključku delovanja programa, je potrebno po ponovni vstavitvi program ponovno zagnati (glej naslednje poglavje).

### Prekinitev in ponovni zagon
Prekinitev delovanja aplikacije brez konca (kompleksno mešanje barv, stopmotion, slideshow) dosežemo tako, da petkrat zapored stopimo na zadnjo (25.) stopnico. Program ponovno zaženemo tako, da petkrat stopimo na tretjo (3.) stopnico.

Če želimo napravo ponovno zagnati, je potrebno stikalo za vklop naprave premakniti v lego, da bo spodnji del notri pritisnjen (ugasnjeno stanje), nato počakati vsaj 5 sekund in nato premakniti stikalo v nasprotno pozicijo (vklopljeno stanje).

### Težave
V primeru, da naprava za projekcijo ne bo imela povezave z napravo za zvok in branje stanja stopnic, bo na projekciji prikazan napis "". V tem primeru je potrebno ponovno zagnati napravo za projekcijo ali celotno napravo.

# Okolje za preizkus gradiva za didaktične stopnice

Okolje za preizkus gradiva za didaktične stopnice je obliki programske datoeke (.exe), ki jo lahko zaženemo z dvojnim levim klikom na datoteko.
Za preizkus je potrebno imeti gradivo pripravljeno na USB ključku, kot bi želeli zadevo pognati na nameščeni opremi na stopnišču (imenovanje, datoteke...).
Tekom preizkušanja je mišljeno, da vnose stopnic simuliramo preko tipkovnice s pritiskom na tipko. Med pritiski pustite nekaj časa za uspešno procesiranje vnosa. Za izhod lahko namesto vnosa "25" pritisnete tipko "ESC", pri čemer je še vedno potrebno pritisniti omenjeno tipko petkrat.
Na koncu preizkusa bo prikazan logotip Pedagoške Fakultete. V primeru vnosa obstaja možnost, da se bo okno "sesulo", ker je konec programa. V primeru nenavadnega delovanja, lahko zaprete okno s pomočjo miške.
-Opozorilo: uporaba tipkovnice je onemogočena v času delovanja programa, zato karkoli vnesete preko tipkovnice, bo program kot njemu namenjen vnos.
-Opozorilo: program je trenutno prilagojen le za Windows okolje.
