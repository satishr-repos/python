import pyodbc 

class sqlconn:
	def __init__(self, server, database, user, pwd):

		self.conn = None
		self.sqlString = 'DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+user+';PWD='+ pwd

	def __del__(self):
		if self.conn:
			self.cursor.close()
			self.conn.close()

	def connect(self):
		try:
			self.conn = pyodbc.connect(self.sqlString)
			self.cursor = self.conn.cursor()
			return True
		except Exception as e:
			print(e)
			return False

	def get_server_version(self):
		self.cursor.execute("SELECT @@version;")
		return self.cursor.fetchall()
	
	def get_server_name(self):
		self.cursor.execute("SELECT @@servername;")
		return self.cursor.fetchall()
            
	def get_table_names(self):
		self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
		return self.cursor.fetchall()

	def exec_sp(self, sqlProc, params):
		self.cursor.execute(sqlProc, params)
		return self.cursor.fetchall()

	def get_records(self, tableName):
		self.cursor.execute("SELECT * FROM %s;" %(tableName))

		cols = [col[0] for col in cur.description]
		rows = self.cursor.fetchall()
	
		return cols,rows;
