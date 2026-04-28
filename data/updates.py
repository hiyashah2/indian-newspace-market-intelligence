import pandas as pd
import re

file_path = 'data/indian_space_startups.csv'
df = pd.read_csv(file_path)
df.set_index('Company', inplace=True)

updates = {
    'Bellatrix Aerospace': {'Total_Funding_USD_Est': '$34.4M', 'Last_Funding_Date': '2026', 'Funding_Round_Type': 'Series A'},
    'GalaxEye': {'Total_Funding_USD_Est': '$18.8M', 'Last_Funding_Date': '2026'},
    'Digantara': {'Total_Funding_USD_Est': '$100M+', 'Last_Funding_Date': '2026', 'Funding_Round_Type': 'Series B'},
    'TakeMe2Space': {'Total_Funding_USD_Est': '$5.0M', 'Last_Funding_Date': '2026'},
    'SatLeo Labs': {'Last_Funding_Date': '2026'},
    'SpaceFields': {'Last_Funding_Date': '2025', 'Funding_Round_Type': 'Pre-Series A'},
    'OrbitAID Aerospace': {'Total_Funding_USD_Est': '$1.5M', 'Funding_Round_Type': 'Pre-Seed', 'Last_Funding_Date': '2025'},
    'PierSight': {'Total_Funding_USD_Est': '$6.0M'},
    'Paras Defence': {'Funding_Round_Type': 'IPO (Mainboard)'},
    'Data Patterns': {'Employees_Range': '1001-5000'}
}

for company, changes in updates.items():
    if company in df.index:
        for column, value in changes.items():
            df.at[company, column] = value

def clean_year(val):
    match = re.search(r'\d{4}', str(val))
    return match.group(0) if match else val

df['Last_Funding_Date'] = df['Last_Funding_Date'].apply(clean_year)

df.reset_index(inplace=True)
df.to_csv(file_path, index=False)

print("Success! Data updated and dates cleaned to years only.")
