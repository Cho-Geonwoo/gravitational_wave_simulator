#-*-coding:utf-8
from Tkinter import *
import tkFileDialog, tkMessageBox 
import Image, ImageTk, ImageFilter
from scipy.interpolate import interp1d
import math
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import numpy as np
################Deifine global variable####################
clight = 2.99792458e8                # m/s
G = 6.67259e-11                      # m^3/kg/s^2 
MSol = 1.989e30                      # kg
biglist = []

class ClickPlot:

	"""
	A clickable matplotlib figure
	
	Usage:
	>>> import clickplot
	>>> retval = clickplot.showClickPlot()
	>>> print retval['subPlot']
	>>> print retval['x']
	>>> print retval['y']
	>>> print retval['comment']
	
	See an example below
	"""

	def __init__(self, fig=None):
	
		"""
		Constructor
		
		Arguments:
		fig -- a matplotlib figure
		"""
	
		if fig != None:
			self.fig = fig		
		else:
			self.fig = plt.get_current_fig_manager().canvas.figure
		self.nSubPlots = len(self.fig.axes)
		self.dragFrom = None
		self.comment = '0'
		self.markers = []
				
		self.retVal = {'comment' : self.comment, 'x' : None, 'y' : None,
			'subPlot' : None}		

		self.sanityCheck()
		self.fig.canvas.mpl_connect('button_press_event', self.onClick)
		self.fig.canvas.mpl_connect('button_release_event', self.onRelease)		
		self.fig.canvas.mpl_connect('scroll_event', self.onScroll)
		self.fig.canvas.mpl_connect('key_press_event', self.onKey)
		
	def clearMarker(self):
	
		"""Remove marker from retVal and plot"""
		
		self.retVal['x'] = None
		self.retVal['y'] = None
		self.retVal['subPlot'] = None
		for i in range(self.nSubPlots):
			subPlot = self.selectSubPlot(i)
			for marker in self.markers:
				if marker in subPlot.lines:
					subPlot.lines.remove(marker)				
		self.markers = []
		self.fig.canvas.draw()
		
	def getSubPlotNr(self, event):
	
		"""
		Get the nr of the subplot that has been clicked
		
		Arguments:
		event -- an event
		
		Returns:
		A number or None if no subplot has been clicked
		"""
	
		i = 0
		axisNr = None
		for axis in self.fig.axes:
			if axis == event.inaxes:
				axisNr = i		
				break
			i += 1
		return axisNr
		
	def sanityCheck(self):
	
		"""Prints some warnings if the plot is not correct"""
		
		subPlot = self.selectSubPlot(0)
		minX = subPlot.dataLim.min[0]
		maxX = subPlot.dataLim.max[0]				
		for i in range(self.nSubPlots):
			subPlot = self.selectSubPlot(i)
			_minX = subPlot.dataLim.min[0]
			_maxX = subPlot.dataLim.max[0]
			if abs(_minX-minX) != 0 or (_maxX-maxX) != 0:
				import warnings		
				warnings.warn('Not all subplots have the same X-axis')
		
	def show(self):
	
		"""
		Show the plot
		
		Returns:
		A dictionary with information about the response
		"""
	
		plt.show()
		self.retVal['comment'] = self.comment
		return self.retVal
		
	def selectSubPlot(self, i):
	
		"""
		Select a subplot
		
		Arguments:
		i -- the nr of the subplot to select
		
		Returns:
		A subplot
		"""
	
		plt.subplot('%d1%d' % (self.nSubPlots, i+1))
		return self.fig.axes[i]

	def onClick(self, event):
	
		"""
		Process a mouse click event. If a mouse is right clicked within a
		subplot, the return value is set to a (subPlotNr, xVal, yVal) tuple and
		the plot is closed. With right-clicking and dragging, the plot can be
		moved.
		
		Arguments:
		event -- a MouseEvent event
		"""		
	
		subPlotNr = self.getSubPlotNr(event)		
		if subPlotNr == None:
			return
		
		if event.button == 1:				
		
			self.clearMarker()
			for i in range(self.nSubPlots):
				subPlot = self.selectSubPlot(i)								
				marker = plt.axvline(event.xdata, 0, 1, linestyle='--', \
					linewidth=2, color='gray')
				self.markers.append(marker)

			self.fig.canvas.draw()
			self.retVal['subPlot'] = subPlotNr
			self.retVal['x'] = event.xdata
			self.retVal['y'] = event.ydata
			print self.retVal['x']
			print self.retVal['y']
			biglist.append([self.retVal['x'],self.retVal['y']])
		else:			
			# Start a dragFrom
			self.dragFrom = event.xdata
			
	def onKey(self, event):
	
		"""
		Handle a keypress event. The plot is closed without return value on
		enter. Other keys are used to add a comment.
		
		Arguments:
		event -- a KeyEvent
		"""
	
		if event.key == 'enter':
			plt.close()
			return
			
		if event.key == 'escape':
			self.clearMarker()
			return
			
		if event.key == 'backspace':
			self.comment = self.comment[:-1]
		elif len(event.key) == 1:			
			self.comment += event.key
		self.supTitle.set_text("comment: %s" % self.comment)
		event.canvas.draw()
			
	def onRelease(self, event):
	
		"""
		Handles a mouse release, which causes a move
		
		Arguments:
		event -- a mouse event
		"""
	
		if self.dragFrom == None or event.button != 3:
			return			
		dragTo = event.xdata
		dx = self.dragFrom - dragTo
		for i in range(self.nSubPlots):
			subPlot = self.selectSubPlot(i)			
			xmin, xmax = subPlot.get_xlim()
			xmin += dx
			xmax += dx				
			subPlot.set_xlim(xmin, xmax)
		event.canvas.draw()
											
	def onScroll(self, event):
	
		"""
		Process scroll events. All subplots are scrolled simultaneously
		
		Arguments:
		event -- a MouseEvent
		"""
	
		for i in range(self.nSubPlots):
			subPlot = self.selectSubPlot(i)		
			xmin, xmax = subPlot.get_xlim()
			dx = xmax - xmin
			cx = (xmax+xmin)/2
			if event.button == 'down':
				dx *= 1.1
			else:
				dx /= 1.1
			_xmin = cx - dx/2
			_xmax = cx + dx/2	
			subPlot.set_xlim(_xmin, _xmax)
		event.canvas.draw()
		
def showClickPlot(fig=None):

	"""
	Show a plt and return a dictionary with information
	
	Returns:
	A dictionary with the following keys:
	'subPlot' : the subplot or None if no marker has been set
	'x' : the X coordinate of the marker (or None)
	'y' : the Y coordinate of the marker (or None)
	'comment' : a comment string	
	"""

	cp = ClickPlot(fig)
	return cp.show()
	
class App(object): 
        def __init__(self): 
                #기본적인 틀 구축
                self.root=Tk()     
                self.root.title("signal analyzer")
                self.menu=Menu(self.root) 
                self.root.config(menu=self.menu); 
                self.label=Label(self.root, text="", width=50, height=20) 
                self.label.pack() 
                
                self.filemenu=Menu(self.menu)
                self.menu.add_cascade(label="File", menu=self.filemenu) 
                self.filemenu.add_command(label="Open", command=self.OpenFile, accelerator="Ctrl+o") 
                self.filemenu.add_separator() 
                self.filemenu.add_command(label="Quit", command=self.Quit, accelerator="Ctrl+q")
                self.filemenu.add_separator()
                self.filemenu.add_command(label="Save", command=self.Save, accelerator="Ctrl+s")
                self.filemenu.add_separator()
                self.filemenu.add_command(label="OpenImage", command=self.OpenImage, accelerator="Ctrl+f")                

                self.editmenu=Menu(self.menu) 
                self.menu.add_cascade(label="Edit", menu=self.editmenu)
                self.editmenu.add_command(label="Draw graph", command=self.Dg, accelerator="Ctrl+i") 
                self.editmenu.add_separator()
                self.editmenu.add_command(label="Noise", command=self.Noise, accelerator="Ctrl+l")
                self.editmenu.add_separator()
                self.editmenu.add_command(label="Chirp mass", command=self.Cm, accelerator="Ctrl+d")   
                self.editmenu.add_separator()
               
                self.directormenu=Menu(self.menu)
                
                self.menu.add_cascade(label="Director", menu=self.directormenu)
                self.directormenu.add_command(label="show",command=self.Director,accelerator="F12")

                self.root.bind("<Control-o>",self.OpenFile) 
                self.root.bind("<Control-q>",self.Quit) 
                self.root.bind("<Control-i>",self.Dg)
                self.root.bind("<Escape>",self.Quit) 
                self.root.bind("<Control-s>", self.Save)
                self.root.bind("<Control-l>", self.Noise)
                self.root.bind("<Control-d>", self.Cm)
                self.root.bind("<Control-f>",self.OpenImage) 
                self.root.bind("<F12>",self.Director)
                self.filename = None
                self.filename2 = None
                self.signal = None
                self.realsignal = []
                self.Image = None
                self.Image2 = None
                self.frequency = 0
                self.differentiate = 0
                self.contractvar = DoubleVar()
                self.root.mainloop() 
                
        def OpenFile(self,event=None): 
                self.filename=tkFileDialog.askopenfilename() 
                if(self.filename==""): 
                        return 
                try: 
                        self.signal=open(self.filename, "r") 
                except: 
                        tkMessageBox.showerror("오류 !","파일 열기에 실패했습니다.") 
                else:
                        self.realsignal=self.signal.read()
                        self.realsignal=self.realsignal.split('\n')
                        self.realsignal=[float(x[:10]) for x in self.realsignal]
			
        def OpenImage(self,event=None): 
                self.filename2=tkFileDialog.askopenfilename() 
                if(self.filename2==""): 
                        return 
                try: 
                        self.Image=Image.open(self.filename2) 
                except: 
                        tkMessageBox.showerror("오류 !","파일 열기에 실패했습니다.") 
                else:                         
                        self.pixel=self.Image.load() 
                        self.label.image=ImageTk.PhotoImage(self.Image) 
                        Label.__init__(self.label,self.root,image=self.label.image,bd=0) 
                        self.label.pack() 
                                
        def Save(self,event=None):      
                try: 
                        self.signal.save("final.jpg") 
                except: 
                        tkMessageBox.showerror("오류 !","저장할 이미지가 존재하지 않습니다.")  
                
        def Quit(self,event=None): 
                self.root.destroy()
                
#############draw_graph#############
        def Dg(self,event=None): 
                a = len(self.realsignal)
                ttime = []
                for i in range(a):
                        ttime.append(0+1./5000.*i)                
                plottype = "png"
		xData = np.linspace(0, float(a)/5000., 100)
		yData1 = np.cos(xData)
		yData2 = np.sin(xData)		
		fig = plt.figure()
		subPlot1 = fig.add_subplot('211')
                plt.plot(ttime,self.realsignal,figure=fig)
		subPlot2 = fig.add_subplot('212')
		plt.plot(xData, yData2, figure=fig)
                plt.xlabel('time(s)')
                plt.ylabel('Amplitude')
                plt.title('Gravitational Signal')
                plt.savefig('Gravitational Signal Graph'+plottype)     
		
		retval = showClickPlot()
		if retval['subPlot'] == None:
			print 'No subplot selected'
		else:
			print 'You clicked in subplot at (%(x).3f, %(y).3f)' \
				% retval
		print biglist
		m = len(biglist)
		n = 0.
		o = 0.
		for i in range(3,m-1):
			n+=float(biglist[i+1][0])-float(biglist[i][0])
		for i in range(3,m-2):
			upper = float(1./(float(biglist[i+2][0])-float(biglist[i+1][0]))-1./(float(biglist[i+1][0])-float(biglist[i][0])))
			lower = float((float(biglist[i+2][0])+float(biglist[i+1][0]))/2.-(float(biglist[i+1][0])+float(biglist[i][0]))/2.)
			o+=float(upper)/float(lower)
		self.frequency =(float(m)-1.)/float(n)
		self.differentiate = float(o)/(float(m)-2.)
		print self.frequency
		print self.differentiate
        def Cm(self,event=None):
                chirp_mass = Tk()
                chirp_mass.title("Chirp mass")
		Chirp_mass = clight**3./G*(5./96.*math.pi**(-8./3.)*self.frequency**(-11./3.)*self.differentiate)**(3./5.)/MSol
		ld = Label(chirp_mass, text="Chirp_mass:%f"%Chirp_mass, font=("Courier", 40, "bold italic"))
		ld.grid(row = 0, column = 0)                
		ld.pack()
        def Noise(self,event=None):
                plottype = "png"
                make_psds = 1
                fs = 5000
                if make_psds:
                    # number of sample for the fast fourier transform:
                        NFFT = 4*fs
                        Pxx_H1, freqs = mlab.psd(self.realsignal, Fs = fs, NFFT = NFFT)
                        # We will use interpolations of the ASDs computed above for whitening:
                        psd_H1 = interp1d(freqs, Pxx_H1)             
                make_plots = 1  
                if make_plots:
                        # plot the ASDs, with the template overlaid:
                        f_min = 0.
                        f_max = 2500.
                        plt.figure(figsize=(10,8))
                        plt.loglog(freqs, np.sqrt(Pxx_H1),'g',label='signal')
                        plt.axis([f_min, f_max, 1e-6, 1])
                        plt.grid('on')
                        plt.ylabel('ASD (strain/rtHz)')
                        plt.xlabel('Freq (Hz)')
                        plt.title('ASD graph')
                        plt.savefig('ASDs.'+plottype)                
                plt.show()
                
        def Director(self, event=None):
                director = Tk()
                director.title("director")
                ld = Label(director, text="Made by",font=("Courier", 40, "bold italic"))
                ld.grid(row = 0, column = 0)
                ld.pack()                
                ld2 = Label(director, text="조건우, 나진환, 한주원",font=("Courier", 20))
                ld2.grid(row = 0, column = 1)
                ld2.pack()
                ld3 = Label(director, text="------------------------------------------------------------------------------------------------------")
                ld3.grid(row=0, column = 2)
                ld3.pack()
                ld4 = Label(director,text=" ",font=("Courier", 40))
                ld4.grid(row=0, column = 3)
                ld4.pack()
                ld5 = Label(director, text="Special Thanks to",font=("Courier", 40, "bold italic"))
                ld5.pack()
                ld6 = Label(director, text="강궁원 박사님", font=("Courier", 20))
                ld6.pack()
                ld7 = Label(director,text=" ",font=("Courier", 40))
                ld7.pack()                 
App()