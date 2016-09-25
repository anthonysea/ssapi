#!flask/bin/python
import sys
sys.path.append("/var/www/ssapi/api")
sys.path.append('/var/www/ssapi')

from flask import Flask, request, render_template, jsonify,abort, make_response
from flask.ext.cache import Cache
import time
import hashlib

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
@app.route('/api/v1.0/<int:api_key>/user/<string:user>/updateRecommendations',methods=['GET'])
def update_recommendations(api_key,user):
	if str(api_key)!=the_api_key:
		abort(401)
	userName = str(user)
	start_time = time.time() 
 
	

	
		
	#get the similar artists that appear more than once
	getRecs = db_select("SELECT DISTINCT similar.similar_artist,COUNT(similar.similar_artist) as cnt FROM release_artists INNER JOIN charts_extended ON charts_extended.release_id=release_artists.release_id INNER JOIN similar ON release_artists.artists=similar.artist INNER JOIN users ON users.name=charts_extended.artist WHERE users.name=%s GROUP BY similar.similar_artist HAVING COUNT(similar.similar_artist) > 0 UNION SELECT DISTINCT release_artists.artists ,COUNT(release_artists.artists) as cnt FROM release_artists INNER JOIN charts_extended ce ON ce.release_id=release_artists.release_id WHERE ce.artist=%s GROUP by release_artists.artists HAVING COUNT(release_artists.artists) > 0 ORDER BY cnt DESC",(userName,userName,))




	dataArtists = getRecs.fetchall()
	for artistRow in dataArtists:
		artist = str(artistRow[0])
		count = str(artistRow[1])
		key = None

		key = hashlib.md5(userName + artist).hexdigest()
		
		#now insert this into the artists_user_has_recd
		insertArtist = db_insert("INSERT INTO artists_user_has_recd (user,artist,the_key,count) VALUES (%s,%s,%s,%s) ON DUPLICATE KEY UPDATE count=VALUES(count)",(userName,artist,key,count))
		#print "inserted " + artist + " for " + userName

	#now we find releases that are by those artists

	getReleases = db_select("SELECT release_id,release_artists.artists,releases.date FROM release_artists INNER JOIN artists_user_has_recd auhr ON auhr.artist=release_artists.artists  INNER JOIN releases ON releases.id=release_artists.release_id WHERE auhr.user=%s AND datediff(now(),releases.date) < 180 GROUP BY release_artists.release_id ORDER BY auhr.count ASC",(userName,))
	dataReleases = getReleases.fetchall()
	count = 0
	
	#dataReleases = dataReleases[0:50] #this gives us the first 10 releases which is what we want

	for releasesRow in dataReleases:
			
				releaseId = str(releasesRow[0])
				key = hashlib.md5(userName + releaseId).hexdigest()
				insertRelease = db_insert("INSERT INTO recommendations (user,release_id,the_key) VALUES (%s,%s,%s) ON DUPLICATE KEY UPDATE the_key=VALUES(the_key)",(userName,releaseId,key))
				
				print "inserted " + releaseId
				

	#now store the labels that a user has recommended more than once
	getLabels = db_select("SELECT releases.label_no_country,COUNT(releases.label_no_country) FROM releases INNER JOIN charts_extended ce ON ce.release_id=releases.id WHERE ce.artist=%s GROUP by releases.label_no_country HAVING COUNT(releases.label_no_country) > 1 ORDER BY COUNT(releases.label_no_country) ASC",(userName,))
	dataLabels = getLabels.fetchall()

	for labelRow in dataLabels:
		label = str(labelRow[0])
		count = str(labelRow[1])
		print label + ': ' + count
		key = hashlib.md5(userName + label).hexdigest()
		insertLabel = db_insert("INSERT INTO labels_user_has_recd (user,label,the_key,count) VALUES (%s,%s,%s,%s) ON DUPLICATE KEY UPDATE the_key=VALUES(the_key),count=VALUES(count)",(userName,label,key,count))


	#now we find releases that are on these labels
	getReleases = db_select("SELECT releases.id,releases.label_no_country,releases.date FROM releases INNER JOIN labels_user_has_recd luhr ON luhr.label=releases.label_no_country WHERE luhr.user=%s AND datediff(now(),releases.date) < 180 GROUP BY releases.label_no_country ORDER BY releases.date DESC",(userName,))
	dataReleases = getReleases.fetchall()
	count =0

	dataReleases = dataReleases[0:40] #this gives us the first 10 releases which is what we want
	
	for releasesRow in dataReleases:

		releaseId = str(releasesRow[0])
		key = hashlib.md5(userName + releaseId).hexdigest()
		insertRelease = db_insert("INSERT INTO recommendations (user,release_id,the_key) VALUES (%s,%s,%s) ON DUPLICATE KEY UPDATE the_key=VALUES(the_key)",(userName,releaseId,key))
		count = count + 1
			#print "inserted " + releaseId

	print "Finished inserts for " + userName


	#display time taken to run script
	return("--- %s seconds ---" % (time.time() - start_time))



	

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'That an invalid method - check https://api.soundshelter.net for a list of valid methods'}), 404)	



@app.errorhandler(401)
def unauthorized(error):
    return make_response(jsonify({'error': 'Unauthorized access - invalid API key'}), 401)
		

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
