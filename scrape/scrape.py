from bs4 import BeautifulSoup
import requests
import csv
import re


def clean_text(text):
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Add space after punctuation if it's followed by a letter
    text = re.sub(r'([.,!?;:])([a-zA-Z])', r'\1 \2', text)
    return text.strip()


# Open a new CSV file to write the scraped text
with open('./scrape/urls.csv', 'r') as input_file, \
        open('./scrape/scraped.csv', 'w', newline='', encoding='utf-8') as output_file, \
        open('./scrape/scraped.txt', 'w', encoding='utf-8') as txt_file:

    reader = csv.reader(input_file)
    writer = csv.writer(output_file)

    # Write header row
    writer.writerow(['URL', 'Text'])

    all_text = []  # List to store all scraped text

    for row in reader:
        url = row[0]
        page_to_scrape = requests.get(url)
        soup = BeautifulSoup(page_to_scrape.text, "html.parser")

        # Extract text from each element separately
        texts = []
        for element in soup.find_all(string=True):
            if element.parent.name not in ['script', 'style']:
                texts.append(element.strip())

        # Join the texts and clean
        text = clean_text(' '.join(texts))

        # Write the URL and the scraped text to the CSV
        writer.writerow([url, text])

        # Append the cleaned text to the all_text list
        all_text.append(text)

    # Write all scraped text to the TXT file
    txt_file.write('\n\n'.join(all_text))

print("Scraping complete. Results saved in 'scraped.csv' and 'scraped.txt'.")
