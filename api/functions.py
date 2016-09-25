def db_select(query,params):

	host = os.environ.get("db_host")
	user = str(os.environ.get("db_user"))
	password = str(os.environ.get("db_password"))
	db = str(os.environ.get("db_db"))

	
	db = MySQLdb.connect(host,user,password,db)
	cur = db.cursor()
	cur.execute(query,params)
	db.close()	
	return cur

	