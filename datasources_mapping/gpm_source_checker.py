from .DataSourceMap import DataSourceMap
import requests, sys, os, json
from dotenv import load_dotenv
from InfoMap import InfoMap

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)


def main(argv):
    existing_plants = InfoMap["GPM"]["plants"]
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
    token = data["gpm_token"]

    url = InfoMap["GPM"]["paths"]["BASE"] + InfoMap["GPM"]["paths"]["ALLDATASOURCES"]
    headers = InfoMap["GPM"]["headers"]
    headers["Authorization"] = f"Bearer {token}"

    for plant in plants:
        plant_id = existing_plants[plant]
        try:
            response = requests.get(url.format(plant_id=plant_id), headers=headers)
            response.raise_for_status()
        
        except requests.exceptions.HTTPError as err:
            print(err)
            return None

        DATA = response.json()

        url2 = InfoMap["GPM"]["paths"]["BASE"] + InfoMap["GPM"]["paths"]["ELEMENTS"]

        try:
            response2 = requests.get(url2.format(plant_id=plant_id), headers=headers)
            response2.raise_for_status()
        
        except requests.exceptions.HTTPError as err:
            print(err)
            return None
        
        ELEMENTSDATA = response2.json()

        print(
f'''====================================================================================

\tPlant: \t{plant}
''')

        print("{:<20} {:<15} {:<15} {:<30} {:<45} {:<30}\n".format(
            "Field", "ElementId", "DataSourceId", "Local Name", "Remote Name", "Element Name"))

        for _, sub_dict in DataSourceMap["GPM"][plant].items():
            for field, prop_dict in sub_dict.items():
                found = False
                for entry in DATA:
                    found = False
                    if entry["DataSourceId"] == prop_dict["DataSourceId"]:
                        elementName = "Not found"
                        for element in ELEMENTSDATA:
                            if element["Identifier"] == entry["ElementId"]:
                                elementName = element["Name"]
                                break
                        print("{:<20} {:<15} {:<15} {:<30} {:<45} {:<30}".format(
                            field, prop_dict["ElementId"], prop_dict['DataSourceId'], prop_dict['DataSourceName'],
                            entry['DataSourceName'], elementName))
                        found = True
                        break
                if not found:
                    print(f"Entry for {field} \033[91mnot found\033[0m.")
        print("\n")
                    

            


if __name__ == "__main__":
    main(sys.argv[1:])