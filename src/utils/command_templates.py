from dataclasses import dataclass


@dataclass
class CommandTemplate:
    command: str
    examples: list[str]
    threshold: float = 0.80


COMMAND_TEMPLATES = [
    CommandTemplate(
        command='go',
        examples=[
            # Kurze Formen ohne Artikel (schnelle Commands)
            "geh wald",
            "gehe taverne",
            "lauf norden",
            "renn weg",
            "komm zurück",

            # Mit Präposition "zum/zur"
            "geh zum wald",
            "gehe zum wald",
            "lauf zum wald",
            "renn zum wald",
            "marschiere zum wald",
            "komm zum wald",
            "geh zur taverne",
            "gehe zur taverne",
            "lauf zur taverne",
            "komm zur taverne",

            # Mit Präposition "in/in den/in die"
            "geh in den wald",
            "gehe in den wald",
            "lauf in den wald",
            "geh in die taverne",
            "gehe in die taverne",
            "lauf in die taverne",
            "renn in die taverne",

            # Mit Präposition "auf"
            "geh auf den marktplatz",
            "gehe auf den platz",
            "lauf auf den turm",

            # Mit Präposition "an"
            "geh an den see",
            "gehe an den fluss",
            "lauf an die tür",

            # Mit "nach" (Richtungen)
            "geh nach norden",
            "gehe nach norden",
            "lauf nach osten",
            "renn nach süden",

            # Ich-Form (1. Person Singular)
            "ich gehe zum wald",
            "ich gehe in die taverne",
            "ich gehe auf den marktplatz",
            "ich gehe an den see",
            "ich laufe zum wald",
            "ich renne weg",
            "ich komme zurück",

            # Wir-Form (1. Person Plural)
            "wir gehen zum wald",
            "wir gehen in die taverne",
            "wir laufen zum see",

            # Aufforderung/Vorschlag
            "lass uns zum wald gehen",
            "lass uns in die taverne gehen",
            "gehen wir zum wald",
            "gehen wir in die taverne",
            "laufen wir zum see",

            # Du-Form (Anweisung an Teammitglied)
            "geh du zum wald",
            "gehe du zur taverne",
            "lauf du zum see",
            "geh du in die taverne",

            # Infinitiv (Antwort-Stil)
            "zum wald gehen",
            "zur taverne gehen",
            "in die taverne gehen",
            "auf den marktplatz gehen",
            "an den see gehen",
            "nach norden gehen",

            # Weitere Synonyme
            "spaziere zum wald",
            "spazieren zum see",
            "schlendere zur taverne",
            "schlendern zum marktplatz",
            "eile zum ausgang",
            "eilen zur tür",
            "hetze zum wald",
            "hetzen weg",
            "flüchte zum ausgang",
            "fliehe weg",
            "zieh zum wald",
            "ziehe zur taverne",

            # Komplexe Sätze
            "geh zur taverne und rede mit dem wirt",
            "ich gehe zum wald um den see zu finden",
            "lauf schnell zur taverne",
            "gehe vorsichtig in den wald",
            "können wir zum wald gehen",
            "kann ich zur taverne gehen",
            "darf ich zum see gehen"
        ],
        threshold=0.80
    ),

    CommandTemplate(
        command='take',
        examples=[
            # Kurze Formen ohne Artikel
            "nimm schlüssel",
            "hole schlüssel",
            "hol schlüssel",
            "pack schlüssel",
            "greif schlüssel",
            "sammel schlüssel",
            "heb schlüssel auf",

            # Mit Artikel (den/das/die)
            "nimm den schlüssel",
            "nimm das buch",
            "nimm die fackel",
            "hole den beutel",
            "hol dir den beutel",
            "pack die fackel ein",
            "packe das seil ein",
            "sammel die münzen",
            "sammel die münzen auf",
            "heb das schwert auf",
            "hebe den hammer auf",

            # Mit "nach" (greifen nach)
            "greif nach dem schlüssel",
            "greife nach dem schwert",
            "greif nach schlüssel",

            # Ich-Form (1. Person Singular)
            "ich nehme schlüssel",
            "ich nehme den schlüssel",
            "ich hole mir schlüssel",
            "ich packe schlüssel ein",
            "ich greife nach schlüssel",
            "ich sammle münzen auf",
            "ich hebe schwert auf",

            # Wir-Form (1. Person Plural)
            "wir nehmen schlüssel",
            "wir nehmen den schlüssel",
            "wir holen uns schlüssel",

            # Vorschlag
            "lass uns schlüssel nehmen",
            "lass uns den schlüssel nehmen",

            # Du-Form (Anweisung an Teammitglied)
            "nimm du schlüssel",
            "nimm du den schlüssel",
            "hol du den beutel",
            "pack du die fackel ein",

            # Infinitiv (Antwort-Stil)
            "schlüssel nehmen",
            "den schlüssel nehmen",
            "beutel holen",
            "fackel einpacken",
            "schwert aufheben",

            # Weitere Synonyme
            "raff schlüssel auf",
            "raffe schlüssel auf",
            "schnapp schlüssel",
            "schnappe dir schlüssel",
            "schnapp dir den schlüssel",
            "klau schlüssel",
            "klaue schlüssel",
            "steck schlüssel ein",
            "stecke schlüssel ein",
            "steck den schlüssel ein",
            "ergreif schlüssel",
            "ergreife schlüssel",

            # Komplexe Sätze
            "nimm den schlüssel und öffne die truhe",
            "ich nehme den schlüssel um die truhe zu öffnen",
            "nimm schnell den schlüssel",
            "nimm vorsichtig das buch",
            "kann ich den schlüssel nehmen",
            "darf ich den schlüssel nehmen",
            "nimm alles mit",
            "nimm nicht das schwert"
        ],
        threshold=0.80
    ),

    CommandTemplate(
        command='drop',
        examples=[
            # Kurze Formen ohne Artikel
            "leg schwert ab",
            "lege schwert ab",
            "wirf schwert weg",
            "wirf schwert",
            "stell fackel hin",
            "stelle fackel hin",
            "lass schwert fallen",

            # Mit Artikel (den/das/die)
            "leg das schwert ab",
            "lege den hammer ab",
            "wirf die fackel weg",
            "wirf das seil weg",
            "stell den beutel hin",
            "stelle die laterne hin",
            "lass den hammer fallen",
            "lass das schwert fallen",

            # Ich-Form (1. Person Singular)
            "ich lege schwert ab",
            "ich lege das schwert ab",
            "ich werfe schwert weg",
            "ich werfe die fackel weg",
            "ich stelle fackel hin",
            "ich lasse schwert fallen",

            # Wir-Form (1. Person Plural)
            "wir legen schwert ab",
            "wir werfen schwert weg",
            "wir lassen schwert fallen",

            # Vorschlag
            "lass uns schwert ablegen",
            "lass uns das schwert ablegen",

            # Du-Form (Anweisung an Teammitglied)
            "leg du schwert ab",
            "leg du das schwert ab",
            "wirf du die fackel weg",
            "stell du den beutel hin",

            # Infinitiv (Antwort-Stil)
            "schwert ablegen",
            "das schwert ablegen",
            "fackel wegwerfen",
            "beutel hinstellen",
            "hammer fallen lassen",

            # Weitere Synonyme
            "entsorge schwert",
            "entsorgen schwert",
            "platziere schwert",
            "platzieren schwert hier",
            "deponiere beutel",
            "deponieren beutel hier",
            "pack schwert aus",
            "packe schwert aus",
            "lass schwert liegen",
            "lasse schwert liegen",
            "lass schwert los",

            # Komplexe Sätze
            "wirf das schwert weg und nimm den hammer",
            "ich lege das schwert ab um platz zu schaffen",
            "wirf schnell die fackel weg",
            "leg vorsichtig den hammer ab",
            "kann ich das schwert ablegen",
            "darf ich das ablegen",
            "wirf alles weg",
            "leg nicht das schwert ab"
        ],
        threshold=0.80
    ),

    CommandTemplate(
        command='use',
        examples=[
            # Kurze Formen ohne Artikel
            "benutz schlüssel",
            "benutze schlüssel",
            "verwend schlüssel",
            "verwende schlüssel",
            "nutz schlüssel",
            "nutze schlüssel",
            "öffne truhe",
            "bedien hebel",
            "bediene hebel",

            # Mit Artikel (den/das/die)
            "benutze den schlüssel",
            "verwende das seil",
            "nutze die fackel",
            "öffne die truhe",
            "öffne den kasten",
            "bediene den hebel",

            # Mit "mit" (Werkzeug/Mittel)
            "öffne truhe mit schlüssel",
            "öffne die truhe mit schlüssel",
            "öffne die truhe mit dem schlüssel",
            "benutze schlüssel an truhe",
            "verwende schlüssel für truhe",

            # Mit "an/auf" (anwenden/einsetzen)
            "wende schlüssel an",
            "wende den schlüssel an",
            "setz schlüssel ein",
            "setze schlüssel ein",
            "setze den schlüssel ein",

            # Ich-Form (1. Person Singular)
            "ich benutze schlüssel",
            "ich benutze den schlüssel",
            "ich öffne truhe",
            "ich öffne die truhe mit schlüssel",
            "ich verwende schlüssel",
            "ich bediene hebel",

            # Wir-Form (1. Person Plural)
            "wir benutzen schlüssel",
            "wir öffnen die truhe",
            "wir verwenden schlüssel",

            # Vorschlag
            "lass uns schlüssel benutzen",
            "lass uns die truhe öffnen",

            # Du-Form (Anweisung an Teammitglied)
            "benutze du schlüssel",
            "benutze du den schlüssel",
            "öffne du die truhe",
            "verwende du das seil",

            # Infinitiv (Antwort-Stil)
            "schlüssel benutzen",
            "den schlüssel benutzen",
            "truhe öffnen",
            "die truhe öffnen",
            "truhe mit schlüssel öffnen",
            "hebel bedienen",

            # Weitere Synonyme
            "aktiviere hebel",
            "aktivieren hebel",
            "betätige hebel",
            "betätigen hebel",
            "drück hebel",
            "drücke hebel",
            "zieh hebel",
            "ziehe hebel",
            "schließ truhe auf",
            "schließe truhe auf",
            "schließ die truhe auf",
            "mach truhe auf",
            "mache truhe auf",
            "krieg truhe auf",
            "kriege truhe auf",

            # Komplexe Sätze
            "benutze den schlüssel um die truhe zu öffnen",
            "öffne die truhe mit dem schlüssel und nimm das gold",
            "ich benutze den schlüssel an der truhe",
            "öffne vorsichtig die truhe",
            "benutze schnell den hebel",
            "kann ich den schlüssel benutzen",
            "darf ich die truhe öffnen",
            "öffne nicht die truhe"
        ],
        threshold=0.80
    ),

    CommandTemplate(
        command='examine',
        examples=[
            # Kurze Formen ohne Artikel
            "untersuch truhe",
            "untersuche truhe",
            "betracht truhe",
            "betrachte truhe",
            "inspizier truhe",
            "inspiziere truhe",
            "muster truhe",
            "mustere truhe",
            "prüf truhe",
            "prüfe truhe",
            "begutacht truhe",
            "begutachte truhe",
            "analysier truhe",
            "schau truhe an",
            "schaue truhe an",
            "sieh truhe an",

            # Mit Artikel (den/das/die)
            "untersuche die truhe",
            "untersuche den hammer",
            "betrachte die inschrift",
            "betrachte das buch",
            "inspiziere den schlüssel",
            "mustere die runen",
            "prüfe den mechanismus",
            "schau die truhe an",
            "schaue den hammer an",
            "sieh das buch an",

            # Ich-Form (1. Person Singular)
            "ich untersuche truhe",
            "ich untersuche die truhe",
            "ich betrachte truhe",
            "ich inspiziere truhe",
            "ich schaue truhe an",

            # Wir-Form (1. Person Plural)
            "wir untersuchen truhe",
            "wir betrachten die truhe",
            "wir schauen truhe an",

            # Vorschlag
            "lass uns truhe untersuchen",
            "lass uns die truhe untersuchen",

            # Du-Form (Anweisung an Teammitglied)
            "untersuche du truhe",
            "untersuche du die truhe",
            "betrachte du den hammer",
            "schau du die truhe an",

            # Infinitiv (Antwort-Stil)
            "truhe untersuchen",
            "die truhe untersuchen",
            "hammer betrachten",
            "inschrift mustern",
            "buch inspizieren",

            # Weitere Synonyme
            "check truhe",
            "checke truhe",
            "checken truhe",
            "kontrolliere truhe",
            "kontrollieren truhe",
            "beschau truhe",
            "beschaue truhe",
            "beäuge truhe",
            "beäugen truhe",
            "studiere truhe",
            "studieren truhe",
            "erforsche truhe",
            "erforschen truhe",
            "durchsuche truhe",
            "durchsuchen truhe",

            # Komplexe Sätze
            "untersuche die truhe genau",
            "betrachte die truhe genauer",
            "ich untersuche die truhe um hinweise zu finden",
            "schau die truhe genau an",
            "untersuche vorsichtig die truhe",
            "kann ich die truhe untersuchen",
            "darf ich das untersuchen",
            "untersuche alles",
            "untersuche nicht die truhe"
        ],
        threshold=0.80
    ),

    CommandTemplate(
        command='read',
        examples=[
            # Kurze Formen ohne Artikel
            "lies buch",
            "lese buch",
            "lies inschrift",
            "studier buch",
            "studiere text",
            "entziffr inschrift",
            "entziffere runen",

            # Mit Artikel (den/das/die)
            "lies das buch",
            "lese das buch",
            "lies die inschrift",
            "lese den brief",
            "studiere das buch",
            "studiere den text",
            "entziffere die inschrift",
            "entziffere die runen",

            # Mit Partikel (durch/vor)
            "lies buch durch",
            "lies das buch durch",
            "lese brief durch",
            "lies text vor",
            "lies den text vor",

            # Ich-Form (1. Person Singular)
            "ich lese buch",
            "ich lese das buch",
            "ich lese das buch durch",
            "ich studiere text",
            "ich entziffere inschrift",

            # Wir-Form (1. Person Plural)
            "wir lesen buch",
            "wir lesen das buch",
            "wir studieren text",

            # Vorschlag
            "lass uns buch lesen",
            "lass uns das buch lesen",

            # Du-Form (Anweisung an Teammitglied)
            "lies du buch",
            "lies du das buch",
            "lese du die inschrift",
            "studiere du den text",

            # Infinitiv (Antwort-Stil)
            "buch lesen",
            "das buch lesen",
            "inschrift lesen",
            "text studieren",
            "runen entziffern",

            # Weitere Synonyme
            "überfliege buch",
            "überfliegen buch",
            "durchstöbere buch",
            "durchstöbern buch",
            "studier text",
            "dekodiere runen",
            "dekodieren runen",
            "entschlüssle inschrift",
            "entschlüsseln inschrift",
            "deute runen",
            "deuten runen",

            # Komplexe Sätze
            "lies das buch um hinweise zu finden",
            "ich lese das buch durch um informationen zu bekommen",
            "lies das buch genau",
            "lies vorsichtig die inschrift",
            "studiere den text genauer",
            "kann ich das buch lesen",
            "darf ich das lesen",
            "lies alles",
            "lies nicht das buch"
        ],
        threshold=0.80
    ),

    CommandTemplate(
        command='talk',
        examples=[
            # Kurze Formen mit "mit"
            "sprich mit wirt",
            "rede mit wirt",
            "red mit wirt",
            "unterhalte dich mit wirt",
            "quatsch mit wirt",
            "quatsche mit wirt",
            "plauder mit wirt",
            "plaudere mit wirt",

            # Kurze Formen ohne "mit" (umgangssprachlich)
            "sprich wirt",
            "rede wirt",
            "red wirt",
            "quatsch wirt",

            # Mit Artikel (dem/der)
            "sprich mit dem wirt",
            "rede mit dem wirt",
            "red mit dem händler",
            "unterhalte dich mit dem wirt",
            "unterhalte dich mit der hexe",
            "quatsche mit dem schmied",
            "quatsche mit der wache",
            "plaudere mit dem bettler",

            # Ich-Form (1. Person Singular)
            "ich spreche mit wirt",
            "ich spreche mit dem wirt",
            "ich rede mit wirt",
            "ich rede mit dem händler",
            "ich unterhalte mich mit wirt",
            "ich quatsche mit wirt",

            # Wir-Form (1. Person Plural)
            "wir sprechen mit wirt",
            "wir sprechen mit dem wirt",
            "wir reden mit händler",

            # Vorschlag
            "lass uns mit wirt sprechen",
            "lass uns mit dem wirt reden",

            # Du-Form (Anweisung an Teammitglied)
            "sprich du mit wirt",
            "sprich du mit dem wirt",
            "rede du mit händler",
            "rede du mit dem händler",

            # Infinitiv (Antwort-Stil)
            "mit wirt sprechen",
            "mit dem wirt sprechen",
            "mit händler reden",
            "mit der hexe reden",

            # Weitere Synonyme
            "frag wirt",
            "frage wirt",
            "frag den wirt",
            "befrage wirt",
            "befragen wirt",
            "befrage den wirt",
            "konversiere mit wirt",
            "konversieren mit wirt",
            "diskutiere mit wirt",
            "diskutieren mit wirt",
            "schnack mit wirt",
            "schnacke mit wirt",

            # Komplexe Sätze
            "sprich mit dem wirt über den schlüssel",
            "ich rede mit dem händler um informationen zu bekommen",
            "rede freundlich mit dem wirt",
            "sprich höflich mit der hexe",
            "frage den wirt nach dem weg",
            "kann ich mit dem wirt sprechen",
            "darf ich mit ihm reden",
            "rede mit allen",
            "sprich nicht mit dem wirt"
        ],
        threshold=0.80
    ),

    CommandTemplate(
        command='look',
        examples=[
            # Kurze Formen (reflexiv "dich um")
            "schau dich um",
            "schaue dich um",
            "sieh dich um",
            "siehe dich um",
            "guck dich um",
            "gucke dich um",

            # Kurze Formen (nur "um")
            "schau um",
            "schaue um",
            "sieh um",
            "guck um",

            # Mit "umher"
            "schau umher",
            "schaue umher",
            "blick umher",
            "blicke umher",
            "späh umher",
            "spähe umher",

            # Allgemein (ohne Partikel)
            "schau",
            "schaue",
            "sieh",
            "guck",

            # Ich-Form (1. Person Singular)
            "ich schaue mich um",
            "ich sehe mich um",
            "ich gucke mich um",
            "ich schaue umher",
            "ich blicke umher",
            "ich schaue",

            # Wir-Form (1. Person Plural)
            "wir schauen uns um",
            "wir sehen uns um",
            "wir gucken uns um",

            # Vorschlag
            "lass uns umschauen",
            "lass uns umsehen",

            # Du-Form (Anweisung an Teammitglied)
            "schau du dich um",
            "schaue du dich um",
            "sieh du dich um",
            "guck du dich um",

            # Infinitiv (Antwort-Stil)
            "umschauen",
            "umsehen",
            "sich umschauen",
            "sich umsehen",

            # Weitere Synonyme
            "orientiere mich",
            "orientieren",
            "kundschafte aus",
            "kundschaften aus",
            "erkunde umgebung",
            "erkunden umgebung",
            "überblick verschaffen",

            # Komplexe Sätze
            "schau dich genau um",
            "ich schaue mich um um die umgebung zu erkunden",
            "schau dich vorsichtig um",
            "sieh dich aufmerksam um",
            "kann ich mich umschauen",
            "darf ich mich umsehen",
            "schau dich überall um"
        ],
        threshold=0.80
    )
]
