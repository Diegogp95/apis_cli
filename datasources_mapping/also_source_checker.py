from .DataSourceMap import DataSourceMap
import requests, sys, os, json
from dotenv import load_dotenv
from InfoMap import InfoMap

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)


def main(argv):
    existing_plants = InfoMap["AlsoEnergy"]["plants"]
    if argv[0] =='all':
        plants = existing_plants.keys()
    else:
        for plant in argv:
            if plant not in existing_plants.keys():
                print(f"La planta {plant} no existe.")
                print("Las plantas disponibles son:\n\t", existing_plants.keys())
                sys.exit(1)
        plants = argv

    with open(os.path.join(os.path.dirname(__file__), "../config.json"), "r") as file:
        data = json.load(file)
    token = data["token"]

    url = InfoMap["AlsoEnergy"]["paths"]["BASE"] + InfoMap["AlsoEnergy"]["paths"]["HARDWARE"]
    headers = InfoMap["AlsoEnergy"]["headers"]
    headers["Authorization"] = f"Bearer {token}"

    url2 = InfoMap["AlsoEnergy"]["paths"]["BASE"] + InfoMap["AlsoEnergy"]["paths"]["COMPONENTS"]

    for plant in plants:
        plant_id = existing_plants[plant]
        try:
            response = requests.get(url.format(siteId=plant_id), headers=headers)
            response.raise_for_status()
        
        except requests.exceptions.HTTPError as err:
            print(err)
            return None

        DATA = response.json()["hardware"]

        print(
f'''====================================================================================

\tPlant: \t{plant}
''')

        print("{:<20} {:<15} {:<15} {:<30} {:<45} {:<30}\n".format(
            "Field", "ElementId", "fieldName", "Local Name", "Remote Name", "Element Name"))

        for _, sub_dict in DataSourceMap["AlsoEnergy"][plant].items():
            for field, prop_dict in sub_dict.items():
                found = False
                if prop_dict is None:
                    continue
                for entry in DATA:
                    found = False
                    if entry["id"] == prop_dict["hardwareId"]:
                        elementName = entry["name"]
                        try:
                            response = requests.get(url2.format(hardwareId=entry["id"]), headers=headers)
                            response.raise_for_status()
                            DATA2 = response.json()
                            DATA2 = [item for nested_dict in DATA2["registerGroups"] for item in nested_dict["registers"]]
                        except requests.exceptions.HTTPError as err:
                            try:
                                response = requests.get(url2.format(hardwareId=entry["id"]), headers=headers)
                                response.raise_for_status()
                                DATA2 = response.json()
                                DATA2 = [item for nested_dict in DATA2["registerGroups"] for item in nested_dict["registers"]]
                            except requests.exceptions.HTTPError as err:
                                print(err)
                                return None
                        remoteName = "\033[91mNot found\033[0m" + " " * 20
                        for component in DATA2:
                            try:
                                if component["dataName"] == prop_dict["fieldName"]:
                                    remoteName = component["name"]
                                    break
                            except KeyError:
                                continue
                                
                        print("{:<20} {:<15} {:<15} {:<30} {:<30} {:<30}".format(
                            field, prop_dict["hardwareId"], prop_dict['fieldName'], prop_dict['DataSourceName'],
                            remoteName, elementName))
                        found = True
                        break
                if not found:
                    print(f"Entry for {field} \033[91mnot found\033[0m.")
        print("\n")


if __name__ == "__main__":
    main(sys.argv[1:])