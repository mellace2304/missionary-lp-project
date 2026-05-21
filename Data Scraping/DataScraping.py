import re
import csv
import time
import random
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def extract_urls_from_file(file_path):
    """Extract URLs from the data.txt file"""
    urls = []
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        # Extract URLs from option values
        pattern = r'<option value="(https://joshuaproject\.net/maps/india/[^"]+)"[^>]*>([^<]+)</option>'
        matches = re.findall(pattern, content)
        for url, name in matches:
            urls.append((url, name.strip()))
    return urls

def get_table_url_from_map_page(map_url):
    """Extract the table URL from the map page"""
    try:
        response = requests.get(map_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Look for links to the district data table page
            links = soup.find_all('a', href=True)
            for link in links:
                if '/people_groups/districts/' in link['href']:
                    return urljoin('https://joshuaproject.net', link['href'])
    except Exception as e:
        print(f"Error accessing map page {map_url}: {e}")
    return None

def parse_table_data(html_content, people_group_name):
    """Parse table data directly from HTML content"""
    soup = BeautifulSoup(html_content, 'html.parser')
    data = []
    headers = []
    
    # Find the table by its ID
    table = soup.find('table', id='districtList')
    if not table:
        print(f"Could not find table for {people_group_name}")
        return headers, data
    
    # Extract headers
    thead = table.find('thead')
    if thead:
        for th in thead.find_all('th'):
            # Clean header text (remove sorting arrows, etc.)
            header_text = th.get_text(strip=True)
            header_text = re.sub(r'[▲▼]', '', header_text)
            headers.append(header_text)
    
    # Extract rows from tbody
    tbody = table.find('tbody')
    if tbody:
        for tr in tbody.find_all('tr'):
            row_data = []
            for td in tr.find_all('td'):
                # Remove hidden spans used for sorting
                for span in td.find_all('span', class_='hidden'):
                    span.decompose()
                
                # Get the cleaned text content
                cell_text = td.get_text(strip=True)
                
                # Handle empty or dash cells
                if not cell_text or cell_text == '-':
                    cell_text = ''
                
                row_data.append(cell_text)
            
            # Add people group name to the data
            if row_data:
                row_data.insert(0, people_group_name)
                data.append(row_data)
    
    return headers, data

def scrape_table_data(table_url, people_group_name):
    """Scrape the table data from the given URL"""
    try:
        response = requests.get(table_url)
        if response.status_code == 200:
            return parse_table_data(response.text, people_group_name)
    except Exception as e:
        print(f"Error scraping table from {table_url}: {e}")
    
    return [], []

def main():
    data_file = 'data.txt'
    output_file = 'ALL_DATA.csv'
    
    # Extract URLs from the file
    people_groups = extract_urls_from_file(data_file)
    print(f"Found {len(people_groups)} people groups to process")
    
    all_data = []
    headers = ['People Group']  # Initialize with People Group column
    
    # Process each URL
    for i, (map_url, people_group_name) in enumerate(people_groups):
        print(f"Processing {i+1}/{len(people_groups)}: {people_group_name}")
        
        # Get the table URL from the map page
        table_url = get_table_url_from_map_page(map_url)
        if not table_url:
            print(f"Could not find table URL for {people_group_name}, trying direct parsing...")
            # Try to scrape the map page directly
            try:
                response = requests.get(map_url)
                if response.status_code == 200:
                    row_headers, rows = parse_table_data(response.text, people_group_name)
                    if rows:
                        # Update headers if first successful scrape
                        if not all_data and row_headers:
                            headers.extend(row_headers)
                        # Add rows to all_data
                        all_data.extend(rows)
                        print(f"Successfully parsed data directly for {people_group_name}")
                        # Sleep to avoid overloading the server
                        time.sleep(random.uniform(1, 3))
                        continue
            except Exception as e:
                print(f"Error directly parsing {map_url}: {e}")
            
            print(f"Skipping {people_group_name}...")
            continue
        
        # Scrape the table data
        row_headers, rows = scrape_table_data(table_url, people_group_name)
        
        # Update headers if this is the first successful scrape
        if not all_data and row_headers:
            headers.extend(row_headers)
        
        # Add rows to all_data
        all_data.extend(rows)
        
        # Sleep to avoid overloading the server
        time.sleep(random.uniform(1, 3))
    
    # Write data to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(all_data)
    
    print(f"Data extraction complete. Saved to {output_file}")
    print(f"Total records: {len(all_data)}")

def process_single_html_file(html_file, output_file, people_group_name="Test Group"):
    """Process a single HTML file for testing"""
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    headers, data = parse_table_data(html_content, people_group_name)
    
    # Prepare headers for CSV
    csv_headers = ['People Group'] + headers
    
    # Write data to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(csv_headers)
        writer.writerows(data)
    
    print(f"Processed single file. Saved to {output_file}")
    print(f"Total records: {len(data)}")

if __name__ == "__main__":
    # Uncomment the following line to process a single HTML file for testing
    # process_single_html_file('example.txt', 'single_group_data.csv', 'Example Group')
    
    # Comment out the following line if you're just testing with a single file
    main()