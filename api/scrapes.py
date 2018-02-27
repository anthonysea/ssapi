import requests
from bs4 import BeautifulSoup
from flask import Flask, request, render_template, jsonify,abort, make_response
import config
import decimal

app = Flask(__name__)
app.config.from_object('config')
the_api_key = config.api_key

#####database functions
from functions import *


###############Juno
@app.route('/api/v1.0/<int:api_key>/scrape/juno/<int:release_id>',methods=['GET'])
def scrape_juno(api_key,release_id):
    if str(api_key)!=the_api_key:
        abort(401)
    juno_url = 'https://www.juno.co.uk/products/' + str(release_id) + '-01'
    r = requests.get(juno_url)
    soup = BeautifulSoup(r.text, "lxml")
    pricing_html = soup.find("div","product-pricing")
    stock = pricing_html.find("em").text
    price = str(pricing_html.find("span","product-price").text)

    return jsonify({'price': price,'stock': stock}), 201



##########hardwax
#####this goes to a label or artist page and returns all releases on that page
@app.route('/api/v1.0/<int:api_key>/scrape/hardwax/<string:type_of_search>/<string:query>/<string:title>',methods=['GET'])
def define_hard_wax_search_url(api_key, type_of_search, query, title):
    if str(api_key)!=the_api_key:
            return 401
    if type_of_search=='artist':
        type_of_search = 'act'
    title = str(title)
    base_url = 'https://hardwax.com/' + str(type_of_search) + '/' + str(query.lower().replace(' ','-'))
    x = get_hard_wax(base_url)
    return x

@app.route('/api/v1.0/<int:api_key>/scrape/hardwax/new',methods=['GET'])
def define_hard_wax_new_url(api_key):
    if str(api_key)!=the_api_key:
        return 401
    base_url = 'https://hardwax.com/this-week/?paginate_by=500'
    x = get_hard_wax(base_url)
    return x

@app.route('/api/v1.0/<int:api_key>/scrape/hardwax/bis',methods=['GET'])
def define_hard_wax_bis_url(api_key):
    if str(api_key)!=the_api_key:
        return 401
    base_url = 'https://hardwax.com/back-in-stock/?paginate_by=500'
    x = get_hard_wax(base_url)
    return x


@app.route('/api/v1.0/<int:api_key>/scrape/hardwax/release/<string:hardwax_id>',methods=['GET'])
def get_hard_wax_release(api_key,hardwax_id):
    if str(api_key)!=the_api_key:
        return 401
    base_url = 'https://hardwax.com/' + str(hardwax_id)
    ####now get the HTML
    try:
        r = requests.get(base_url)
    except Exception as e:
        return "Failed to request the Hardwax URL " + base_url, 405

    soup = BeautifulSoup(r.text, "lxml")
    stock_details = soup.find("div","add_order").text
    
    if 'out of stock' in stock_details:
        return jsonify({'in_stock':'false','url':base_url})
    else:
        return jsonify({'in_stock':'true','url':base_url})

    


def get_hard_wax(base_url):

    ####now get the HTML
    try:
        r = requests.get(base_url)
    except Exception as e:
        return "Failed to request the Hardwax URL " + base_url, 405

    soup = BeautifulSoup(r.text, "lxml")
    for product in soup.find_all("div","listing"):
        details = str()
        label_html = str()
        label = str()
        label_url = str()
        artist_title = str()
        split_a_t = str()
        artist = str()
        title = str()
        release_url = str()

        details = product.find("div","textblock")
        label_html = details.find("div","linesmall")

        label = label_html.find("a").text.encode('utf-8')
        label_url = label_html.findAll("a")[0]['href']

        artist_title = details.find("div","linebig").text.encode('utf-8')
        split_a_t = artist_title.split(":\xc2\xa0")
        artist = split_a_t[0]

        title = split_a_t[1]
        release_url = label_html.findAll("a")[1]['href']

        split_release_url = release_url.split('/')
        store_release_id =  str(split_release_url[1])
        print(store_release_id)
        
        if len(store_release_id)<1:
            print('Didnt get the store id - skip')
            continue

        if len(label) < 3 or len(title) < 3:
            print('skipping ' + title + ' or ' + label + ' as less than 3 characters')
            continue

        
        #sql = ('SELECT id FROM releases_all WHERE label_no_country LIKE %s AND title LIKE %s') % ('%' + label + '%','%' + title + '%')
        try:
            query = db_insert('INSERT INTO store_mappings (release_id,store,store_url,unique_key,store_release_id) SELECT id,%s,%s, md5(concat(id,%s)),%s FROM releases_all WHERE label_no_country LIKE %s AND title LIKE %s ON DUPLICATE KEY UPDATE store_url=values(store_url),store_release_id=values(store_release_id)', ('hardwax',release_url,'hardwax',store_release_id,label + '%','%' + title + '%'))
            data = query.fetchall()
            print(query,data)
        except Exception as e:
            print(str(e))
            continue
        
        
    return base_url,201


