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
    print("Error: scraped_company_data.csv not found! Run clean.py first.")
    exit()

# Extract Key Information using Gemini LLM
def extract_info_with_gemini(text):
    model = genai.GenerativeModel("gemini-2.0-pro-exp")

    prompt = f"""
    From the data given, pull out the information for the below given questions:
    1. What is the Company's mission statement or core values?
    2. What are the products or services that the company offers?
    3. When was the company founded, and who were the founders?
    4. Where is the company's headquarters located?
    5. Who are the key executives or leadership team members?
    6. Has the company received any notable awards or recognitions?
    
    Text: {text}
    
    Provide the answers in a structured JSON format with the following fields:
    {{
        "company": <company_name>,
        "mission_statement_or_core_values": <value>,
        "products_or_services": <value>,
        "founding_details": <value>,
        "headquarters_location": <value>,
        "key_executives_or_leadership": <value>,
        "notable_awards_or_recognitions": <value>
    }}
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

# Parse the JSON data from the extracted information
extracted_data = json.loads(extracted_info.replace('```json\n', '').replace('```', '').strip())

# Prepare data for DataFrame
rows = []
companies = ['Cisco', 'BP', 'Accenture', 'Visa', 'GSK']  # List of companies to match extracted data

for company in companies:
    # Find the company in the extracted data
    company_data = next((item for item in extracted_data if item['company'].lower() == company.lower()), None)
    
    if company_data:
        row = {
            'Company': company,
            'What is the Company\'s mission statement or core values?': company_data.get('mission_statement_or_core_values', 'Not found'),
            'What are the products or services that the company offers?': ', '.join(company_data['products_or_services'].split(', ')) if isinstance(company_data.get('products_or_services'), str) else company_data.get('products_or_services', 'Not found'),
            'When was the company founded, and who were the founders?': company_data.get('founding_details', 'Not found'),
            'Where is the company\'s headquarters located?': company_data.get('headquarters_location', 'Not found'),
            'Who are the key executives or leadership team members?': company_data.get('key_executives_or_leadership', 'Not found'),
            'Has the company received any notable awards or recognitions?': company_data.get('notable_awards_or_recognitions', 'Not found')
        }
    else:
        # If no company data found, fill with 'Not found' values
        row = {
            'Company': company,
            'What is the Company\'s mission statement or core values?': 'Not found',
            'What are the products or services that the company offers?': 'Not found',
            'When was the company founded, and who were the founders?': 'Not found',
            'Where is the company\'s headquarters located?': 'Not found',
            'Who are the key executives or leadership team members?': 'Not found',
            'Has the company received any notable awards or recognitions?': 'Not found'
        }
    
    rows.append(row)

# Create DataFrame with questions as columns
df = pd.DataFrame(rows)

# Save to Excel
excel_file = "company_details.xlsx"
df.to_excel(excel_file, index=False)

print(f"\nData successfully saved to {excel_file}!")
print("\nSample of saved data:")
print(df.head())
