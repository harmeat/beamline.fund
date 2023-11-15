import requests
from bs4 import BeautifulSoup
import pandas as pd

headers = {
    'authority': 'www.beamline.fund',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9,ru;q=0.8',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
}

if __name__ == '__main__':
    
    URL = "https://www.beamline.fund/portfolio"
    response = requests.get(URL, headers=headers)
    # Assuming 'response' is your HTTP response object
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        main_container = soup.find('main', {'class': 'PAGES_CONTAINER'})

        if main_container:
            companies_data = []
            find_companies = main_container.find_all('div', {'role': 'region', 'aria-label': 'content changes on hover'})

            for company in find_companies:
                company_data = {}
                # Title
                title_element = company.find('h5')
                company_data['Title'] = title_element.text if title_element else 'N/A'

                # First Link
                link_element = company.find('a', href=True)
                company_data['Link'] = link_element['href'] if link_element else 'N/A'

                # Image Source
                img_element = company.find('img')
                company_data['Image'] = img_element['src'].replace(',blur_3', '') if img_element else 'N/A'

                # Short Descriptions
                rich_text_elements = company.find_all('div', {'data-testid': 'richTextElement'})
                for i, rich_text in enumerate(rich_text_elements[1:], start=1):
                    if rich_text:
                        FOUND = False
                        description_text = ""
                        
                        headings = rich_text.find_all('h2')
                        if headings:
                            for heading in headings:
                                clean_text = str(heading).replace('<br class="wixui-rich-text__text">', '').replace('</br>', '').replace('Website','')
                                description_text += BeautifulSoup(clean_text, 'html.parser').get_text().strip()
                                FOUND = True

                        if not FOUND:
                            headings = rich_text.find_all('h4')
                            if headings:
                                for heading in headings:
                                    clean_text = str(heading).replace('<br class="wixui-rich-text__text">', '').replace('</br>', '').replace('Website','')
                                    if clean_text != ' ':
                                        description_text += BeautifulSoup(clean_text, 'html.parser').get_text().strip()
                                        FOUND = True
                        
                        if not FOUND:
                            paragraphs = rich_text.find_all('p')
                            for para in paragraphs:
                                if para:
                                    clean_text = str(para).replace('<br class="wixui-rich-text__text">', '').replace('</br>', '').replace('Website','')
                                    if clean_text != ' ':
                                        description_text += BeautifulSoup(clean_text, 'html.parser').get_text().strip()
                                        FOUND = True
                        
                        company_data[f'Description_{i}'] = description_text.strip()

                companies_data.append(company_data)

            # Convert to DataFrame and save as Excel
            df = pd.DataFrame(companies_data)
            df.to_excel('companies_data.xlsx', index=False)

    else:
        print(f"Request failed with status code {response.status_code}")
