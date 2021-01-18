import os
import fifocapgain
import xlsxwriter
import csv
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from datetime import datetime
from configparser import ConfigParser

FIFOCAPGAIN = "Fifo Capital Gain"
CONFIG_FILE = "pmsapp.ini"

class pmsconfig:
	
	def __init__(self):
		self.customers = []
		self.fy = "2019-20"
		self.dir = os.getcwd()
		self.server = None
		self.load_config()

	def __del__(self):
		pass

	def load_config(self):
		cp = ConfigParser(allow_no_value=True)
		cp.read(CONFIG_FILE)
		if cp.has_section('HA_PMS'):
			self.customers = cp.get('HA_PMS','customers').split(',')
			self.fy = cp.get('HA_PMS', 'fy')
			self.dir = cp.get('HA_PMS', 'defaultdir')
			self.server = cp.get('HA_PMS', 'servername')
			self.database = cp.get('HA_PMS', 'database')
			self.user = cp.get('HA_PMS', 'username')
			self.pwd = cp.get('HA_PMS', 'password')

		return

	def save_config(self):
		cp = ConfigParser(allow_no_value=True)
		cp.add_section('HA_PMS')
	
		strcustomers = ','.join(self.customers)

		cp.set('HA_PMS', 'customers', strcustomers)
		cp.set('HA_PMS', 'fy', self.fy)
		cp.set('HA_PMS', 'defaultdir', self.dir)
		cp.set('HA_PMS', '; Some other example server values are')
		cp.set('HA_PMS', '; server = localhost\sqlexpress # for a named instance')
		cp.set('HA_PMS', '; server = myserver,port # to specify an alternate port')
		cp.set('HA_PMS', 'servername', self.server)
		cp.set('HA_PMS', 'database', self.database)
		cp.set('HA_PMS', 'username', self.user)
		cp.set('HA_PMS', 'password', self.pwd)

		with open(CONFIG_FILE, 'w') as configfile:
			cp.write(configfile)

		return

class savetofile:
	def __init__(self, customer, fy, filetype='*.xlsx'):
		self.filetype = filetype
		self.customername = customer
		self.financialyear = fy

		fname = customer.replace(' ', '') + "_pmscapgain_" + fy
		
		fname = filedialog.asksaveasfilename(initialdir=config.dir, initialfile=fname, filetypes=[(filetype, filetype)])

		fname += filetype[1:]

		if filetype == '*.xlsx':
			self.wb = xlsxwriter.Workbook(fname)
			self.wb.formats[0].set_font_name('Times New Roman')
			self.wb.formats[0].set_font_size(11)

		# use this dir as initial directory next time
		config.dir = os.path.dirname(fname)
		self.filename = fname

	def __del__(self):
		if self.filetype == '*.xlsx':
			self.wb.close()

	#Set up some formats to use.
	def setup_formats(self):
		workbook = self.wb
		self.bold = workbook.add_format({'bold': True})
		self.italic = workbook.add_format({'italic': True})
		self.red = workbook.add_format({'color': 'red'})
		self.blue = workbook.add_format({'color': 'blue'})
		self.left= workbook.add_format({'align': 'left'})
		self.center = workbook.add_format({'align': 'center'})
		self.right = workbook.add_format({'align': 'right'})
		self.superscript = workbook.add_format({'font_script': 1})	
		self.border = workbook.add_format({'border':True})
		self.timesfont = workbook.add_format({'font_name' : 'Times New Roman'})
		self.size = workbook.add_format({'font_size' : 12})

		# Conditional numerical formatting.
		self.numfmt1 = workbook.add_format()
		self.numfmt1.set_num_format('[Green]General;[Red]-General;General')
		 # Add a number format for cells with money.
		self.money = workbook.add_format({'num_format': '$#,##0'})

		# Add an Excel date format.
		self.datefmt1 = workbook.add_format({'num_format': 'mmmm d yyyy'})

	def __writeascsv(self, headerinfo, data):
		with open(self.filename, 'w') as cs:
			cswriter = csv.writer(cs)

			header = [item[0] for item in headerinfo]

			cswriter.writerow(header)
			cswriter.writerows(data)

	def __writeasexcel(self, header, data):
		ws = self.wb.add_worksheet()

		captionfmt = self.wb.add_format({
						'bold': True,
						})

		headerfmt1 = self.wb.add_format({
						'bold': True, 
						'align': 'center',
						'bg_color' : '#FFF5EE',
						'border' : 1})
		
		headerfmt2 = self.wb.add_format({
						'bold': True, 
						'align': 'center',
						'bg_color' : '#F0FFF0',
						'border' : 1})
	
		headerfmt3 = self.wb.add_format({
						'bold': True, 
						'align': 'center',
						'bg_color' : '#FFFACD',
						'border' : 1})

		defaultfmt = self.wb.add_format({
						'align': 'left',
						'border' : 1})

		datefmt1 = self.wb.add_format({
						'num_format' : 'dd-mmm-yyyy',
						'align': 'left',
						'border' : 1})
		
		numfmt1 = self.wb.add_format({
						'num_format' : '[Green]General;[Red]-General;General',
						'align': 'center',
						'border' : 1})
		
		numfmt2 = self.wb.add_format({
						'num_format' : '[Black]#,##0.0000;[Red]-#,##0.0000',
						'align': 'left',
						'border' : 1})

		numfmt3 = self.wb.add_format({
						'num_format' : '[Black]#,##0.00;[Red]-#,##0.00',
						'align': 'center',
						'border' : 1})


		ws.write(1, 1, 'Customer:', captionfmt)
		ws.write(1, 2, self.customername, captionfmt)
		ws.write(2, 1, 'FY:', captionfmt)
		ws.write(2, 2, self.financialyear, captionfmt)


		ws.merge_range(4,1, 4, 5, 'SELL', headerfmt1)
		ws.merge_range(4,6, 4, 10, 'BUY', headerfmt2)
		ws.merge_range(4,11, 4, 12, 'CAPITAL GAINS', headerfmt3)

		row = 5
		for col, item in enumerate(header):
			if col < 5:
				headerfmt = headerfmt1
			elif col < 10:
				headerfmt = headerfmt2 
			else:
				headerfmt = headerfmt3 

			ws.write(row, col+1, item[0], headerfmt)
			ws.set_column(col+1, col+1, item[2])

		row += 1 
		col = 1
		for i, record in enumerate(data):
			for j, val in enumerate(record):
				if header[j][1] == 'date':
					datafmt = datefmt1
				elif header[j][1] == 'int':
					datafmt = numfmt3
				elif header[j][1] == 'currency':
					datafmt = numfmt2
				else:
					datafmt = defaultfmt
			
				ws.write(row+i, col+j, val, datafmt)	

	def write(self, header, data):
		
		if self.filetype == '*.xlsx':
			self.__writeasexcel(header, data)				
		elif self.filetype == '*.csv':
			self.__writeascsv(header, data)
		else:
			pass	

def execute_query():
	global treev
	global header, records

	if pmsQuery.get() == FIFOCAPGAIN:	
		header, records = fifocapgain.get_fifo_cap_gains(config.server, config.database, config.user, config.pwd, custName.get(), fyYear.get())
		if records == None:
			messagebox.showwarning('No Data', 'Error connecting to SQL Server or no data')
			return

	if custName.get() not in config.customers:
		config.customers.append(custName.get())
	
	# clear tree view
	for i in treev.get_children():
		treev.delete(i)

	treev['columns'] = list(range(0, len(header))) 	
	for i, item in enumerate(header):
		treev.heading(i, text=item[0], anchor=W)
		treev.column(i, width=item[2]*5)
		
	i = 0
	for rec in records:
		if i % 2 == 0:
			treev.insert('', 'end', values=rec[0:len(header)], tags=('evenrow',))
		else:
			treev.insert('', 'end', values=rec[0:len(header)], tags=('oddrow',))
		i += 1

	return

def save_data_as():
	storedata = savetofile(custName.get(), fyYear.get(), fileType.get())
	storedata.write(header, records)

	return

root = Tk()
root.title('Query Financial Data')
root.geometry('700x600')

# load config
global config
config = pmsconfig()
if not config.server:
	messagebox.showerror('No config file', 'Server information not available')
	exit()	

s = ttk.Style()
s.configure('Treeview', 
	background='white', 
	foreground='black',
	rowheight=25,
	fieldbackground='white')
s.map('Treeview', background=[('selected', 'gold')])

#s.theme_use('default')


# first frame settings

frame1 = ttk.LabelFrame(root, text="Query", height=50)
frame1.pack(expand="yes", fill="both", padx=10)

nameLbl = Label(frame1, text="Customer Name: ", padx=5)
nameLbl.grid(row=0, column=0)

custName = ttk.Combobox(frame1, value=config.customers)
custName.grid(row=0, column=1)


queryBtn = Button(frame1, text=" Execute Query", padx=10, command=execute_query)
#queryBtn.config(width=20)
queryBtn.grid(row=0, column=3, padx=(20,5))

pmsQueries = [FIFOCAPGAIN]
pmsQuery = StringVar()
queryMenu = OptionMenu(frame1, pmsQuery, *pmsQueries)
queryMenu.config(width=20)
pmsQuery.set(pmsQueries[0])
queryMenu.grid(row=0, column=4)

# second frame settings

frame2 = ttk.LabelFrame(root, text='Options', height=100)
frame2.pack(expand="yes", fill="both", padx=10, pady=5)

fyLbl = Label(frame2, text="Financial Year: ", padx=5)
fyLbl.grid(row=0, column=0)

def get_fy_year(year=2012):
	fy = []
	current = int(datetime.now().year)
	while year <= current:
		nextYear = str(year+1)
		fy_year = "{0:d}-{1:s}".format(year, nextYear[-2:])
		fy.append(fy_year)
		year += 1
	return fy

fyYears = get_fy_year()
fyYear = StringVar()
fyMenu = OptionMenu(frame2, fyYear, *fyYears)
fyMenu.config(width=20)
fyYear.set(config.fy)
fyMenu.grid(row=0, column=1)

# third frame settings

frame3 = ttk.LabelFrame(root, text='', borderwidth=0, height=400)
frame3.pack(expand="yes", fill="both", padx=10, pady=(0,3))

vscroll = ttk.Scrollbar(frame3, orient='vertical')
vscroll.pack(side='right', fill=Y)

hscroll = ttk.Scrollbar(frame3, orient='horizontal')
hscroll.pack(side='bottom', fill=X)

treev = ttk.Treeview(frame3, selectmode='browse', yscrollcommand=vscroll.set, xscrollcommand=hscroll.set)
treev.pack(expand='yes', fill='both')

treev.tag_configure('oddrow', background='white')
treev.tag_configure('evenrow', background='#EBF5FB')
	
# Defining heading 
treev['show'] = 'headings'

vscroll.configure(command=treev.yview)
hscroll.configure(command=treev.xview)

saveAsBtn = Button(root, text="Save As...", padx=20, command=save_data_as)
saveAsBtn.pack(side='left', padx=10, pady=(0, 10))

fileTypes = ['*.xlsx', '*.csv', '*.pdf']
fileType = StringVar()
fileOption = OptionMenu(root, fileType, *fileTypes)
fileType.set(fileTypes[0])
fileOption.pack(side='left', pady=(0,10))

#sbarVar = StringVar()
#sbarVar.set('status bar...') 
#sbar = ttk.Label(root, textvariable=sbarVar, borderwidth=1, relief=GROOVE, anchor=E, font=('Courier', 12))
#sbar.pack(fill=X, padx=10, pady=2)

root.mainloop()

config.fy = fyYear.get()
config.save_config()
