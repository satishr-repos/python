import os
import copy
import sqlconn
from datetime import datetime 

PAN = 'pan'
STRATEGY = 'strategy'
NAME = 'name'
DATE = 'date'
COMPANY = 'company'
QUANTITY = 'quantity'
TYPE = 'type'
UNIT_PRICE = 'unitprice'
TOTAL_PRICE = 'totalprice'

SHORT_CAPGAINS = 'short term'
LONG_CAPGAINS = 'long term'

class transaction:
	def __init__(self, strategy, pan, name, company, trdate, quantity, totalprice, unitprice):
		self.rec = {PAN : pan.strip(), 
					STRATEGY : strategy.strip(),
					NAME : name.strip(),
					COMPANY : company.strip(),
					DATE : trdate.date(),
					QUANTITY : int(quantity),
					TYPE : 'BUY' if int(quantity) > 0 else 'SELL',
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

	def __calculatecapgains(self, sell, buy):
		sell_date = sell.rec[DATE]
		sell_unitprice = sell.rec[UNIT_PRICE]
		
		buy_date = buy.rec[DATE]
		buy_quantity = buy.rec[QUANTITY]
		buy_totalprice = buy.rec[TOTAL_PRICE]

		cap_gains = (buy_quantity * sell_unitprice) - buy_totalprice
		cap_gains = round(cap_gains, 4)

		lt = 0
		st = 0

		if (sell_date - buy_date).days > 365:
			lt = cap_gains
		else:
			st = cap_gains

		return st, lt

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

				short_term, long_term = self.__calculatecapgains(self.all_tx[i], self.all_tx[j])

				r.append(short_term)
				r.append(long_term)

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

def get_fifo_cap_gains(server, database, user, pwd, customerName, fyYear):

	db = sqlconn.sqlconn(server, database, user, pwd)
	if db.connect() == False:
		return None,None

	rows = db.get_server_version()
	for row in rows:
		print(row[0])

	SQL = "exec [dbo].[procFIFOCapitalGain] @InvestorName = ?"
	params = ("%"+customerName+"%")

	rows = db.exec_sp(SQL, params)
	print(rows[0])
	
	tx = transactions()
	for row in rows:
		t = transaction(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
		tx.add(t)
	
	del db

	fields=[DATE,COMPANY,QUANTITY,UNIT_PRICE, TOTAL_PRICE]
	#fields = [PAN, STRATEGY, NAME, TYPE]

	data = tx.get_fifo_data(fyYear[0:4], fields)

	print(data)

	#print("{0}  {1:<40s} {2:6d} {3:10.4f}  {4:.4f}".format(t.trdate, t.company, t.quantity, t.unitprice, t.totalprice))

	header = [(DATE, 'date', 12), (COMPANY, 'str', 30), (QUANTITY, 'int', 10), (UNIT_PRICE, 'currency', 12), (TOTAL_PRICE, 'currency', 15),
				(DATE, 'date', 12), (COMPANY, 'str', 35), (QUANTITY, 'int', 10), (UNIT_PRICE, 'currency', 12), (TOTAL_PRICE, 'currency', 15),
				(SHORT_CAPGAINS, 'currency', 15), (LONG_CAPGAINS, 'currency', 15)]

	return header, data
