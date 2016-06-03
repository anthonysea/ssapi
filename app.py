#!flask/bin/python
from flask import Flask
#!flask/bin/python
from flask import Flask, request, render_template, jsonify,abort, make_response

#http://flask.pocoo.org/snippets/9/
from werkzeug.contrib.cache import SimpleCache

import collections

#database connect
from flaskext.mysql import MySQL
import json
import sys

import config

reload(sys)
sys.setdefaultencoding('utf-8')

app = Flask(__name__)
app.config.from_pyfile('config.py')
app.config['MYSQL_DATABASE_USER'] = config.user
app.config['MYSQL_DATABASE_PASSWORD'] = config.password
app.config['MYSQL_DATABASE_DB'] = config.database
app.config['MYSQL_DATABASE_HOST'] = config.host


mysql = MySQL()
mysql.init_app(app)

#http://flask.pocoo.org/snippets/9/
CACHE_TIMEOUT = 300
cache = SimpleCache()
class cached(object):

    def __init__(self, timeout=None):
        self.timeout = timeout or CACHE_TIMEOUT

    def __call__(self, f):
        def decorator(*args, **kwargs):
            response = cache.get(request.path)
            if response is None:
                response = f(*args, **kwargs)
                cache.set(request.path, response, self.timeout)
            return response
        return decorator


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/v1.0/<int:api_key>/release/<int:release_id>',methods=['GET'])
@cached()
def get_release(api_key,release_id):
	
	if str(api_key) !='2844':
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
		return "No record found"

	for x in range(0,numrows):
		row = cursor.fetchone()
		release_id = str(row[0])
		#artists = str(row[1])
		all_artists = str(row[2])
		title = str(row[4])
		label = str(row[6])
		genre = str(row[8])
		date = str(row[9])

		release_data = {'release_id':release_id,'artists':all_artists,'title':title,'label':label,'genre':genre,'date':date}

	#get savers
	#####pass release_id into query to get release details	
	cursor = mysql.connect().cursor()
	try:
		results = cursor.execute("SELECT artist from charts_extended where release_id='" + release_id + "'")
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
		saver_data.append(d)
		
	print saver_data

	

	final_data = {'details':release_data,'savers':saver_data}
	resp = jsonify(results=final_data)
	return resp


	

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)	



@app.errorhandler(401)
def unauthorized(error):
    return make_response(jsonify({'error': 'Unauthorized access - invalid API key'}), 401)
		

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
