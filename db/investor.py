import os
import csv
import copy
import argparse
import sqlwrap
from datetime import datetime 

PAN = 'pan'
STRATEGY = 'strategy'
NAME = 'name'
DATE = 'date'
COMPANY = 'company'
QUANTITY = 'quantity'
TYPE = 'type'
RATE = 'rate'
BROKERAGE = 'brokerage'
UNIT_PRICE = 'unitprice'
TOTAL_PRICE = 'totalprice'

class transaction:
	def __init__(self, pan, strategy, name, company, trdate, quantity, rate, brokerage, unitprice, totalprice):
		self.rec = {PAN : pan.strip(), 
					STRATEGY : strategy.strip(),
					NAME : name.strip(),
					COMPANY : company.strip(),
					DATE : datetime.strptime(trdate, "%m/%d/%y").date(),
					QUANTITY : int(quantity),
					TYPE : 'BUY' if int(quantity) > 0 else 'SELL',
					RATE : float(rate),
					BROKERAGE : float(brokerage),
					UNIT_PRICE : float(unitprice),
					TOTAL_PRICE : abs(float(totalprice)) }

	def is_fy(self, fyyear):
		if(fyyear == 'all'):
			return True
		
		fy_apr = datetime(int(fyyear), 4, 1).date()
		fy_mar = datetime(int(fyyear)+1, 3, 31).date()
		if((self.rec[DATE] >= fy_apr) and (self.rec[DATE] <= fy_mar)):
			return True
		else:
			return False
	
	def is_buy(self):
		return True if self.rec[TYPE] == 'BUY' else False

class transactions:
	def __init__(self):
		self.all_tx = []
		self.company_tx = dict()

	def add(self, T):
		self.all_tx.append(T)	
		self.company_tx.setdefault(T.rec[COMPANY], []).append(T)

	def get_fy_data(self, fy, fields):
		recs = []
		for t in self.all_tx:
			r = [t.rec[f] for f in fields if t.is_fy(fy)]
			if r:
				recs.append(r)
		return recs

	def get_cw_data(self, fy, fields):
		recs = []
		empty = [''] * len(fields)
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
		empty = [''] * len(fields)
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
				sellqty = abs(self.all_tx[i].rec[QUANTITY])
				while(sellqty > 0):
					try:
						j = buys.pop(0)
						if(self.all_tx[i].rec[DATE] < self.all_tx[j].rec[DATE]):
							print('{0:s} Ignore Sell:{1:%Y/%m/%d} {2:d} before Buy:{3:%Y/%m/%d} {4:d}'\
								.format(c, self.all_tx[i].rec[DATE], self.all_tx[i].rec[QUANTITY],\
								self.all_tx[j].rec[DATE], self.all_tx[j].rec[QUANTITY]))
							continue
						buyqty = self.all_tx[j].rec[QUANTITY]	
						fifos[i].append(j)
						if(buyqty > sellqty):
							new = copy.deepcopy(self.all_tx[j])
							unitprice = new.rec[TOTAL_PRICE] / new.rec[QUANTITY]
							self.all_tx[j].rec[QUANTITY] = sellqty
							self.all_tx[j].rec[COMPANY] = c + ' (FIFO)'							
							self.all_tx[j].rec[TOTAL_PRICE] = round(unitprice * sellqty,4)
							new.rec[QUANTITY] = buyqty - sellqty
							new.rec[COMPANY] = c + ' (FIFO)'
							new.rec[TOTAL_PRICE] = round(unitprice * new.rec[QUANTITY],4)
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
	
	tx = transactions()
	for row in rows:
		t = transaction(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9])
		tx.add(t)
	
	del db

	fields=[DATE,COMPANY,QUANTITY,TYPE,UNIT_PRICE, TOTAL_PRICE]
	#fields = [PAN, STRATEGY, NAME, BROKERAGE, RATE]

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

