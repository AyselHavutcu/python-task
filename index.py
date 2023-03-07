import pandas as pd
import requests
import openpyxl
from datetime import datetime

def generate_excel(keys, colored):
    # Read CSV file into a pandas DataFrame
    df = pd.read_csv('vehicles.csv', sep='delimiter', header=None)

    # Convert DataFrame to JSON object and send it to the REST API
    json_data = {"csv_file" : df.to_json(orient='records') }
    response = requests.post('http://127.0.0.1:5000/process-csv', json=json_data)

    # Parse server response and convert it to a DataFrame
    data = response.json()
    res_df = pd.DataFrame(data)

    # Filter DataFrame to only include columns specified in 'keys'
    col_list = ['rnr', 'gruppe', 'hu']
    if keys:
        col_list.extend(keys)
    res_df = res_df[col_list]

    # Apply color to DataFrame if 'colored' is True
    if colored:
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

    # Sort DataFrame by 'gruppe'
    res_df = res_df.sort_values(by='gruppe')

    # Create Excel file and save DataFrame as a worksheet in the workbook
    filename = f'vehicles_{datetime.today().strftime("%Y-%m-%d")}.xlsx'
    writer = pd.ExcelWriter(filename, engine='openpyxl')
    res_df.to_excel(writer, sheet_name='Sheet1', index=False)

    # Save the Excel file
    writer.save()

# Example usage
keys = ['kurzname', 'info']
colored = True
generate_excel(keys, colored)
