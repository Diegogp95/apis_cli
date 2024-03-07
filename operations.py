import requests
import os, sys
from dotenv import load_dotenv
import json
from InfoMap import InfoMap

# Cargar variables de entorno
load_dotenv()


output_path = os.path.join(os.path.dirname(__file__), "output/output.json")
output_path_raw = os.path.join(os.path.dirname(__file__), "output/output_raw.json")


####### Funciones auxiliares

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

def check_gpm_login(portafolio, config_file_path):
    if ping(portafolio, config_file_path):
        return True
    else:
        print("Ping fallido, autenticando...")
        token = auth(portafolio, config_file_path)
        if token:
            return True
        else:
            print("Error: Autenticacion fallida.")
            sys.exit(1)

def write_data_to_file(file_head, data, relevant_items, mode):
    with open(output_path_raw, "w") as output_file:
        json.dump(
            {**file_head, "data": data},
            output_file,
            indent=2,
            ensure_ascii=False
            )

    output_data = []
    for item in data:
        item_data = {
            key: item[key] for key in relevant_items
        }

        output_data.append(item_data)

        if mode == 'static':
            print("\n==================================================\n")
            for key, value in item_data.items():
                print(f"\t{key}: {value}")
    if mode == 'static': print("\n==================================================\n")

    with open(output_path, "w") as output_file:
        json.dump(
                  {**file_head, "data": output_data},
                  output_file,
                  indent=2,
                  ensure_ascii=False)

    if mode == 'static': print(f"Datos de elementos guardados en {output_path}")


####### Funciones de operaciones

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
    
def all_datasources(portafolio, config_file_path, plant_id, mode='static'):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    url = InfoMap[portafolio]["paths"]["BASE"] + InfoMap[portafolio]["paths"]["DATASOURCES"].format(plant_id)
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
    
    DATA = response.json()
    relevant_items = ["DataSourceName", "DataSourceId"]
    write_data_to_file({}, DATA, relevant_items, mode)
    return

def datasource(portafolio, config_file_path, plant_id, element_id, mode='static'):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    url = InfoMap[portafolio]["paths"]["BASE"] + InfoMap[portafolio]["paths"]["DATASOURCE"].format(plant_id, element_id)
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
    
    DATA = response.json()
    relevant_items = ["DataSourceName", "DataSourceId"]
    write_data_to_file({'PlantId': plant_id, 'ElementId': element_id},
                       DATA, relevant_items, mode)
    return


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
        response.raise_for_status()
        return True
    except requests.exceptions.HTTPError as err:
        print(err)
        return False
    
def plants(portafolio, config_file_path, mode='static'):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

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
    relevant_items = ["Name", "Id", "ElementCount"]
    write_data_to_file({}, DATA, relevant_items, mode)
    return

def elements(portafolio, config_file_path, plant_id, mode='static'):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if portafolio != "GPM":
        print("Elements no disponible para este portafolio.")
        return
    url = InfoMap[portafolio]["paths"]["BASE"] + InfoMap[portafolio]["paths"]["ELEMTNS"].format(plant_id)
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
    file_head = {
        "PlantId": plant_id,
    }

    relevant_items = ["Name", "Identifier", "TypeString"]
    write_data_to_file(file_head, DATA, relevant_items, mode)
    return