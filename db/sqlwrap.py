import os
import sqlite3 as sql
from sqlite3 import Error

class sqlwrap:

	def __init__(self, dbPath):
		self.conn = None

		try:
			if(not os.path.isfile(dbPath)):
				raise ValueError

			self.dbPath = dbPath
			self.conn = sql.connect(dbPath)
		except Error as e:
			print(e)

	def __del__(self):
		if self.conn:
			self.conn.close()

	def get_table_names(self):
		cur = self.conn.cursor()
		cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
		return cur.fetchall()

	def get_records(self, tableName):
		cur = self.conn.cursor()
		cur.execute("SELECT * FROM %s;" %(tableName))

		cols = [col[0] for col in cur.description]
		rows = cur.fetchall()
	
		return cols,rows;

