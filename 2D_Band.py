import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
import math
from pandas import Series, DataFrame

#greek letter dictionary
greek={'Alpha':'\u0391','Beta':'\u0392','Gamma':'\u0393','Delta':'\u0394','Epsilon':'\u0395','Zeta':'\u0396','Eta':'\u0397','Theta':'\u0398','Iota':'\u0399',
'Kappa':'\u039A','Lambda':'\u039B','Mu':'\u039C','Nu':'\u039D','Csi':'\u039E','Omicron':'\u039F','Pi':'\u03A0','Rho':'\u03A1','Sigma':'\u03A3','Tau':'\u03A4',
'Upsilon':'\u03A5','Phi':'\u03A6','Chi':'\u03A7','Psi':'\u03A8','Omega':'\u03A9', 'Sigma_1':'\u03A3\u2081'}

#input readout
file=input("Enter filename: \n")
ceck2=True
path=[]
while ceck2==True:
	bp=input("Disclose your path, as last point enter end: \n")
	if bp!='end':
		path.append(bp)
	else:
		ceck2=False

#determination of skiprows and High Simmetry Point  
headers=['#','@']
skiprow=0
header=open(file, 'r')
ceck=True
count=0
HSP=[]
while ceck==True:
	line=header.readline()
	if line[0] in headers:
		skiprow+=1
		if line.startswith('@ XAXIS TICK     '):
			fine=len(line)
			save_el=line[(fine-8):fine-2]
			HSP.append(save_el)
	else:
		header.close()
		ceck=False
for i in HSP:
	num=float(i)
	HSP[count]=num
	count+=1

#data import
Band=pd.read_csv(file,sep="\s+", header=None, engine='python', skiprows=skiprow,skipfooter=1)
no_band=len(Band.columns)-1
print (no_band)
	
#conversion
eV=27.2114

#plot
#Band plot
y_mx=[]
y_mn=[]
dx=Band[0]
for i in range(1,no_band+1):
	dy=Band[i]*eV
	maxy=dy.max()
	miny=dy.min()
	y_mx.append(maxy)
	y_mn.append(miny)
	plt.plot(dx,dy, color='r')

#HSP lines
x_abs=Band[0]
x_max=x_abs.max()
x_min=x_abs.min()
y_max=max(y_mx)
y_min=min(y_mn)
y_band=np.linspace(y_min-3,y_max+3,2)
Hygh_sym_point=[]
for i in HSP:
	x_band=np.ones(2)*i
	plt.plot(x_band,y_band,color='black')
#x axis label creation
for i in path:
	if i in greek:
		g=greek.get(i)
		Hygh_sym_point.append(g)
	else:
		Hygh_sym_point.append(i)

x=np.linspace(x_min,x_max,2)
y=0*x
plt.xticks(HSP,Hygh_sym_point)
plt.ylabel('Energy (eV)')
plt.plot(x,y,color='blue')  
plt.show()

