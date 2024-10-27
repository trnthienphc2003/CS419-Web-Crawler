import httpx
from bs4 import BeautifulSoup

def crawl_website(url):
    # Send an HTTP request to the URL
    response = httpx.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the webpage content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        with open('data.html', 'w') as f:
            f.write(soup.prettify())
        
        # Extract all the links on the webpage
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            # Clean up links to handle relative URLs and append to the list
            if href.startswith('http'):
                links.append(href)
            # else:
            #     links.append(url + href)
        
        return links
    else:
        print(f"Failed to retrieve webpage. Status code: {response.status_code}")
        return []

# Example usage
url = 'https://tuoitre.vn/tp-hcm-hom-qua-mua-to-hon-100mm-chieu-toi-nay-mua-con-nhieu-hon-20241021113448945.htm'
# Replace with the desired URL
links = crawl_website(url)

# Print all found links
for link in links:
    print(link)
