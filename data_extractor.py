import argparse
import json
import os
import tkinter as tk
from tkinter import scrolledtext

def extract_data(file, key, value, stdout=False,output=None):
    with open(file, 'r') as f:
        data = json.load(f)

    results = [item for item in data['data'] if key in item and str(value).lower() in str(item[key]).lower()]

    print(f'Found {len(results)} results')  # Print the number of results

    result_str = '\n'.join([f'=====================\n{json.dumps(item, indent=4)}\n=====================' for item in results])


    if not stdout:
        root = tk.Tk()

        # Create a new window for the scrolled text
        result_window = tk.Toplevel(root)
        result_window.title("Resultados")

        # Set the window size
        result_window.geometry("1000x1200")

        # Create a ScrolledText widget
        text_area = scrolledtext.ScrolledText(result_window, wrap = tk.WORD, width = 40, height = 10)
        text_area.pack(fill = tk.BOTH, expand = True)

        # Insert the result string into the text area
        text_area.insert(tk.INSERT, result_str)

        # Hide the root window
        root.withdraw()

        # This line is necessary to display the Tkinter window
        result_window.protocol("WM_DELETE_WINDOW", root.quit)  # This line will make the program stop if the result window is closed
        result_window.mainloop()
        root.destroy()  # This line will ensure that the Tkinter process ends when the window is closed

        if output:
            path = os.path.join(os.path.dirname(__file__), "output", output)
            with open(path, 'a') as f:
                json.dump(results, f)

    else:
        print(result_str)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extraer datos de un archivo JSON.')
    parser.add_argument('file', help='El archivo JSON a leer.')
    parser.add_argument('key', help='La llave a buscar.')
    parser.add_argument('value', help='El valor a buscar.')
    parser.add_argument('-o', '--output', help='El archivo de salida donde guardar los resultados.')

    args = parser.parse_args()

    extract_data(args.file, args.key, args.value, args.output)
