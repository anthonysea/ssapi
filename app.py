#!flask/bin/python
from flask import Flask
#!flask/bin/python
from flask import Flask, request, render_template, jsonify,abort, make_response
#database connect
from flaskext.mysql import MySQL
import json
import sys

import config



reload(sys)
sys.setdefaultencoding('utf-8')

app = Flask(__name__)

app.config['MYSQL_DATABASE_USER'] = config.user
app.config['MYSQL_DATABASE_PASSWORD'] = config.password
app.config['MYSQL_DATABASE_DB'] = config.database
app.config['MYSQL_DATABASE_HOST'] = config.host

#mysql = MySQL()
#mysql.init_app(app)


@app.route('/ss/api/v1.0/<int:api_key>/release/<int:release_id>',methods=['GET'])
def get_release(api_key,release_id):
	
	if str(api_key) !='2844':
		abort(401)
	release_id = str(release_id) #convert to string
	####check that we recieved a release_id
	if len(release_id) ==0:
		abort(404)
	
	return release_id

	#####pass release_id into query to get release details	
	#cursor = mysql.connect().cursor()
	#cursor.execute("SELECT * from releases where id='" + release_id + "'")
	

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)	



@app.errorhandler(401)
def unauthorized(error):
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)
		

if __name__ == '__main__':
    app.run(debug=True)