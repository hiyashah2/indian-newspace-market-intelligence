import pandas as pd

# 1. Load the dataset
df = pd.read_csv('/Users/hiyashah/Documents/indian-newspace-market-intelligence/data/indian_space_startups.csv')

# Set 'Company' as index for easy targeting
df.set_index('Company', inplace=True)

# 2. Update Bellatrix Aerospace
df.at['Bellatrix Aerospace', 'Total_Funding_USD_Est'] = '$34.4M'
df.at['Bellatrix Aerospace', 'Last_Funding_Date'] = 'Mar-2026'
df.at['Bellatrix Aerospace', 'Funding_Round_Type'] = 'Series A'

# 3. Update GalaxEye
df.at['GalaxEye', 'Total_Funding_USD_Est'] = '$18.8M'
df.at['GalaxEye', 'Last_Funding_Date'] = 'Mar-2026'

# 4. Update Digantara
df.at['Digantara', 'Total_Funding_USD_Est'] = '$100M+'
df.at['Digantara', 'Last_Funding_Date'] = 'Apr-2026'
df.at['Digantara', 'Funding_Round_Type'] = 'Series B'

# 5. Update TakeMe2Space (Correcting overestimation and date)
df.at['TakeMe2Space', 'Total_Funding_USD_Est'] = '$5.0M'
df.at['TakeMe2Space', 'Last_Funding_Date'] = 'Jan-2026'

# 6. Update SatLeo Labs
df.at['SatLeo Labs', 'Last_Funding_Date'] = 'Apr-2026'

# 7. Update SpaceFields
df.at['SpaceFields', 'Last_Funding_Date'] = 'Sep-2025'
df.at['SpaceFields', 'Funding_Round_Type'] = 'Pre-Series A'

# 8. Update OrbitAID Aerospace
df.at['OrbitAID Aerospace', 'Total_Funding_USD_Est'] = '$1.5M'
df.at['OrbitAID Aerospace', 'Funding_Round_Type'] = 'Pre-Seed'
df.at['OrbitAID Aerospace', 'Last_Funding_Date'] = 'Jan-2025'

# 9. Update PierSight (Adjusting to verified $6M seed)
df.at['PierSight', 'Total_Funding_USD_Est'] = '$6.0M'

# 10. Update Listing/Employee Details for Public Companies
df.at['Paras Defence', 'Funding_Round_Type'] = 'IPO (Mainboard)'
df.at['Data Patterns', 'Employees_Range'] = '1001-5000'

# 11. Reset index and save the updated file
df.reset_index(inplace=True)
df.to_csv('indian_space_startups_updated.csv', index=False)

print("Updates complete! Saved as 'indian_space_startups_updated.csv'")