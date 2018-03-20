<<<<<<< HEAD
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
import requests
from bs4 import BeautifulSoup
#####database functions
from functions import db_insert,db_select
import config



class deejay_scrape():
    def __new__(self):
        return 'doing it'

    def get_page(self, url):
        self.base_url = url
=======
import requests
from bs4 import BeautifulSoup

class deejay_scrape():
    def __init__(self):
        self.base_url = 'https://www.deejay.de/content.php?param=/m_All/sm_News/sort_voe/perpage_180/page_1'

    def get_page(self, url):
>>>>>>> 2c970b446800dab232c6fa83f9309dd558edf030
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
<<<<<<< HEAD
        
=======
>>>>>>> 2c970b446800dab232c6fa83f9309dd558edf030

    def scrape_listings(self, soup):
        listings_dict = []
        for product in soup.find_all("article", "product"):
            product_id = product['id'].replace('a','')
            details_a = product.find("div", "inner_a")
            try:
                title_html = details_a.find("h3","title")
            except:
<<<<<<< HEAD
                continue
            title = title_html.find("a").text.replace('2x12"','').strip().replace('()',"")
=======
                pass
            title = title_html.find("a").text
>>>>>>> 2c970b446800dab232c6fa83f9309dd558edf030
            product_url = title_html.find("a")['href']

            details_b = product.find("div", "inner_b")
            try:
                label_html = details_b.find("div","label")
            except:
<<<<<<< HEAD
                continue
=======
                pass
>>>>>>> 2c970b446800dab232c6fa83f9309dd558edf030

            try:
                label = label_html.findAll("b")[0].text
            except:
                label = label_html.findAll("a")[0]['href']
                try:
                    label = label_html.findAll("em")[0].text
                except:
<<<<<<< HEAD
                    continue
=======
                    pass
>>>>>>> 2c970b446800dab232c6fa83f9309dd558edf030

            details = {'title': title, 'label': label, 'url': product_url, 'product_id': product_id}
            listings_dict.append(details)

        self.listings_dict = listings_dict

    def check_db_for_match(self, listings_dict):
<<<<<<< HEAD
        for record in listings_dict:
            print('Doing ' + record['title'] + ' on ' + record['label'])

            try:
                query = db_insert('''INSERT INTO store_mappings (release_id,store,store_url,unique_key,store_release_id) 
                    SELECT id,%s,%s, md5(concat(id,%s)),%s 
                    FROM releases_all 
                    WHERE label_no_country LIKE %s AND title LIKE %s 
                    ON DUPLICATE KEY UPDATE store_url=values(store_url),store_release_id=values(store_release_id)''', 
                    ('deejay',record['url'],'deejay',record['product_id'],record['label'] + '%','%' + record['title'] + '%'))
                data = query.fetchall()
                print(query,data)
            except Exception as e:
                print(str(e))
                pass


    def scrape_stock(self, soup):
        stock = soup.find('div','stock').text
        if stock=='out of Stock':
            output = json.dumps({'store':'deejay','in_stock':'false','cart_url':self.base_url})
            return output
        else:
            output = json.dumps({'store':'deejay','in_stock':'true','cart_url':self.base_url})
            return output





    def process_all(self,base_url):
        self.get_page(base_url)
=======
        return listings_dict


    def scrape_stock(self, listing_url):
        return listing_url


    def process_all(self):
        self.get_page(self.base_url)
>>>>>>> 2c970b446800dab232c6fa83f9309dd558edf030
        self.load_html_into_bs(self.page_got)
        self.scrape_listings(self.soup)
        self.check_db_for_match(self.listings_dict)

<<<<<<< HEAD
    def check_stock(self,base_url):
        self.get_page(base_url)
        self.load_html_into_bs(self.page_got)
        return self.scrape_stock(self.soup)



client = deejay_scrape()


######scrape listings and store in DB
for x in range(1,10):
    print('Doing page' + str(x))
    
    print(client.process_all('https://www.deejay.de/content.php?param=/m_All/sm_News/sort_voe/perpage_180/page_' + str(x)))

release_id = '307117'
base_url_scrape = 'https://www.deejay.de/content.php?param=' + release_id


print(client.check_stock(base_url_scrape))



=======
    def check_stock(self):
        self.get_page(self.base_url)
        self.load_html_into_bs(self.page_got)
        self.scrape_stock(self.soup)



######scrape listings and store in DB
client = deejay_scrape()
print(client.process_all())
>>>>>>> 2c970b446800dab232c6fa83f9309dd558edf030
