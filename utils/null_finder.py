import json

def find_nulls_in_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)

    null_values = []
    for item in data:
        if 'timestamp' in item:
            null_keys = [k for k, v in item.items() if v is None]
            if null_keys:
                null_values.append({ 'timestamp': item['timestamp'], 'null_keys': null_keys })

    

    return null_values