import csv
import pandas as pd
import requests
from datetime import datetime
import argparse

def read_csv_data():
    # Open the CSV file
    with open('vehicles.csv', 'r', encoding="utf-8-sig") as csv_file:
        # Read the CSV data using the DictReader function
        csvreader = csv.DictReader(csv_file)

        # Convert the CSV data to a list of dictionaries
        rows = list(csvreader)
        return rows

def generate_excel(args):

    csv_data = read_csv_data()

    response = requests.post('http://127.0.0.1:5000/upload-csv', json=csv_data)

    # Parse server response and convert it to a DataFrame
    data = response.json()
    
    res_df = pd.DataFrame(data)

    # Sort dataframe by "gruppe" column
    res_df.sort_values('gruppe', inplace=True)
    
    
    # Define columns to include in output
    keys = ['rnr'] + args.keys if args.keys else ['rnr']

    if args.colored:
        res_df = color_cells_with_hu(res_df)
        style = True
    else:
        style = None

     # If labelIds are given and at least one colorCode could be resolved,
    # use the first colorCode to tint the cell's text (if labelIds is given in -k)
    if 'labelIds' in keys:
        res_df = color_cells_with_labelIds(res_df,keys)
 

    # Select only the desired columns and write to Excel file
    filename = 'vehicles_{}.xlsx'.format(datetime.now().strftime('%Y-%m-%d'))
    res_df.to_excel(filename, index=False)
    
    # Apply cell coloring if the "-c" flag is True
    if style is not None:
        # Create Excel file and save DataFrame as a worksheet in the workbook
        filename = f'vehicles_{datetime.today().strftime("%Y-%m-%d")}.xlsx'
        writer = pd.ExcelWriter(filename, engine='openpyxl')
        res_df.to_excel(writer, sheet_name='Sheet1', index=False)

        # Save the Excel file
        writer.save()


def color_cells_with_hu(res_df):
    colors = {
            'green': '#007500',
            'orange': '#FFA500',
            'red': '#b30000'
        }
    def get_color(row):
            diff = datetime.today() - datetime.strptime(row['hu'], '%Y-%m-%d')

            if diff.days <= 90:
                return colors['green']
            elif diff.days <= 365:
                return colors['orange']
            else:
                return colors['red']

    res_df['color'] = res_df.apply(get_color, axis=1)
    res_df = res_df.style.applymap(lambda x: f'background-color: {x}', subset=pd.IndexSlice[:, ['color']])

    return res_df


def color_cells_with_labelIds(res_df,keys):
    color_codes = list(set(res_df['colorCode']))
    if len(color_codes) > 0:
        color_code = color_codes[0]
        res_df['labelIds'] = res_df['labelIds'].apply(lambda x: f'\033[38;5;{color_code}m{x}\033[0m' if x else '')
    string_df = res_df.to_string(index=False, columns=keys)
    return string_df


# Define input arguments
parser = argparse.ArgumentParser()
parser.add_argument('-k', '--keys', nargs='*', help='Additional columns to include in the output')
parser.add_argument('-c', '--colored', action='store_true',default=True, help='Color rows based on "hu" value')
args = parser.parse_args()

generate_excel(args)
