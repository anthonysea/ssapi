from flask import Flask, request, render_template, jsonify,abort, make_response
from flaskext.mysql import MySQL
import config
#this is for the function db_select
import MySQLdb

app = Flask(__name__)
app.config.from_object('config')


app.config['MYSQL_DATABASE_USER'] = config.user
app.config['MYSQL_DATABASE_PASSWORD'] = config.password
app.config['MYSQL_DATABASE_DB'] = config.database
app.config['MYSQL_DATABASE_HOST'] = config.host



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