import google.generativeai as genai
import pandas as pd
import json

# Configure Google Gemini API
genai.configure(api_key="AIzaSyASY90fGTzSOiEs6u9Fu3ed0y-2cxegDPs") 
 
# Read cleaned data from file
try:
    with open("scraped_company_data.csv", "r", encoding="utf-8") as file:
        cleaned_text = file.read()
except FileNotFoundError:
    print("Error: cleaned_data.txt not found! Run clean.py first.")
    exit()
 
# Extract Key Information using Gemini LLM
def extract_info_with_gemini(text):
    model = genai.GenerativeModel("gemini-2.0-pro-exp") 
 
 
 
    prompt = f"""
    From the data given, pull out the informations for the below given questions
    What is the Company's mission statement or core values?
    what are the Products or services that the company offers?
    When was the company founded, and who were the founders?
    Where is the company's headquarters located?
    Who are the key executives or leadership team members?
    Has the company received any notable awards or recognitions?
 
    Text: {text}
 
    Provide the answers in structured JSON format.
    """
 
    try:
        response = model.generate_content(prompt)
        if response and response.text:
            return response.text.strip()
        else:
            return "No relevant information found."
    except Exception as e:
        print(f"Error extracting info: {e}")
        return "Extraction failed."
 
# Run extraction
extracted_info = extract_info_with_gemini(cleaned_text)
 
# Debugging: Print extracted data
print("\nExtracted Information:\n", extracted_info)
 
# Save Data to CSV
#df = pd.DataFrame([["https://www.cisco.com/", extracted_info]], columns=["Website", "Extracted Information"])
#df.to_csv("extracted_company_data.csv", index=False)
 
#print("\n✅ Data successfully saved to extracted_company_info.csv!")



# Parse the JSON data from the extracted information
extracted_data = json.loads(extracted_info.replace('```json\n', '').replace('```', '').strip())

# Prepare data for DataFrame
rows = []
for company, details in extracted_data.items():
    row = {
        'Company': company,
        'Website': f"https://www.{company.lower()}.com/",
        'Mission Statement': details.get('mission_statement_or_core_values', 'Not found'),
        'Products/Services': ', '.join(details['products_or_services']) if isinstance(details.get('products_or_services'), list) else details.get('products_or_services', 'Not found'),
        'Founded': details.get('founding_details', 'Not found'),
        'Headquarters': details.get('headquarters_location', 'Not found'),
        'Key Executives': ', '.join(details['key_executives_or_leadership']) if isinstance(details.get('key_executives_or_leadership'), list) else details.get('key_executives_or_leadership', 'Not found'),
        'Awards/Recognitions': ', '.join(details['notable_awards_or_recognitions']) if isinstance(details.get('notable_awards_or_recognitions'), list) else details.get('notable_awards_or_recognitions', 'Not found')
    }
    rows.append(row)

# Create DataFrame
df = pd.DataFrame(rows)

# Reorder columns
column_order = [
    'Company',
    'Website',
    'Mission Statement',
    'Products/Services',
    'Founded',
    'Headquarters',
    'Key Executives',
    'Awards/Recognitions'
]
df = df[column_order]

# Save to Excel
excel_file = "company_details.xlsx"
df.to_excel(excel_file, index=False)

print(f"\n Data successfully saved to {excel_file}!")
print("\n Sample of saved data:")
print(df.head())