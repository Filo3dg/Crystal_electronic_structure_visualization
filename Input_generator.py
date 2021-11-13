import math
import numpy as np
import os

#read input file
reference=input("Introduce your input file: \n")
reference=open(reference,'r')
count2=0.0
ceck2=True
while ceck2==True:
	line2=reference.readline()
	fine=len(line2)
	save_el=line2[0:fine]
	if count2==0:
		no_smpg_pt=save_el#Number of sampling point 
	elif count2==1:
		frct_conv=save_el#Number of file produced by the script
	elif count2==2:
		x_start=save_el#Plane start for kx
	elif count2==3:
		x_end=save_el#Plane end for kx
	elif count2==4:
		y_start=save_el#Plane start for ky 
	elif count2==5:
		y_end=save_el#Plane end for ky
	elif count2==6:
		z_start=save_el#Plane start for kz
	elif count2==7:
		z_end=save_el#Plane end for kz
	elif count2==8:
		save_el=line2[0:fine-1]
		prmb=save_el#File name
	elif count2==9:
		st_band=save_el#First band
	elif count2==10:
		end_band=save_el#Last band
	elif count2==11:
		save_el=line2[0:fine-1]
		folder_input=save_el#Folder where you wanna save the PROPERTIES input for the 3D band  
	elif count2==12:
		folder_output=save_el#Folder where you wanna save the input for 3D_Band.py
	else:
		ceck2=False
		reference.close()
	count2+=1


#var definition
conv_mtx=np.array([[-0.5,0.5,0.5],[0.5,-0.5,0.5],[0.5,0.5,-0.5]])#Conversion matrix
frct_conv=float(frct_conv)
x_start=float(x_start)
m=frct_conv*x_start
x_start=m/frct_conv
x_end=float(x_end)
m=frct_conv*x_end
x_end=m/frct_conv
y_start=float(y_start)
n=frct_conv*y_start
y_start=n/frct_conv
y_end=float(y_end)
n=frct_conv*y_end
y_end=n/frct_conv
z_start=float(z_start)
p=frct_conv*z_start
z_start=p/frct_conv
z_end=float(z_end)
p=frct_conv*z_end
z_end=p/frct_conv
no_smpg_pt=int(no_smpg_pt)
no_smpg_pt=str(no_smpg_pt)
st_band=int(st_band)
st_band=str(st_band)
end_band=int(end_band)
end_band=str(end_band)

#creation of directories
os.mkdir(folder_input)
os.mkdir(folder_output)

#conversion function
def conv(x,y,z,prim):
	vector= np.array([x,y,z])
	prim_coor=vector.dot(conv_mtx)
	prim_coor=prim_coor*abs(prim)
	return prim_coor


#Write PROP input band
def write_input(start_pt,end_pt,doc,prim,smp,st,end):
	file=open(doc,'a')
	file.write("BAND")
	file.write("\nTaAs 3D Bande")
	frct_prim=str(abs(int(prim)))
	no_smpg_pt=str(smp)
	parametri="1 "+frct_prim+" "+no_smpg_pt+" "+st+" "+end+" 1 0"
	file.write("\n"+parametri)
	xs=str(int(start_pt[0]))
	ys=str(int(start_pt[1]))
	zs=str(int(start_pt[2]))
	xe=str(int(end_pt[0]))
	ye=str(int(end_pt[1]))
	ze=str(int(end_pt[2]))
	segmento=xs+" "+ys+" "+zs+"   "+xe+" "+ye+" "+ze
	file.write("\n"+segmento)
	file.write("\nEND")
	file.write("\nEND")
	file.close()

#Input creation 
step=1/frct_conv
i=0
count1=0
Input_3D_file_name=folder_output+"/"+prmb+".3D"
Input_3D=open(Input_3D_file_name,'a')
Input_3D.write(str(int(frct_conv)))
Input_3D.write("\n"+no_smpg_pt)
#method for sampling on a ky,kz plane with sampling point along the kz direction
if x_start==x_end:
	x=x_start
	i=y_start
	step=step*y_end
	frct_prim=(1/step)*2
	Input_3D.write("\n"+str(y_start))
	Input_3D.write("\n"+str(y_end))
	Input_3D.write("\n"+str(z_start))
	Input_3D.write("\n"+str(z_end))
	if y_end>0:
		while i<=y_end:
			counter=str(count1)
			file=folder_input+"/"+prmb+counter+".d3"
			output=folder_output+"/"+prmb+counter+".band"
			start=conv(x,i,z_start,frct_prim)
			end=conv(x,i,z_end,frct_prim)
			write_input(start,end,file,frct_prim,no_smpg_pt,st_band,end_band)
			Input_3D.write("\n"+output)
			i+=step
			count1+=1
	elif y_end<0:
		while i>=y_end:
			counter=str(count1)
			file=folder_input+"/"+prmb+counter+".d3"
			output=folder_output+"/"+prmb+counter+".band"
			start=conv(x,i,z_start,frct_prim)
			end=conv(x,i,z_end,frct_prim)
			write_input(start,end,file,frct_prim,no_smpg_pt,st_band,end_band)
			Input_3D.write("\n"+output)
			i+=step
			count1+=1
	elif y_start<0 and y_end>0:
		while i<=0:
			counter=str(count1)
			file=folder_input+"/"+prmb+counter+".d3"
			output=folder_output+"/"+prmb+counter+".band"
			start=conv(x,i,z_start,frct_prim)
			end=conv(x,i,z_end,frct_prim)
			write_input(start,end,file,frct_prim,no_smpg_pt,st_band,end_band)
			Input_3D.write("\n"+output)
			i+=step
			count1+=1
		if i>0:
			while i<=y_end:
				counter=str(count1)
				file=folder_input+"/"+prmb+counter+".d3"
				output=folder_output+"/"+prmb+counter+".band"
				start=conv(x,i,z_start,frct_prim)
				end=conv(x,i,z_end,frct_prim)
				write_input(start,end,file,frct_prim,no_smpg_pt,st_band,end_band)
				Input_3D.write("\n"+output)
				i+=step
				count1+=1


#method for sampling on a kx,kz plane with sampling point along the kz direction
elif y_start==y_end:
	y=y_start
	i=x_start
	seg_lenght=x_end-x_start
	step=step*seg_lenght
	frct_prim=(1/step)*2
	Input_3D.write("\n"+str(x_start))
	Input_3D.write("\n"+str(x_end))
	Input_3D.write("\n"+str(z_start))
	Input_3D.write("\n"+str(z_end))
	if x_end>0:
		while i<=x_end:
			counter=str(count1)
			file=folder_input+"/"+prmb+counter+".d3"
			output=folder_output+"/"+prmb+counter+".band"
			start=conv(i,y,z_start,frct_prim)
			end=conv(i,y,z_end,frct_prim)
			write_input(start,end,file,frct_prim,no_smpg_pt,st_band,end_band)
			Input_3D.write("\n"+output)
			i+=step
			count1+=1
	elif x_end<0:
		while i>=x_end:
			counter=str(count1)
			file=folder_input+"/"+prmb+counter+".d3"
			output=folder_output+"/"+prmb+counter+".band"
			start=conv(i,y,z_start,frct_prim)
			end=conv(i,y,z_end,frct_prim)
			write_input(start,end,file,frct_prim,no_smpg_pt,st_band,end_band)
			Input_3D.write("\n"+output)
			i+=step
			count1+=1
	elif x_start<0 and x_end>0:
		while i<=0:
			counter=str(count1)
			file=folder_input+"/"+prmb+counter+".d3"
			output=folder_output+"/"+prmb+counter+".band"
			start=conv(i,y,z_start,frct_prim)
			end=conv(i,y,z_end,frct_prim)
			write_input(start,end,file,frct_prim,no_smpg_pt,st_band,end_band)
			Input_3D.write("\n"+output)
			i+=step
			count1+=1
		if i>0:
			while i<=x_end:
				counter=str(count1)
				file=folder_input+"/"+prmb+counter+".d3"
				output=folder_output+"/"+prmb+counter+".band"
				start=conv(i,y,z_start,frct_prim)
				end=conv(i,y,z_end,frct_prim)
				write_input(start,end,file,frct_prim,no_smpg_pt,st_band,end_band)
				Input_3D.write("\n"+output)
				i+=step
				count1+=1
			
#method for sampling on a kx,ky plane with sampling point along the ky direction
elif z_start==z_end:
	z=z_start
	i=x_start
	seg_lenght=x_end-x_start
	step=step*seg_lenght
	frct_prim=(1/step)*2
	Input_3D.write("\n"+str(x_start))
	Input_3D.write("\n"+str(x_end))
	Input_3D.write("\n"+str(y_start))
	Input_3D.write("\n"+str(y_end))
	if x_end<0:
		while i<=x_end:
			counter=str(count1)
			file=folder_input+"/"+prmb+counter+".d3"
			output=folder_output+"/"+prmb+counter+".band"
			start=conv(i,y_start,z,frct_prim)
			end=conv(i,y_end,z,frct_prim)
			write_input(start,end,file,frct_prim,no_smpg_pt,st_band,end_band)
			Input_3D.write("\n"+output)
			i+=step
			count1+=1
	elif x_end<0:
		while i>=x_end:
			counter=str(count1)
			file=folder_input+"/"+prmb+counter+".d3"
			output=folder_output+"/"+prmb+counter+".band"
			start=conv(i,y_start,z,frct_prim)
			end=conv(i,y_end,z,frct_prim)
			write_input(start,end,file,frct_prim,no_smpg_pt,st_band,end_band)
			Input_3D.write("\n"+output)
			i+=step
			count1+=1
	elif x_start<0 and x_end>0:
		while i<=0:
			counter=str(count1)
			file=folder_input+"/"+prmb+counter+".d3"
			output=folder_output+"/"+prmb+counter+".band"
			start=conv(i,y_start,z,frct_prim)
			end=conv(i,y_end,z,frct_prim)
			write_input(start,end,file,frct_prim,no_smpg_pt,st_band,end_band)
			Input_3D.write("\n"+output)
			i+=step
			count1+=1
		if i>0:
			while i<=x_end:
				counter=str(count1)
				file=folder_input+"/"+prmb+counter+".d3"
				output=folder_output+"/"+prmb+counter+".band"
				start=conv(i,y_start,z,frct_prim)
				end=conv(i,y_end,z,frct_prim)
				write_input(start,end,file,frct_prim,no_smpg_pt,st_band,end_band)
				Input_3D.write("\n"+output)
				i+=step
				count1+=1

Input_3D.write("\nend")
Input_3D.close()




