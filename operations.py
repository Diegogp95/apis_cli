import requests
import os, sys
from dotenv import load_dotenv
import json
from InfoMap import InfoMap

# Cargar variables de entorno
load_dotenv()



####### Funciones auxiliares

def save_token(portafolio, token, config_file_path):
    # Cargar datos existentes desde el archivo (o un diccionario vacío si el archivo está vacío o no existe)
    try:
        with open(config_file_path, 'r') as config_file:
            data = json.load(config_file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    if portafolio == "GPM":
        data["gpm_token"] = token
    elif portafolio == "AlsoEnergy":
        data["alsoenergy_token"] = token
    else:
        print("Error: Portafolio no reconocido.")
        sys.exit(1)

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

def write_data_to_file(file_head, data, relevant_items, mode, prefix=''):
    output_path = os.path.join(os.path.dirname(__file__), "output/" + prefix + "output.json")
    output_path_raw = os.path.join(os.path.dirname(__file__), "output/" + prefix + "output_raw.json")
    with open(output_path_raw, "w") as output_file:
        json.dump(
            {**file_head, "data": data},
            output_file,
            indent=2,
            ensure_ascii=False
        )

    output_data = []
    for item in data:
        item_data = {}
        try:
            for key in relevant_items:
                item_data[key] = item[key]
            output_data.append(item_data)
            if mode == 'static':
                print("\n==================================================\n")
                for key, value in item_data.items():
                    print(f"\t{key}: {value}")
        except KeyError:
            pass

    if mode == 'static': print("\n==================================================\n")

    with open(output_path, "w") as output_file:
        json.dump(
                  {**file_head, "data": output_data},
                  output_file,
                  indent=2,
                  ensure_ascii=False)

    if mode == 'static': print(f"Datos de elementos guardados en {output_path}")

def load_token(portafolio, config_file_path):
    with open(config_file_path, "r") as config_file:
        data = json.load(config_file)
    try:
        if portafolio == "GPM":
            return data["gpm_token"]
        elif portafolio == "AlsoEnergy":
            return data["alsoenergy_token"]
        else:
            print("Error: Portafolio no reconocido.")
            sys.exit(1)
    except KeyError:
        return ""


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
            response = requests.post(url, headers=InfoMap[portafolio]['headers-auth'], data=data)
            response.raise_for_status()
            token = response.json()["access_token"]
        save_token(portafolio, token, config_file_path)
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
    url = InfoMap[portafolio]["paths"]["BASE"] + InfoMap[portafolio]["paths"]["ALLDATASOURCES"].format(
        plant_id=plant_id)
    headers = InfoMap[portafolio]["headers"]
    token = load_token(portafolio, config_file_path)
    headers["Authorization"] = f"Bearer {token}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        return None
    
    DATA = response.json()
    relevant_items = ["DataSourceName", "DataSourceId"]
    write_data_to_file({'PlantId': plant_id}, DATA, relevant_items, mode, prefix='alldatasources_')
    return

def datasource(portafolio, config_file_path, plant_id, element_id, mode='static'):
    if portafolio == "GPM":
        url = InfoMap[portafolio]["paths"]["BASE"] + InfoMap[portafolio]["paths"]["DATASOURCE"].format(
            plant_id=plant_id, element_id=element_id)
    elif portafolio == "AlsoEnergy":
        url = InfoMap[portafolio]["paths"]["BASE"] + InfoMap[portafolio]["paths"]["COMPONENTS"].format(
            hardwareId=element_id)
    headers = InfoMap[portafolio]["headers"]
    token = load_token(portafolio, config_file_path)
    headers["Authorization"] = f"Bearer {token}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        return None
    
    DATA = response.json()
    if portafolio == "GPM":
        relevant_items = ["DataSourceName", "DataSourceId"]
    elif portafolio == "AlsoEnergy":
        relevant_items = ["dataName", "name"]
        DATA = [item for nested_dict in DATA["registerGroups"] for item in nested_dict["registers"]]
    write_data_to_file({'PlantId': plant_id, 'ElementId': element_id},
                       DATA, relevant_items, mode,
                       prefix='datasources_' if portafolio == "GPM" else 'components_')
    return


#### ESPECIFICO PARA GPM
def ping(portafolio, config_file_path):
    if portafolio != "GPM":
        print("Ping no disponible para este portafolio.")
        return
    url = InfoMap[portafolio]["paths"]["BASE"] + InfoMap[portafolio]["paths"]["PING"]
    headers = InfoMap[portafolio]["headers"]
    token = load_token(portafolio, config_file_path)
    headers["Authorization"] = f"Bearer {token}"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return True
    except requests.exceptions.HTTPError as err:
        print(err)
        return False
    
def plants(portafolio, config_file_path, alert_count=False, mode='static'):
    if portafolio == "GPM":
        url = InfoMap[portafolio]["paths"]["BASE"] + InfoMap[portafolio]["paths"]["PLANTS"]
    elif portafolio == "AlsoEnergy":
        url = InfoMap[portafolio]["paths"]["BASE"] + InfoMap[portafolio]["paths"]["SITES"]
    headers = InfoMap[portafolio]["headers"]
    token = load_token(portafolio, config_file_path)
    headers["Authorization"] = f"Bearer {token}"
    if alert_count and portafolio == "AlsoEnergy":
        url = url + "?withAlertCounts=true"
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
    if portafolio == "GPM":
        relevant_items = ["Name", "Id", "ElementCount"]
    elif portafolio == "AlsoEnergy":
        relevant_items = ["siteId", "siteName"]
        DATA = DATA["items"]
    write_data_to_file({}, DATA, relevant_items, mode, prefix='plants_' if portafolio == "GPM" else 'sites_')
    return

def elements(portafolio, config_file_path, plant_id, mode='static', includeArchivedFields=False,
             includeAlertCounts=False, includeAlertINfo=False, includeDisabledHardware=False,
             includeSummaryFields=False, includeDeviceConfig=False, includeDataNameFields=False,):
    if portafolio == "GPM":
        url = InfoMap[portafolio]["paths"]["BASE"] + InfoMap[portafolio]["paths"]["ELEMENTS"].format(
            plant_id=plant_id)
    elif portafolio == "AlsoEnergy":
        url = InfoMap[portafolio]["paths"]["BASE"] + InfoMap[portafolio]["paths"]["HARDWARE"].format(
            siteId=plant_id)
    headers = InfoMap[portafolio]["headers"]
    token = load_token(portafolio, config_file_path)
    headers["Authorization"] = f"Bearer {token}"
    try:
        if portafolio == "AlsoEnergy":
            params = {
                "includeArchivedFields": includeArchivedFields,
                "includeAlertCounts": includeAlertCounts,
                "includeAlertInfo": includeAlertINfo,
                "includeDisabledHardware": includeDisabledHardware,
                "includeSummaryFields": includeSummaryFields,
                "includeDeviceConfig": includeDeviceConfig,
                "includeDataNameFields": includeDataNameFields
            }
            response = requests.get(url, headers=headers, params=params)
        elif portafolio == "GPM":
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
    if portafolio == "GPM":
        relevant_items = ["Name", "Identifier", "TypeString"]

    elif portafolio == "AlsoEnergy":
        relevant_items = ["id", "name"]
        DATA = DATA["hardware"]

    write_data_to_file(file_head, DATA, relevant_items, mode,
                       prefix='elements_' if portafolio == "GPM" else 'hardware_')
    return

def get_data(portafolio, config_file_path, start_date, end_date, datasource_ids=None,
            site_id=None, hardware_id=None, field=None, grouping="minutes",
            granularity=15, aggregation=1, bin_size="Bin15min", tz=None, func='Avg',
            also_query_file=None, mode='static'):
    url = InfoMap[portafolio]["paths"]["BASE"] + InfoMap[portafolio]["paths"]["DATA"]
    headers = InfoMap[portafolio]["headers"]
    token = load_token(portafolio, config_file_path)
    headers["Authorization"] = f"Bearer {token}"

    if portafolio == "GPM":
        datasource_ids = ",".join(map(str, datasource_ids))

        params = {
            "dataSourceIds": datasource_ids,
            "startDate": start_date,
            "endDate": end_date,
            "grouping": grouping,
            "granularity": granularity,
            "aggregationType": aggregation
        }
        body = None

    elif portafolio == "AlsoEnergy":
        if also_query_file:
            with open(also_query_file, 'r') as query_file:
                query_data = json.load(query_file)
            body = [
                {
                    "siteId": query["siteId"],
                    "hardwareId": query["hardwareId"],
                    "fieldName": query["fieldName"],
                    "function": query["function"]
                } for query in query_data
            ]

        else:
            body = [{
                "siteId": int(site_id),
                "hardwareId": int(hardware_id),
                "fieldName": field,
                "function": func
            }]

        params = {
            "from": start_date,
            "to": end_date,
            "binSizes": bin_size,
        }
        if tz:
            params["tz"] = tz
        

    try:
        if portafolio == "GPM":
            response = requests.get(url, headers=headers, params=params)
        elif portafolio == "AlsoEnergy":
            # print(params, body)
            response = requests.post(url, headers=headers, params=params, json=body)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
        return None
    except requests.exceptions.RequestException as err:
        print(err)
        return None

    try:
        DATA = response.json()
    except json.JSONDecodeError as err:
        print(response.status_code)
        raise err

    if mode == 'pipe': return DATA
    
    if portafolio == "GPM":
        relevant_items = ["DataSourceId", "Date", "Value"]
    elif portafolio == "AlsoEnergy":
        relevant_items = ["timestamp", "data"]
        info = DATA["info"]
        DATA = DATA["items"]

    write_data_to_file({}, DATA, relevant_items, mode, prefix='data_')