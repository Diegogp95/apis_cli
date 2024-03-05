import requests
import os
from dotenv import load_dotenv
import json
from InfoMap import InfoMap

# Cargar variables de entorno
load_dotenv()



def auth(portafolio, config_file_path):
    username = os.getenv(f"{portafolio}_USER")
    password = os.getenv(f"{portafolio}_PASS")
    url = InfoMap[portafolio]["paths"]["BASE"] + InfoMap[portafolio]["paths"]["AUTH"]
    try:
        if portafolio == "GPM":
            data = {"username": username, "password": password}
            response = requests.post(url, headers=InfoMap[portafolio]['headers'], json=data)
            response.raise_for_status()
            token = response.json()["AccessToken"]
            expiration = response.json()["ExpiresIn"]
        elif portafolio == "AlsoEnergy":
            data = {"grant_type": "password", "username": username, "password": password}
            response = requests.post(url, headers=InfoMap[portafolio]['headers'], data=data)
            response.raise_for_status()
            token = response.json()["access_token"]
        save_token(token, config_file_path)
        if portafolio == "GPM":
            print(f"Expiracion: {expiration}")
        return token
    except requests.exceptions.HTTPError as err:
        print(err)
        return None
    except requests.exceptions.RequestException as err:
        print(err)
        return None

def save_token(token, config_file_path):
    # Cargar datos existentes desde el archivo (o un diccionario vacío si el archivo está vacío o no existe)
    try:
        with open(config_file_path, 'r') as config_file:
            data = json.load(config_file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    data["token"] = token

    # Escribir el diccionario actualizado
    with open(config_file_path, 'w') as config_file:
        json.dump(data, config_file, indent=2)

    # Imprimir
    with open(config_file_path, 'r') as config_file:
        updated_data = json.load(config_file)
        for key, value in updated_data.items():
            print(f'\t{key}: {value}')


#### ESPECIFICO PARA GPM
def ping(portafolio, config_file_path):
    if portafolio != "GPM":
        print("Ping no disponible para este portafolio.")
        return
    url = InfoMap[portafolio]["paths"]["BASE"] + InfoMap[portafolio]["paths"]["PING"]
    headers = InfoMap[portafolio]["headers"]
    with open(config_file_path, "r") as config_file:
        data = json.load(config_file)
    token = data["token"]
    headers["Authorization"] = f"Bearer {token}"

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.exceptions.HTTPError as err:
        print(err)
        return False
    
def plants(portafolio, config_file_path, mode='short'):
    output_path = os.path.join(os.path.dirname(__file__), "output/gpm_plants.json")
    if portafolio != "GPM":
        print("Plants no disponible para este portafolio.")
        return
    url = InfoMap[portafolio]["paths"]["BASE"] + InfoMap[portafolio]["paths"]["PLANTS"]
    headers = InfoMap[portafolio]["headers"]
    with open(config_file_path, "r") as config_file:
        data = json.load(config_file)
    token = data["token"]
    headers["Authorization"] = f"Bearer {token}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        return None
    except requests.exceptions.RequestException as err:
        print(err)
        return None
    
    DATA = response.json()

    for item in DATA:
        if mode == 'short':
            print(
f'''
\tNombre: {item["Name"]}
\tId: {item["Id"]}
\tTotal elementos: {item["ElementCount"]}
'''
                )
        elif mode == 'long':
            with open(output_path, "a") as output_file:
                output_data = {
                    "Nombre": item["Name"],
                    "Id": item["Id"],
                    "Total elementos": item["ElementCount"],
                    "Unique Id": item["UniqueID"]
                }
                for parameter in DATA["Parameters"].items():
                    output_data[parameter['key']] = parameter['value']
            print(f"Datos de plantas guardados en {output_path}")
        
        else:
            print("Modo no reconocido.")
            return

    return