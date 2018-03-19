import requests
from bs4 import BeautifulSoup

class deejay_scrape():
    def __init__(self):
        self.base_url = 'https://www.deejay.de/content.php?param=/m_All/sm_News/sort_voe/perpage_180/page_1'

    def get_page(self, url):
        print('Getting page..' + url)
        try:
            r = requests.get(url)
            self.page_got = r.text
        except Exception as e:
            error = "Couldnt grab the url " + str(e)
            return error

    def load_html_into_bs(self, html):
        soup = BeautifulSoup(html, "lxml")
        self.soup = soup

    def scrape_listings(self, soup):
        listings_dict = []
        for product in soup.find_all("article", "product"):
            product_id = product['id'].replace('a','')
            details_a = product.find("div", "inner_a")
            try:
                title_html = details_a.find("h3","title")
            except:
                pass
            title = title_html.find("a").text
            product_url = title_html.find("a")['href']

            details_b = product.find("div", "inner_b")
            try:
                label_html = details_b.find("div","label")
            except:
                pass

            try:
                label = label_html.findAll("b")[0].text
            except:
                label = label_html.findAll("a")[0]['href']
                try:
                    label = label_html.findAll("em")[0].text
                except:
                    pass

            details = {'title': title, 'label': label, 'url': product_url, 'product_id': product_id}
            listings_dict.append(details)

        self.listings_dict = listings_dict

    def check_db_for_match(self, listings_dict):
        return listings_dict


    def scrape_stock(self, listing_url):
        return listing_url


    def process_all(self):
        self.get_page(self.base_url)
        self.load_html_into_bs(self.page_got)
        self.scrape_listings(self.soup)
        self.check_db_for_match(self.listings_dict)

    def check_stock(self):
        self.get_page(self.base_url)
        self.load_html_into_bs(self.page_got)
        self.scrape_stock(self.soup)



######scrape listings and store in DB
client = deejay_scrape()
print(client.process_all())
