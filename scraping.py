"""
To run this script:

1. Activate the virtual environment:
    - Open a terminal/command prompt
    - Navigate to the directory containing this script
    - Run the command: `env\Scripts\activate`

2. Run the script:
    - In the same terminal/command prompt, run the command: `python scraping.py`
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import textwrap
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# Constants
BASE_URL = "https://azimpremjifoundation.org/appi-list-view"
PAGE_SIZE = 80

# Function to get the last page number
def get_last_page_number():
    initial_req = requests.get(BASE_URL)
    initial_soup = BeautifulSoup(initial_req.content, 'html.parser')
    last_page_item = initial_soup.find('li', class_='pager-last')
    last_page_url = last_page_item.find('a')['href']
    return int(last_page_url.split('=')[-1])

# Function to scrape data from a page
def scrape_page(page_number):
    url = f"{BASE_URL}?page={page_number}"
    req = requests.get(url)
    soup = BeautifulSoup(req.content, 'html.parser')
    tags = soup.find_all(['h3', 'p'])
    return tags

# Function to process tags and add them to the data list
def process_tags(tags, data, heading_count):
    for tag in tags:
        text = tag.get_text()
        if tag.name == 'h3':
            heading_count += 1
            text = f'{heading_count} : {text}'
            data.append(text)
        elif tag.name == 'p':
            lines = textwrap.wrap(text, width=PAGE_SIZE)
            data.extend(lines)
        data.append('')
    return data, heading_count

# Function to create a PDF file from the DataFrame
def create_pdf(df):
    c = canvas.Canvas("output.pdf", pagesize=letter)
    line_pos = 750
    for index, row in df.iterrows():
        if line_pos < 50:
            c.showPage()
            line_pos = 750
        c.drawString(50, line_pos, row['Text'])
        line_pos -= 15
    c.save()

def main():
    last_page_number = get_last_page_number()
    data = []
    heading_count = 0

    for page in range(last_page_number + 1):
        tags = scrape_page(page)
        data, heading_count = process_tags(tags, data, heading_count)

    df = pd.DataFrame(data, columns=['Text'])

    # Excel file
    df.to_excel("output.xlsx", index=False)

    # Text file
    df.to_csv("output.txt", index=False)
    create_pdf(df)

if __name__ == "__main__":
    main()


#############end################