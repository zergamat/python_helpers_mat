import configparser
import inspect
import requests
import re
import json
import subprocess

def wczytaj_ini(plik_ini, czy_debug=False):
    """
    Wczytuje dane z pliku INI.

    Args:
        plik_ini (str): Ścieżka do pliku INI.
        czy_debug (bool, optional): Flaga włączająca tryb debugowania. Defaults to False.
    """

    config = configparser.ConfigParser()
    config.optionxform = str
    config.read(plik_ini)

    if czy_debug:
        print(f"### FUNKCJA {inspect.currentframe().f_code.co_name}")
        print(f"###Odczyt danych z pliku INI ({plik_ini}):")
        for sekcja in config.sections():
            print(f"###  Sekcja: {sekcja}")
            for klucz, wartosc in config.items(sekcja):
                print(f"###    {klucz}: {wartosc}")

    return config

def zapisz_ini(plik_ini, dane_ini, czy_debug=False):
    """
    Zapisuje dane do pliku INI.

    Args:
        plik_ini (str): Ścieżka do pliku INI.
        dane_ini (dict): Słownik zawierający dane do zapisania.
        czy_debug (bool, optional): Flaga włączająca tryb debugowania. Defaults to False.
    """

    config = configparser.ConfigParser()
    config.optionxform = str
    for sekcja, opcje in dane_ini.items():
        config[sekcja] = opcje

    with open(plik_ini, 'w') as plik:
        config.write(plik)

    if czy_debug:
        print(f"### FUNKCJA {inspect.currentframe().f_code.co_name}")
        print(f"###Zapis danych do pliku INI ({plik_ini}):")
        for sekcja in config.sections():
            print(f"###  Sekcja: {sekcja}")
            for klucz, wartosc in config.items(sekcja):
                print(f"###    {klucz}: {wartosc}")

def pobierz_dane(url, czy_debug=False):
    """
    Pobiera dane ze strony internetowej i zwraca je w postaci listy słowników.

    Args:
        url: Adres URL strony internetowej.
        czy_debug: Flaga określająca, czy włączyć tryb debugowania (domyślnie False).

    Returns:
        Lista słowników, gdzie każdy słownik reprezentuje parę 
        "value": wartość, "nazwa": nazwa.
    """

    try:
        if czy_debug:
            print(f"### FUNKCJA {inspect.currentframe().f_code.co_name}")
            print(f"###Pobieram dane z: {url}")

        response = requests.get(url)
        response.raise_for_status()

        html = response.text
        if czy_debug:
            print(f"###Pierwsze 100 znaków HTML: {html[:100]}")

        wzorzec = r"&zwnj;([^;]+); &zwnj;([^;]+);"
        if czy_debug:
            print(f"###Wzorzec wyrażenia regularnego: {wzorzec}")

        wyniki = re.findall(wzorzec, html)

        dane = []
        for wartosc, nazwa in wyniki:
            dane.append({"value": wartosc, "nazwa": nazwa})
            if czy_debug:
                print(f"###Dodano parę: {wartosc}, {nazwa}")

        if czy_debug:
            print(f"###Znaleziono {len(dane)} par.")

        return dane

    except requests.exceptions.RequestException as e:
        if czy_debug:
            print(f"###Błąd podczas pobierania strony: {e}")
        return None
    
def publikuj_dane_mqtt(dane, temat_bazowy, czy_debug=False):
    """
    Publikuje dane do brokera MQTT. Każda para value-nazwa 
    jest publikowana jako osobny obiekt JSON w osobnym temacie.

    Args:
        dane: Lista słowników z danymi do opublikowania.
        temat_bazowy: Bazowy temat MQTT.
        czy_debug: Flaga określająca, czy włączyć tryb debugowania (domyślnie False).
    """

    try:
        if czy_debug:
            print(f"### FUNKCJA {inspect.currentframe().f_code.co_name}")
            print(f"###Dane wejściowe: {dane}")
            print(f"###Temat bazowy: {temat_bazowy}, wysyłam:")

        for element in dane:
            temat = f"{temat_bazowy}/{element['nazwa']}"
            wiadomosc = json.dumps({"value": element['value']})

            if czy_debug:
                print(f"###{temat}, wiadomość: {wiadomosc}")

            polecenie = [
                "mosquitto_pub",
                "-t", temat,
                "-m", wiadomosc,
                "-q", "1",
                "-r",  # Retain flag
            ]

            subprocess.run(polecenie, check=True)

    except subprocess.CalledProcessError as e:
        print(f"###Błąd podczas publikowania danych MQTT: {e}")



def pobierz_wartosc_z_ini(plik_ini, klucz, czy_debug=False):
    """
    Pobiera wartość z pliku INI na podstawie klucza, przeszukując wszystkie sekcje.

    Args:
        plik_ini: Ścieżka do pliku INI lub adres URL.
        klucz: Klucz, którego wartość ma zostać pobrana.
        czy_debug: Flaga określająca, czy włączyć tryb debugowania.

    Returns:
        Wartość skojarzona z kluczem lub None w przypadku błędu.
    """

    try:
        config = configparser.ConfigParser()
        if czy_debug:
            print(f"Odczytuję plik INI: {plik_ini}")

        if plik_ini.startswith("http"):
            if czy_debug:
                print("Pobieram plik INI z URL...")
            response = requests.get(plik_ini)
            response.raise_for_status()
            config.read_string(response.text)
        else:
            if czy_debug:
                print("Odczytuję plik INI z lokalnego systemu...")
            config.read(plik_ini)

        if czy_debug:
            print(f"Dostępne sekcje: {config.sections()}")

        for sekcja in config.sections():
            if czy_debug:
                print(f"Sprawdzam sekcję: {sekcja}")
            if config.has_option(sekcja, klucz):
                wartosc = config.get(sekcja, klucz)
                if czy_debug:
                    print(f"Znaleziono wartość dla klucza '{klucz}' w sekcji '{sekcja}': {wartosc}")
                break
        else:
            if czy_debug:
                print(f"Brak klucza '{klucz}' w żadnej sekcji.")
            return None

        # Usuń komentarze, białe znaki i znaki '
        wartosc = wartosc.split(';')[0].strip().replace("'", "")
        return wartosc

    except requests.exceptions.RequestException as e:
        if czy_debug:
            print(f"Błąd podczas pobierania pliku INI z URL: {e}")
        return None
    except configparser.Error as e:
        if czy_debug:
            print(f"Błąd podczas parsowania pliku INI: {e}")
        return None