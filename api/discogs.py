import requests
from bs4 import BeautifulSoup
from flask import Flask, request, render_template, jsonify,abort, make_response
import config
import decimal
import json
import collections
from collections import Counter #count items in a list
import operator #to sort a dict
import hashlib #used to generate the key for the insert
import re

app = Flask(__name__)
app.config.from_object('config')
the_api_key = config.api_key

#####database functions
from functions import db_insert,db_select



#############import from Discogs##################
@app.route('/api/v1.0/<int:api_key>/user/<string:user>/importDiscogs/<string:discogs_user>',methods=['GET'])
def import_discogs(api_key,user,discogs_user):
    if str(api_key)!=the_api_key:
        abort(401)
    userName = str(user)
    discogsUser = str(discogs_user)

    headers = {
    'User-Agent': 'soundshelter.net',
    'From': 'info@soundshelter.net'  # This is another valid field
    }

    #gets collection
    r = requests.get('https://api.discogs.com/users/' + discogsUser + '/collection/folders/0/releases',headers=headers)



    text = r.text
    text = text.encode('utf-8')
    searchJson = json.loads(text)


    #gets collection

    results_per_page = searchJson['pagination']['per_page']


    num_pages = searchJson['pagination']['pages'] + 1


    #now go through each page
    data = []

    counter = 0

    for page_number in xrange(0,num_pages):
        url = 'https://api.discogs.com/users/' + discogsUser + '/collection/folders/0/releases?per_page=' + str(results_per_page) + '&page=' + str(page_number)
        print('Doing ' + url)
        r = requests.get(url,headers=headers)
        text = r.text
        text = text.encode('utf-8')

        #now we have a list of releases, we can pull out the artists
        searchJson = json.loads(text)

        num_releases = len(searchJson['releases'])

        for x in xrange(0,num_releases):
            num_artists =  len(searchJson['releases'][x]['basic_information']['artists'])
            #get all artists
            for y in xrange(0,num_artists):
                artist = searchJson['releases'][x]['basic_information']['artists'][y]['name']
                if artist is 'Various':
                    pass
                if artist is 'Unknown Artist':
                    pass
                data.append(artist)


    total = dict(Counter(data))

    #sorted_x = sorted(total.items(), key=operator.itemgetter(1))

    for x in total:
        artist = str(x.encode('utf-8'))

        artist = re.sub(r'\(.*?\)', '',artist) #removes the (19) at the end of some artists
        artist = artist.replace("&","and")
        artist = artist.replace("'","")

        count = str(total[x])

        key = hashlib.md5(userName + artist).hexdigest()
        print(userName,discogsUser,artist,count,key)

        counter += 1





        try:
            insert = db_insert("INSERT INTO discogs_collection (user,discogs_user,artist,count,the_key) VALUES (%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE count=VALUES(count)",(userName,discogsUser,artist,count,key))
            print("Inserted for " + artist)

        except Exception as e:
            print(str(e))


    return "We picked out " + str(counter) + " artists from your Discogs collection"
