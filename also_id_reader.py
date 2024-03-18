import json
from unidecode import unidecode

def main():
    with open("output/output_raw.json", "r") as file:
        data = json.load(file)
    
    output_data = {}
    with open("output/also_ids.json", "w") as file:
        for entry in data["data"]:
            site_name = unidecode(entry["siteName"]).replace(" ", "_").replace("ñ", "n")
            output_data[site_name] = entry["siteId"]
        json.dump(output_data, file, indent=4, ensure_ascii=False)
    
    print("IDs de plantas guardados en output/also_ids.json")

if __name__ == "__main__":
    main()