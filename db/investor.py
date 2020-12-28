import os
import csv
import copy
import argparse
import sqlwrap
from datetime import datetime 

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

	def __fifo_recs(self, fifos, fy, fields):
		recs = []
		empty = [''] * 6
		for i,lst in fifos.items():
			s = [self.all_tx[i].rec[f] for f in fields if self.all_tx[i].is_fy(fy)]
			if(len(s) == 0):
				continue
			
			for j in lst:
				b = [self.all_tx[j].rec[f] for f in fields]
				if(lst[0] == j):
					r = s + b
				else:
					r = empty + b
				recs.append(r)
		return recs

	def get_fifo_data(self, fy, fields):
		fifos = dict()
		for c,lst in self.company_tx.items():
			buys = [self.all_tx.index(t) for t in lst if t.is_buy()]
			sells = [self.all_tx.index(t) for t in lst if not t.is_buy()]
			for i in sells:
				fifos.setdefault(i, [])
				sellqty = abs(self.all_tx[i].rec['quantity'])
				while(sellqty > 0):
					try:
						j = buys.pop(0)
						if(self.all_tx[i].rec['date'] < self.all_tx[j].rec['date']):
							print('{0:s} Ignore Sell:{1:%Y/%m/%d} {2:d} before Buy:{3:%Y/%m/%d} {4:d}'\
								.format(c, self.all_tx[i].rec['date'], self.all_tx[i].rec['quantity'],\
								self.all_tx[j].rec['date'], self.all_tx[j].rec['quantity']))
							continue
						buyqty = self.all_tx[j].rec['quantity']	
						fifos[i].append(j)
						if(buyqty > sellqty):
							new = copy.deepcopy(self.all_tx[j])
							unitprice = new.rec['totalprice'] / new.rec['quantity']
							self.all_tx[j].rec['quantity'] = sellqty
							self.all_tx[j].rec['company'] = c + '(PARTIAL)'							
							self.all_tx[j].rec['totalprice'] = round(unitprice * sellqty,4)
							new.rec['quantity'] = buyqty - sellqty
							new.rec['company'] = c + '(PARTIAL)'
							new.rec['totalprice'] = round(unitprice * new.rec['quantity'],4)
							self.all_tx.append(new)
							buys.insert(0, self.all_tx.index(new))
						sellqty -= buyqty
					except IndexError:
						print("no corresponding buy for sell(%s: %d)" % (c, sellqty))
						break				
		return self.__fifo_recs(fifos, fy, fields)

def exporttocsv(filename, header, data):
	with open(filename, 'w') as cs:
		cswriter = csv.writer(cs)
		cswriter.writerow(header)
		cswriter.writerows(data)

def main(dbFile, csvFile, fy, cw, fifo):

	db = sqlwrap.sqlwrap(dbFile)	
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
	elif fifo == True:
		data = tx.get_fifo_data(fy, fields)
		fields += fields
	else:
		data = tx.get_fy_data(fy, fields)

	print(data)

	exporttocsv(csvPath, fields, data)

	#print("{0}  {1:<40s} {2:6d} {3:10.4f}  {4:.4f}".format(t.trdate, t.company, t.quantity, t.unitprice, t.totalprice))

if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument('-i', '--dbpath', action='store', type=str, default='./test.db',  help="Database file path")
	parser.add_argument('-o', '--csvpath', action='store', type=str, default='./out.csv', help=".csv file to output the info")
	parser.add_argument('-y', '--fy', action='store', type=str, default='all',  help="get data pertaining to a particular FY")
	parser.add_argument('-c', '--companywise', action='store_true', help="get company wise transactions")
	parser.add_argument('-f', '--fifo', action='store_true', help="get first in first out sell transactions")
	args = parser.parse_args()

	dbPath = args.dbpath
	csvPath = args.csvpath
	fy = args.fy
	cw = args.companywise
	fifo = args.fifo

	main(dbPath, csvPath, fy, cw, fifo)

