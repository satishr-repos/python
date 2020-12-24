import os
import csv
import argparse
from datetime import datetime 
import sqlite3 as sql
from sqlite3 import Error

class sqldb:

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

class transaction:
	def __init__(self, pan, strategy, name, company, trdate, quantity, rate, brokerage, unitprice, totalprice):
		self.rec = dict() 
		self.rec['pan'] = pan.strip()
		self.rec['strategy'] = strategy.strip()
		self.rec['name'] = name.strip()
		self.rec['company'] = company.strip()
		self.rec['date'] = datetime.strptime(trdate,'%m/%d/%y').date()
		self.rec['quantity'] = int(quantity)
		self.rec['type'] = 'BUY' if self.rec['quantity'] > 0 else 'SELL'
		self.rec['rate'] = float(rate)
		self.rec['brokerage'] = float(brokerage)
		self.rec['unitprice'] = float(unitprice)
		self.rec['totalprice'] = abs(float(totalprice))

	def is_fy(self, fyyear):
		if(fyyear == 'all'):
			return True
		elif(self.rec['date'].year == int(fyyear) and self.rec['date'].month >= 4) or\
			(self.rec['date'].year == (int(fyyear)+1) and self.rec['date'].month <= 3):	
			return True
		else:
			return False

	def is_buy(self):
		return True if self.rec['type'] == 'BUY' else False

class transactions:
	def __init__(self):
		self.all_tx = []
		self.company_tx = dict()

	def add(self, T):
		self.all_tx.append(T)	
		self.company_tx.setdefault(T.rec['company'], []).append(T)

	def get_fy_data(self, fy, fields):
		recs = []
		for t in self.all_tx:
			r = [t.rec[f] for f in fields if t.is_fy(fy)]
			if r:
				recs.append(r)
		return recs

	def get_cw_data(self, fy, fields):
		recs = []
		empty = [''] * 6
		for c,lst in self.company_tx.items():
			for t in lst:
				b = empty.copy()
				s = empty.copy()
				if t.is_buy():
					b = [t.rec[f] for f in fields if t.is_fy(fy)]
				else:
					s = [t.rec[f] for f in fields if t.is_fy(fy)]
				
				r = b + s
				if r != empty:
					recs.append(r)
		return recs

def exporttocsv(filename, header, data):
	with open(filename, 'w') as cs:
		cswriter = csv.writer(cs)
		cswriter.writerow(header)
		cswriter.writerows(data)

def main(dbFile, csvFile, fy, cw):

	db = sqldb(dbFile)	
	names = db.get_table_names() 
	cols,rows = db.get_records(names[0])
	#print(cols)
	
	tx = transactions()
	for row in rows:
		t = transaction(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9])
		tx.add(t)
	
	del db

	fields=['date','company','quantity','type','unitprice', 'totalprice']
	#fields = ['date', 'company', 'quantity', 'type', 'totalprice']
	#fydata = tx.get_fy_data('2019', fields)
	#print(fydata)

	if cw == True:
		data = tx.get_cw_data(fy, fields)
		fields += fields
	else:
		data = tx.get_fy_data(fy, fields)

	print(data)

	exporttocsv(csvPath, fields, data)

	#print("{0}  {1:<40s} {2:6d} {3:10.4f}  {4:.4f}".format(t.trdate, t.company, t.quantity, t.unitprice, t.totalprice))

if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument('-i', '--dbpath', action='store', type=str, help="Database file path")
	parser.add_argument('-o', '--csvpath', action='store', type=str, help=".csv file to output the info")
	parser.add_argument('-y', '--fy', action='store', type=str, default='all',  help="get data pertaining to a particular FY")
	parser.add_argument('-c', '--companywise', action='store_true', help="get company wise transactions")
	args = parser.parse_args()

	dbPath = "./test.db" if args.dbpath == None else args.dbpath
	csvPath = "./out.csv" if args.csvpath == None else args.csvpath
	fy = args.fy
	cw = args.companywise

	main(dbPath, csvPath, fy, cw)

