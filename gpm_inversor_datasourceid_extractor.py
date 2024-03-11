import requests, sys, os, json
from dotenv import load_dotenv
from InfoMap import InfoMap
import subprocess

def main():
    # subprocess.run(["python", "api_explorer.py", "-o", "ELEMENTS", "--plant-id", "44"])

    with open("output/output_raw.json", "r") as file:
        data = json.load(file)
    
    with open(os.path.join(os.path.dirname(__file__), "config.json"), "r") as file:
        config = json.load(file)
    token = config["token"]

    plant_id = 44
    elements = {}
    cts = 3
    inverters_per_ct = 15
    
    url = InfoMap["GPM"]["paths"]["BASE"] + InfoMap["GPM"]["paths"]["DATASOURCE"]
    headers = InfoMap["GPM"]["headers"]
    headers["Authorization"] = f"Bearer {token}"

    for i in range(1,cts+1):
        for j in range(1,inverters_per_ct+1):
            found = False
            element = {}
            for entry in data["data"]:
                if j<10:
                    if f"Inverter_{i}.0{j}" in entry["Name"]:
                        element["DataSourceName"] = f"Inversor CT{i}.0{j}"
                        element["ElementId"] = entry["Identifier"]
                        found = True
                        break
                else:
                    if f"Inverter_{i}.{j}" in entry["Name"]:
                        element["DataSourceName"] = f"Inversor CT{i}.{j}"
                        element["ElementId"] = entry["Identifier"]
                        found = True
                        break
            if not found:
                print(f"Entry for CT0{i} - Inversor {j} not found.")
            else:
                elements[f"inv{inverters_per_ct*(i-1)+j}"] = element
    
    for element in list(elements.values()):
        try:
            response = requests.get(url.format(plant_id, element["ElementId"]), headers=headers)
            response.raise_for_status()
        
        except requests.exceptions.HTTPError as err:
            print(err)
            return None
        
        DATA = response.json()

        found = False
        for entry in DATA:
            if entry["DataSourceName"] == "POTENCIA ACTIVA":
                element["DataSourceId"] = entry["DataSourceId"]
                found = True
                break
        if not found:
            print(f"Entry for {element['DataSourceName']} - POTENCIA ACTIVA not found.")
        
    with open("output/extracted_data_sources.json", "w") as file:
        json.dump(elements, file, indent=4)


if __name__ == "__main__":
    main()