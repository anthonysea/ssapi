#!flask/bin/python
import sys
sys.path.append("/var/www/ssapi/api")
sys.path.append('/var/www/ssapi')

from flask import Flask, request, render_template, jsonify,abort, make_response
from flask.ext.cache import Cache
import time
import hashlib

##############for Discogs API
import requests
import json
import collections
from collections import Counter #count items in a list
import operator #to sort a dict
import hashlib #used to generate the key for the insert
import re
###############end Discogs API

#this is for the function db_select
import MySQLdb


import collections

#database connect
from flaskext.mysql import MySQL
import json


import config

#https://pythonhosted.org/Flask-Cache/



reload(sys)
sys.setdefaultencoding('utf-8')

app = Flask(__name__)
app.config.from_object('config')
cache = Cache(app,config={'CACHE_TYPE': 'simple'})


app.config['MYSQL_DATABASE_USER'] = config.user
app.config['MYSQL_DATABASE_PASSWORD'] = config.password
app.config['MYSQL_DATABASE_DB'] = config.database
app.config['MYSQL_DATABASE_HOST'] = config.host
the_api_key = config.api_key


mysql = MySQL()
mysql.init_app(app)



################DB QUERIES FOR FOLLOWING METHODS: updateRecommendations
def db_select(query,params):

	host = config.host
	user = config.user
	password = config.password
	db = config.database

	
	db = MySQLdb.connect(host,user,password,db)
	cur = db.cursor()
	cur.execute(query,params)
	db.close()	
	return cur

def db_insert(query,params):
	host = config.host
	user = config.user
	password = config.password
	db = config.database


	db = MySQLdb.connect(host,user,password,db)
	cur = db.cursor()
	cur.execute(query,params)
	db.commit()
	db.close()
	return cur

#######END DB QUERIES


@app.route('/')
@app.route('/index/')
def index():
    return render_template('index.html')


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
	#print r.text



	text = r.text
	text = text.encode('utf-8')
	searchJson = json.loads(text)
	#print searchJson

	#gets collection

	results_per_page = searchJson['pagination']['per_page']
	#print results_per_page

	num_pages = searchJson['pagination']['pages'] + 1
	#print num_pages

	#now go through each page
	data = []

	counter = 0

	for page_number in xrange(0,num_pages):
		url = 'https://api.discogs.com/users/' + discogsUser + '/collection/folders/0/releases?per_page=' + str(results_per_page) + '&page=' + str(page_number)
		print 'Doing ' + url
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
		print userName,discogsUser,artist,count,key

		counter += 1



		

		try:
			insert = db_insert("INSERT INTO discogs_collection (user,discogs_user,artist,count,the_key) VALUES (%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE count=VALUES(count)",(userName,discogsUser,artist,count,key))
			print "Inserted for " + artist

		except Exception as e:
			print e


	return "We picked out " + str(counter) + " artists from your Discogs collection"


#########get a users personalised recommendations
@app.route('/api/v1.0/<int:api_key>/user/<string:user>/recommendations',methods=['GET'])
def get_recommendations(api_key,user):
	if str(api_key)!=the_api_key:
		abort(401)
	user = str(user)
	return 'coming soon for ' + user


#########get all releases by an artist
@app.route('/api/v1.0/<int:api_key>/artist/<string:artist>',methods=['GET'])
@cache.cached(timeout=50)
def get_artist(api_key,artist):
	if str(api_key)!=the_api_key:
		abort(401)
	artist = str(artist)
	if len(artist) ==0:
		abort(404)

	cursor = mysql.connect().cursor()
	try:
		results = cursor.execute("SELECT releases.* from releases INNER JOIN release_artists ON releases.id=release_artists.release_id where release_artists.artists='" + artist + "' GROUP BY releases.id ORDER BY releases.date DESC")
	except Exception as e:
		return "Failed to run db query: " + str(e)

	numrows = int(cursor.rowcount)

	if numrows==0:
		return "No record found"

	id_data = []
	for x in range(0,numrows):
		row = cursor.fetchone()
		release_id = str(row[0])
		d = collections.OrderedDict()
		d['release_id'] = release_id
		d['all_artists'] = str(row[2])
		d['title'] = str(row[4])
		d['label'] = str(row[6])
		d['genre'] = str(row[8])
		d['date'] = str(row[9])
		d['small_img'] = 'https://www.soundshelter.net/images/covers/CS' + release_id + '-01A-MED.jpg'
		d['big_img'] = 'https://www.soundshelter.net/images/covers/CS' + release_id + '-01A-BIG.jpg'
		d['api_release_id'] = 'https://api.soundshelter.net/api/v1.0/' + str(api_key) + '/release/' + release_id
		id_data.append(d)
		
	final_data = {'releases':id_data}
	resp = jsonify(results=final_data)
	return resp


#######get all releases on a label
@app.route('/api/v1.0/<int:api_key>/label/<string:label>',methods=['GET'])
@cache.cached(timeout=50)
def get_label(api_key,label):
	if str(api_key)!=the_api_key:
		abort(401)
	label = str(label)
	if len(label) ==0:
		abort(404)

	cursor = mysql.connect().cursor()
	try:
		results = cursor.execute("SELECT releases.* from releases where releases.label_no_country='" + label + "' GROUP BY releases.id ORDER BY releases.date DESC")
	except Exception as e:
		return "Failed to run db query: " + str(e)

	numrows = int(cursor.rowcount)

	if numrows==0:
		return "No record found"

	id_data = []
	for x in range(0,numrows):
		row = cursor.fetchone()
		release_id = str(row[0])
		d = collections.OrderedDict()
		d['release_id'] = release_id
		d['all_artists'] = str(row[2])
		d['title'] = str(row[4])
		d['label'] = str(row[6])
		d['genre'] = str(row[8])
		d['date'] = str(row[9])
		d['small_img'] = 'https://www.soundshelter.net/images/covers/CS' + release_id + '-01A-MED.jpg'
		d['big_img'] = 'https://www.soundshelter.net/images/covers/CS' + release_id + '-01A-BIG.jpg'
		d['api_release_id'] = 'https://api.soundshelter.net/api/v1.0/' + str(api_key) + '/release/' + release_id
		id_data.append(d)
		
	final_data = {'releases':id_data}
	resp = jsonify(results=final_data)
	return resp



#########get a release
@app.route('/api/v1.0/<int:api_key>/release/<int:release_id>',methods=['GET'])
@cache.cached(timeout=50)
def get_release(api_key,release_id):
	
	if str(api_key) !=the_api_key:
		abort(401)
	release_id = str(release_id) #convert to string
	####check that we recieved a release_id
	if len(release_id) ==0:
		abort(404)
	
	#return release_id

	#####pass release_id into query to get release details	
	cursor = mysql.connect().cursor()
	try:
		results = cursor.execute("SELECT * from releases where id='" + release_id + "'")
	except Exception as e:
		return "Failed to run db query: " + str(e)

	numrows = int(cursor.rowcount)

	if numrows==0:
		return "No record found for " + str(release_id)

	for x in range(0,numrows):
		row = cursor.fetchone()
		release_id = str(row[0])
		#artists = str(row[1])
		all_artists = str(row[2])
		title = str(row[4])
		label = str(row[6])
		genre = str(row[8])
		date = str(row[9])
		small_img = 'https://www.soundshelter.net/images/covers/CS' + release_id + '-01A-MED.jpg'
		big_img = 'https://www.soundshelter.net/images/covers/CS' + release_id + '-01A-BIG.jpg'

		release_data = {'release_id':release_id,'artists':all_artists,'title':title,'label':label,'genre':genre,'date':date,'small_img':small_img,'big_img':big_img}

	#get savers
	#####pass release_id into query to get release details	
	cursor = mysql.connect().cursor()
	try:
		results = cursor.execute("SELECT artist from charts_extended where artist!= 'Sound Shelter' AND release_id='" + release_id + "'")
	except Exception as e:
		return "Failed to run db query: " + str(e)

	numrows = int(cursor.rowcount)

	if numrows==0:
		return "No record found"


	##get list of users who saved this release
	saver_data = []
	for x in range(0,numrows):
		row = cursor.fetchone()
		user = str(row[0])
		d = collections.OrderedDict()
		d['user'] = user
		d['user_url'] = 'https://api.soundshelter.net/api/v1.0/' + str(api_key) + '/user/' + user + '/recommendations'
		saver_data.append(d)
		
	print saver_data

	

	final_data = {'details':release_data,'savers':saver_data}
	resp = jsonify(results=final_data)
	return resp



#########update a users recs
@app.route('/api/v1.0/<int:api_key>/user/<string:user>/updateRecommendations/<string:stage>',methods=['GET'])
def update_recommendations(api_key,user,stage):
	if str(api_key)!=the_api_key:
		abort(401)
	userName = str(user)
	stage = str(stage)

	if stage=='onboarding':
		date_diff=720
	else:
		date_diff=30

	start_time = time.time() 

	#now store the labels: These are the labels that the artists in AUHR have appeared on more than twice
	try:
		getLabels = db_select('''SELECT label,sum(cnt) as cnt
			FROM (
			SELECT releases.label_no_country as label,COUNT(releases.label_no_country) * 5 as cnt
				FROM releases_all releases
				JOIN listens
				ON listens.release_id=releases.id
				WHERE listens.user=%s
				AND releases.id!='0'
				GROUP BY releases.label_no_country
			UNION ALL
			SELECT releases.label_no_country as label,COUNT(releases.label_no_country) * 20 as cnt
				FROM releases_all releases
				JOIN charts_extended ce
				ON ce.release_id=releases.id
				WHERE ce.artist=%s
				AND releases.id!='0'
				GROUP BY releases.label_no_country
			UNION ALL
			SELECT releases.label_no_country as label,COUNT(releases.label_no_country) * 30 as cnt
				FROM releases_all releases
				JOIN buys
				ON buys.release_id=releases.id
				WHERE buys.user=%s
				AND releases.id!='0'
				GROUP BY releases.label_no_country
			UNION ALL
			(SELECT DISTINCT ll.label,COUNT(ll.id) * 100 as cnt
				FROM label_love ll
				WHERE ll.user=%s
				GROUP BY ll.label)
			) as deets
			WHERE cnt > 5
			GROUP BY label
			ORDER BY cnt DESC
			LIMIT 0,50''',(userName,userName,userName,userName))
	
	except Exception as e:
		print str(e) + " - the error is in the label calculation"
		

	dataLabels = getLabels.fetchall() 

	for labelRow in dataLabels:
		label = str(labelRow[0])
		count = str(labelRow[1])
		print label + ': ' + count
		key = hashlib.md5(userName + label).hexdigest()
		insertLabel = db_insert("INSERT INTO labels_user_has_recd (user,label,the_key,count) VALUES (%s,%s,%s,%s) ON DUPLICATE KEY UPDATE the_key=VALUES(the_key),count=VALUES(count)",(userName,label,key,count))

	#now we find releases that are by those artists
	if stage=='onboarding':
		number_of_items = 20
	else:
		number_of_items = 2
	

	#now we find releases that are on these labels
	getReleases = db_select("SELECT releases.id,releases.label_no_country,releases.date FROM releases_all releases INNER JOIN labels_user_has_recd luhr ON luhr.label=releases.label_no_country  LEFT JOIN recommendations ON recommendations.release_id=releases.id AND recommendations.user=luhr.user WHERE luhr.user=%s AND datediff(now(),releases.date) <= %s GROUP BY releases.label_no_country ORDER BY luhr.count DESC LIMIT 0," + str(number_of_items) + "",(userName,date_diff))
	dataReleases = getReleases.fetchall()
	count =0

	#we reverse so that we can then sort the recommendations by rec.id
	dataReleases = reversed(dataReleases)

	
	for releasesRow in dataReleases:

		releaseId = str(releasesRow[0])
		key = hashlib.md5(userName + releaseId).hexdigest()
		insertRelease = db_insert("INSERT INTO recommendations (user,release_id,the_key) VALUES (%s,%s,%s) ON DUPLICATE KEY UPDATE the_key=VALUES(the_key)",(userName,releaseId,key))
		count = count + 1
		print "inserted " + releaseId


	#######################now do the artists_user_has_recd

	sql = """SELECT artist,sum(cnt) as cnt FROM
			(SELECT DISTINCT similar.similar_artist as artist,COUNT(similar.similar_artist) as cnt FROM release_artists INNER JOIN charts_extended ON charts_extended.release_id=release_artists.release_id INNER JOIN similar ON release_artists.artists=similar.artist INNER JOIN users ON users.name=charts_extended.artist WHERE users.name=%s GROUP BY similar.similar_artist HAVING COUNT(similar.similar_artist) > 0 UNION all
				SELECT DISTINCT release_artists.artists as artist ,COUNT(release_artists.artists) * 20 as cnt FROM release_artists INNER JOIN charts_extended ce ON ce.release_id=release_artists.release_id 
				WHERE ce.artist=%s GROUP by release_artists.artists HAVING COUNT(release_artists.artists) > 0
			UNION all
				SELECT artist_love.artist as artist,'75' as cnt FROM artist_love WHERE artist_love.user=%s AND artist_love.source!='onboarding'
			UNION all
				SELECT artist_love.artist as artist,'10' as cnt FROM artist_love WHERE artist_love.user=%s AND artist_love.source='onboarding'
			UNION all
				SELECT `auhr`.artist, auhr.count
				FROM artists_user_has_recd auhr WHERE auhr.user=%s AND count='20'
			UNION all
				SELECT release_artists.artists, COUNT(artists) * 5 as cnt
				FROM release_artists
				INNER JOIN listens
				ON listens.release_id=release_artists.release_id
				WHERE listens.user=%s
				GROUP BY release_artists.artists
			UNION all
				SELECT similar_artist as artist,COUNT(similar.id)
				FROM similar
				JOIN genre_artists ga
				ON ga.artist=similar.artist
				JOIN genre_follows gf
				ON gf.genre=ga.genre
				JOIN users
				ON users.name=gf.user
				WHERE users.name=%s
				GROUP BY similar.similar_artist
			UNION all
				SELECT artist,count * 30 as cnt
				FROM discogs_collection
				WHERE user=%s
				AND artist!='Various'
				AND count>1	
			UNION all
				SELECT artist,'50'
				FROM spotify_top_artists
				WHERE user=%s
			UNION ALL
				SELECT artists as artist, COUNT(*) * 30 as cnt
				FROM release_artists
				JOIN buys
				ON release_artists.release_id=buys.release_id
				WHERE buys.user=%s
				GROUP BY release_artists.artists
			UNION ALL
				SELECT artists as artist, COUNT(*) * -5 as cnt
				FROM release_artists
				JOIN dislike
				ON release_artists.release_id=dislike.release_id
				WHERE dislike.user=%s
				GROUP BY release_artists.artists
				
			) as final
			WHERE cnt > 5
			GROUP by artist
			ORDER BY cnt DESC
			LIMIT 0,150
			"""

 
	

	#get the similar artists that appear more than once
	getRecs = db_select(sql,(userName,userName,userName,userName,userName,userName,userName,userName,userName,userName,userName))

	dataArtists = getRecs.fetchall()
	for artistRow in dataArtists:
		artist = str(artistRow[0])
		count = str(artistRow[1])
		key = None

		key = hashlib.md5(userName + artist).hexdigest()
		
		#now insert this into the artists_user_has_recd
		insertArtist = db_insert("INSERT INTO artists_user_has_recd (user,artist,the_key,count) VALUES (%s,%s,%s,%s) ON DUPLICATE KEY UPDATE count=VALUES(count)",(userName,artist,key,count))
		print "inserted " + artist + " for " + userName

	#now we find releases that are by those artists
	if stage=='onboarding':
		number_of_items = 50
	else:
		number_of_items = 2


	getReleases = db_select("""SELECT release_artists.release_id,release_artists.artists,releases.date FROM release_artists INNER JOIN artists_user_has_recd auhr ON auhr.artist=release_artists.artists INNER JOIN releases_all releases ON releases.id=release_artists.release_id LEFT JOIN recommendations ON recommendations.release_id=releases.id AND recommendations.user=auhr.user WHERE auhr.user=%s AND datediff(now(),releases.date) <= %s AND recommendations.release_id IS NULL
								GROUP BY release_artists.release_id ORDER BY auhr.count DESC LIMIT 0,""" + str(number_of_items) + """""",(userName,date_diff))
	dataReleases = getReleases.fetchall()
	count = 0

	#we reverse so that we can then sort the recommendations by rec.id
	dataReleases = reversed(dataReleases)

	# if stage=='onboarding':
	# 	dataReleases = dataReleases[0:50] #this gives us the first 70 releases which is what we want
		
	# else:
	# 	dataReleases = dataReleases[48:2] #this gives us the first 70 releases which is what we want
		
	

	
	

	for releasesRow in dataReleases:
			
				releaseId = str(releasesRow[0])
				key = hashlib.md5(userName + releaseId).hexdigest()
				insertRelease = db_insert("INSERT INTO recommendations (user,release_id,the_key) VALUES (%s,%s,%s) ON DUPLICATE KEY UPDATE the_key=VALUES(the_key)",(userName,releaseId,key))
				
				print "inserted " + releaseId
			


	

	print "Finished inserts for " + userName


	#display time taken to run script
	return("--- %s seconds ---" % (time.time() - start_time) + ' for ' + userName)



	

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'That an invalid method - check https://api.soundshelter.net for a list of valid methods'}), 404)	



@app.errorhandler(401)
def unauthorized(error):
    return make_response(jsonify({'error': 'Unauthorized access - invalid API key'}), 401)
		

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
