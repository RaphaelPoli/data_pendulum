#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

# push r to record 7 seconds and analyse automatically
# push q to quit
Device_adress='/dev/serial/by-id/usb-1a86_USB_Serial-if00-port0'
Device_adress='/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_75830333238351C0D101-if00'

#now truth should be the coef calculated from line equation
#
from sklearn.linear_model import LinearRegression
calculate_lm=True
from scipy.fftpack import fft
import numpy as np #usually there by default
import math
import matplotlib.pyplot as plt



import pyexcel 
from pyexcel_ods import get_data
from pyexcel_ods import save_data
from collections import OrderedDict

import serial

import pygame
from pygame.locals import *
import keyboard

import datetime
import os

from collections import OrderedDict

print ("int",int("0xaa",16))

def hexcolor(string):#does not work on python3
	print ("string",string)
	red_s=string[0:2]
	green_s=string[2:4]
	blue_s=string[4:6]
	print (red_s)
	print (type(red_s))
	red=int(red_s,16)/255.0
	green=int(green_s,16)/255.0
	blue=int(blue_s,16)/255.0
	return (red,green,blue)
	
	
	
# new colors: bg 3d3d45
#             light 808080
#			  shade 2e2e36
# 			  calming yes 365238
#			  calming no  633636

#Calming_yes=(54,82,56)#hexcolor("365238")
#Calming_no=(99,54,54)#hexcolor("633636")
#Background_color=(61,61,69)#hexcolor("3d3d45")
#Truth_color=(128,128,128)#hexcolor("808080")
#intensity_color=(153,69,00)#hexcolor("994500")
#Resistance_color=(46,46,54)#hexcolor("2e2e36")



Calming_yes=(64,92,68)#hexcolor("365238")
Calming_no=(108,64,64)#hexcolor("633636")
Background_color=(61,61,69)#hexcolor("3d3d45")
Truth_color=(255,255,255)#hexcolor("808080")
intensity_color=(153,69,00)#hexcolor("994500")
Resistance_color=(0,0,0)#hexcolor("2e2e36")


##---------------------------------------------used procedures
		

def gon_dot(dot_center,nsides, radius, dot1_angle, direction, i):
	dot1_angle=math.radians(dot1_angle)
	dot=(dot_center[0] + radius * math.cos((dot1_angle+(2 * math.pi * i / float(nsides)*direction))),
		dot_center[1] + radius * math.sin((dot1_angle+(2 * math.pi * i / float(nsides)*direction))))
	return dot

	

def line_equation(a,b):
	same_point=False
	vertical=False
	horizontal=False
	error=False
	line_equation=""
	#print "a:",a," b:",b
	line_a=0
	line_b=0
	xa=a[0]
	ya=a[1]
	xb=b[0]
	yb=b[1]
	if (xa==xb and ya==yb):
		same_point=True
		error=True
		distance_to_line=9999
		return ("same point",0,0)
		#print "meme point"
	if ya==yb:
		horizontal=True
	if xa==xb:
		#print "vertical"
		vertical=True
		
	if not (vertical or horizontal or same_point):
		
		line_a=(yb-ya)/float(xb-xa)
		#print ""
		#print "a de dot ",xa,ya," et ",xb,yb," ",line_a
		line_b=(yb-line_a*xb)
		#print "b de dot ",xa,ya," et ",xb,yb," ",line_b
		#print "equation de la droite ",xa,ya,xb,yb,":",line_a,"x+",line_b
		line_equation="y="+str(line_a)+"x+"+str(line_b)
		if line_a==0:
			#print "line_a =0"
			horizontal==True	
	else:
		if horizontal:
			line_equation="y="+str(ya)
			line_a=0
			line_b=ya
			#print "(",x,y,")-(",xa,ya,")=",distance_to_line,"/","ya",ya,"yb",yb
		if vertical:
			line_equation="x="+str(xa)
			line_a=0
			line_b=0
			
	return [line_equation,line_a,line_b]
	





def biggest_in_list(lis):
	n=0
	m=0
	biggest=0
	write1=0
	write2=0
	write3=0
	count=0
	offset=0
	for item in lis:
		n=n+1
		count=count+1
		if count>len(lis)/3 and write1==0: 
			write1=1
			#print"1/3 done at ", datetime.datetime.strftime(datetime.datetime.now(), "%H:%M")
			#os.system('say "one third reached"') 
			#print "inkmean",inkmean
		if count>2*len(lis)/3 and write2==0: 
			write2=1
			#print"2/3 done at ", datetime.datetime.strftime(datetime.datetime.now(), "%H:%M")
			#os.system('say "two third reached"') 

			#print "inkmean",inkmean
		if count>3*len(lis)/3 and write3==0: 
			write3=1
			#print"3/3 done at ", datetime.datetime.strftime(datetime.datetime.now(), "%H:%M")
			#print "inkmean",inkmean
		if (item>biggest):
			biggest=item
			offset=n-1
	#print"biggest=",biggest
	return[biggest,offset]


def biggest_offsets_list(lis,howmany):#has been improved since "shape and alignement" version
	image=[]
	for item in lis:
		image.append(item)
	offset_list=[]
	#print "lis",lis
	if len(lis)<howmany:
		howmany=len(lis)
	for i in range(howmany):
		find1=biggest_in_list(image)
		#print "find",find1
		#print "offset",find1[1]
		offset_list.append(find1[1])
		image[find1[1]]=0
	return offset_list
	
def count_occurences(number, list_name):
	count=0
	for item in list_name:
		if item==number:
			count=count+1
	return count
	
	
def count_close(number, list_name, percent_close):
	count=0
	for item in list_name:
		if item>number-percent_close*number and item<number+percent_close*number:
			count=count+1
	return count

def mean(list_name):
	return sum(list_name)/float(len(list_name))
	

def plot_fft(integer_data, sample_framerate, sensitivity):
	#print "sensitivity=",sensitivity
#	print "length",len(integer_data)
	how_many_used_bands=0
	def near(item, liste, sensitivity):
		for item2 in liste:
			if math.fabs(item2[0]-item)<sensitivity:
				return True
		return False
	N=len(integer_data)
	T=1.0/float(sample_framerate)
	y2f=[]
	freq_list=[]
	freq_list2=[]
	#print "computing fft"
	yf = fft(integer_data)
	for item in yf:
		y2f.append(np.abs(item)*2.0/float(N))#frequency list
	#here regular spaces are created to sort y2f output
	xf = np.linspace(0.0, 1.0/float(1000.0*T), int(N/8.0))#N/2 is the bandwidth that is to say the maximum detectable frequency
	#with /500*T as interval and n/16 at bandwith, plant observation is fairly precise.
	#with narrower bands (when the second argument is greater) the signal is more segmented, and so band averages are lower.
	#also variations will be more important if there are less bands.
	
	#the input is one resistance value every hundredth of second
	#it does not allow to observe "sleeping time" of the plant (sometimes all values drop to the lowest band for a short or longer period)
	#print "finding peak frequency"
	#print "length of frequency array",len(xf)
	y2f.sort()
	#max_frequency=max(y2f) # better calculation is further
	min_frequency=min(y2f)
	#print "lowest_found", y2f[0]
	#print "peak list", peak
	#print "fft list", y2f
	#print "len of y2f",len(y2f)
	#print "detectable band list", xf
	#print "len of xf", len(xf)
	#print "value of peak",peak[0]
	#print ""
	#print "computing more peaks"#need to remove neighbour frequencies
	band_contain=[]
	band_filled=[]
	i=0
	#distributing frequencies into bands
	for item in range (len(xf)-2):#cycling thru bands
		#print xf[item], xf[item+1]
		#print
		count=0
		i=i+1
		band_filled.append([])
		for item2 in y2f:#cycling frequencies
			if item2>xf[item] and item2<=xf[item+1]:
				count=count +1
				band_filled[i-1].append(item2)#nourishing the list of frequency in each band
		band_contain.append(count)
	
	#print "frequency band contain", band_contain[0:64] #this is the quantity of found frequencies per band
	band=[]
	i=0
	last_i=0
	for item2 in band_filled:#cycling bands
			i=i+1
			if len(item2)>4 and i>last_i:# here is the threshold value for highest band (it must contain more than 4 frequencies)
				last_i=i
				band=item2
	
	#print "len of max band", len(band)
	if len(band)>0:
		max_frequency=max(band)
	else:
		max_frequency=0
	#print "before",y2f[3]
	offset_list= biggest_offsets_list(band_contain,1)#1 is the number of highest freq
	
	selected_band_list=[]
	
	#creating a list of all frequencies in most gifter band
	for item2 in y2f:#cycling frequencies
		if item2>xf[offset_list[0]] and item2<=xf[offset_list[0]+1]:
			selected_band_list.append(item2)
	for item in band_contain:#cycling frequencies
		if item!=0:
			how_many_used_bands=how_many_used_bands+1
	#print "length of frequency list in highest band:",len(selected_band_list)
	if len(selected_band_list)>0:
		mean_frequency=mean(selected_band_list)
	else:
		mean_frequency=0
	#print offset_list[0]
	#how_many=count_occurences(band_contain[offset_list[0]],band_contain)#for less than ten measures per second
	
	# here is the threshold to count closer bands to the highest band (last argument (started with 0.2)(value between 0 and 1)
	how_many_close_bands=count_close(band_contain[offset_list[0]],band_contain,0.1)
	
	result=[mean_frequency,how_many_close_bands, how_many_used_bands,min_frequency,max_frequency]
	#print "offset list",offset_list
	#print "after",y2f[3]
	
	
	# the rest here was used for the synthesiser, but not in the plant observer
	
	for item in offset_list:
		#print "offset",item
		#print "peak", y2f[item]
		if item<len(xf) and not near(xf[item],freq_list,sensitivity):#sensitivity was 8 at first then it's been 21 then 100 and also 1000(Minimum distance from two peaks)
			#                                                sensitivity higher removes vibrato
			#print "offset",item
			#print "peak", y2f[item]
			#print "frequency",xf[item]
			#print ""
			freq_list.append([xf[item],y2f[item]])
	#print "dominant freq list",freq_list
	liste=[]
	for freq in freq_list:
		liste.append(freq[1])
	rooftop=biggest_in_list(liste)[0]
	#print "amplitude list",liste
	#print "rooftop",rooftop
	for freq in range(len(freq_list)):
		freq_list[freq][1]=freq_list[freq][1]*100/float(rooftop)
	#print "avant",freq_list
	for freq in range(len(freq_list)):
		if freq_list[freq][1]>5:#----------------------------here is a percent threshold to detection of a harmonic
			freq_list2.append(freq_list[freq])
		
	#print "apres",freq_list2
	#print "end at",datetime.datetime.strftime(datetime.datetime.now(),"%H:%M")
	#plt.plot(xf, 2.0/float(N) * np.abs(yf[0:N/2]))#N length of sample
	#plt.grid()
	#plt.show()
	return result




def plot_vibrato_fft(integer_data, sample_framerate, sensitivity):
	#print "sensitivity=",sensitivity
#	print "length",len(integer_data)
	how_many_used_bands=0
	def near(item, liste, sensitivity):
		for item2 in liste:
			if math.fabs(item2[0]-item)<sensitivity:
				return True
		return False
	N=len(integer_data)
	T=1.0/float(sample_framerate)
	y2f=[]
	freq_list=[]
	freq_list2=[]
	#print "computing fft"
	yf = fft(integer_data)
	for item in yf:
		y2f.append(np.abs(item)*2.0/float(N))#frequency list
	#here regular spaces are created to sort y2f output
	#print "N/2.0",N/2.0
	xf = np.linspace(0.0, 1.0/float(10*T), int(N/2.0))#N/2 is the bandwidth that is to say the maximum detectable frequency
	#print xf
	#with /500*T as interval and n/16 at bandwith, plant observation is fairly precise.
	#with narrower bands (when the second argument is greater) the signal is more segmented, and so band averages are lower.
	#also variations will be more important if there are less bands.
	
	#the input is one resistance value every hundredth of second
	#it does not allow to observe "sleeping time" of the plant (sometimes all values drop to the lowest band for a short or longer period)
	#print "finding peak frequency"
	#print "length of frequency array",len(xf)
	y2f.sort()
	#max_frequency=max(y2f) # better calculation is further
	min_frequency=min(y2f)
	#print "lowest_found", y2f[0]
	#print "peak list", peak
	#print "vibrato fft list", y2f
	#print "len of y2f",len(y2f)
	#print "detectable band list", xf
	#print "len of xf", len(xf)
	#print "value of peak",peak[0]
	#print ""
	#print "computing more peaks"#need to remove neighbour frequencies
	band_contain=[]
	band_filled=[]
	i=0
	#distributing frequencies into bands
	for item in range (len(xf)-2):#cycling thru bands
		#print "band",xf[item], xf[item+1]
		#print
		count=0
		i=i+1
		band_filled.append([])
		for item2 in y2f:#cycling frequencies
			if item2>xf[item] and item2<=xf[item+1]:
				count=count +1
				band_filled[i-1].append(item2)#nourishing the list of frequency in each band
		band_contain.append(count)
	
	#print "vibrato band contain",band_contain #this is the quantity of found frequencies per band
	band=[]
	i=0
	last_i=0
	for item2 in band_filled:#cycling bands
			i=i+1
			if len(item2)>2 and i>last_i:# here is the threshold value for highest band (it must contain more than 4 frequencies)
				last_i=i
				band=item2
	
	#print "len of max band", len(band)
	if len(band)>0:
		max_frequency=max(band)
	else:
		max_frequency=0
	#print "before",y2f[3]
	offset_list= biggest_offsets_list(band_contain,1)#1 is the number of highest freq
	
	selected_band_list=[]
	
	#creating a list of all frequencies in most gifter band
	if len(y2f)>0 and len(offset_list)>0:
		for item2 in y2f:#cycling frequencies
			if item2>xf[offset_list[0]] and item2<=xf[offset_list[0]+1]:
				selected_band_list.append(item2)
	else:
		selected_band_list= []
	for item in band_contain:#cycling frequencies
		if item!=0:
			how_many_used_bands=how_many_used_bands+1
	#print "length of frequency list in highest band:",len(selected_band_list)
	if len(selected_band_list)>0:
		mean_frequency=mean(selected_band_list)
	else:
		mean_frequency=0
	#print offset_list[0]
	#how_many=count_occurences(band_contain[offset_list[0]],band_contain)#for less than ten measures per second
	
	# here is the threshold to count closer bands to the highest band (last argument (started with 0.2)(value between 0 and 1)
	if len(offset_list)>0:
		how_many_close_bands=count_close(band_contain[offset_list[0]],band_contain,0.1)
	else:
		how_many_close_bands=0
	result=[mean_frequency,how_many_close_bands, how_many_used_bands,min_frequency,max_frequency]
	#print "offset list",offset_list
	#print "after",y2f[3]
	
	
	# the rest here was used for the synthesiser, but not in the plant observer
	
	for item in offset_list:
		#print "offset",item
		#print "peak", y2f[item]
		if item<len(xf) and not near(xf[item],freq_list,sensitivity):#sensitivity was 8 at first then it's been 21 then 100 and also 1000(Minimum distance from two peaks)
			#                                                sensitivity higher removes vibrato
			#print "offset",item
			#print "peak", y2f[item]
			#print "frequency",xf[item]
			#print ""
			freq_list.append([xf[item],y2f[item]])
	#print "dominant freq list",freq_list
	liste=[]
	for freq in freq_list:
		liste.append(freq[1])
	rooftop=biggest_in_list(liste)[0]
	#print "amplitude list",liste
	#print "rooftop",rooftop
	for freq in range(len(freq_list)):
		freq_list[freq][1]=freq_list[freq][1]*100/float(rooftop)
	#print "avant",freq_list
	for freq in range(len(freq_list)):
		if freq_list[freq][1]>5:#----------------------------here is a percent threshold to detection of a harmonic
			freq_list2.append(freq_list[freq])
		
	#print "apres",freq_list2
	#print "end at",datetime.datetime.strftime(datetime.datetime.now(),"%H:%M")
	#plt.plot(xf, 2.0/float(N) * np.abs(yf[0:N/2]))#N length of sample
	#plt.grid()
	#plt.show()
	return result


def mean(list_name):
	if len(list_name)>0:
		return sum(list_name)/float(len(list_name))
	else:
		return 0
	
def blind_add_row(row):
	
	global output_file
#	print "adding row"
	book = pyexcel.get_book(file_name=output_file)#loads a sheet in a sheet object that can be modified
	book.Sheet1.row+= row
	book.save_as(output_file)
	
	


def extract_digit(value, label_required, exclusion_strings):
	
	#takes a string of byte characters
	#checks if the label is contained in the value
	#extracts digits on the right of the ":" sign
	#checks if in right part some strings are found or not that could cancel the result
	#returns an int
	s=b"NA"
	v=b"NA"
	s2=b"NA"
	v2=b"NA"
	no_exclusion_string=True
	
	def only_digit(string):
		chiffres=b"0123456789."
		new_fil=b""
		
		#print ("string",string)
		for char in string:
			#print ("char",bytes([char]))
			if bytes([char]) in chiffres:
				
				new_fil=new_fil+bytes([char])
		return new_fil

	def no_exclusion_string(string, exclusion_strings):
		for st in exclusion_strings:
			if st in string:
				return False
		return True
			



	if value!=b"" or value !=b"\n":
		if label_required in value:
			if b":" in value:
				v=value.split(b":")[1]
				#print ("v split:",v)
				v_int=only_digit(v)
				#print ("v_int:",v_int)
			else:
				v_int=b"0"
			if v_int!=b'' and no_exclusion_string(v_int,exclusion_strings):
				#print ("v no exlu:",v_int)
				if b"." in v_int:
					vs=v_int.split(b".")[0]#removing digits after the point
					if vs==b"":
						v2=0
					else:
						v2=int(vs)
				else:
					v2=int(v_int)
				#print ("v2:",v2)
				return v2


def blind_add_row(row):
	
	global output_file
#	print "adding row"
	book = pyexcel.get_book(file_name=output_file)#loads a sheet in a sheet object that can be modified
	book.Sheet1.row+= row
	book.save_as(output_file)
	recorder=False
	
	
	
def xls_add_row(fil, row):
	
#	print "adding row"
	book = pyexcel.get_book(file_name=fil)#loads a sheet in a sheet object that can be modified
	book.Sheet1.row+= row
	book.save_as(fil)
	recorder=False
	
	
	
def increment(fil):
	chiffres=u"0123456789"
#pour lire le numéro de fichier
#j'enlève les lettres et les soulignés, et je lis les deux derniers caractères avant le point
#ou je ne garde que les chiffres trouvés
#s'il n'y a pas de chiffre l'ajout est "02"
	fil=fil.split(".")[0]
	new_fil=""
	for char in fil:
		if char in chiffres:
			new_fil=new_fil+char
	#print "last digit",new_fil[len(new_fil)-2:len(new_fil)]
	result=u""+str(int(new_fil[len(new_fil)-2:len(new_fil)])+1).zfill(2)
	#print result
	return result



def only_digit(string):
	chiffres=b"0123456789."
	new_fil=b""
	
	#print ("string",string)
	for char in string:
		#print ("char",bytes([char]))
		if bytes([char]) in chiffres:
			
			new_fil=new_fil+bytes([char])
	return new_fil
	
	
	

pygame.init()

available = pygame.font.get_fonts()
print (available)

ennd=False

#----------------------------------------------------------------program loop

while not ennd:
	long_term_rec=True
	name=u'pendulum_01.xls'
	path="./"
	list_of_files=[]
	for r,d,f in os.walk(path):#r root, d directory, f file
		for file in f:
			list_of_files.append(file)
	
	new_name=name
	output_file=name
	
	#iterating thru given name plus end numbers until new name is found
	while new_name in list_of_files:
		#output_file ="ohm_input20_02.xls"
		#print new_name, "found in working directory adding increment to name"
		spl=new_name.split(".")[0]#removing extension
		output_file=spl[0:len(spl)-3]+"_"+increment(new_name)+".xls"#replacing number and re adding extention
		#print "elaborating name", output_file
		new_name=output_file
	print ()
	print ("creating", output_file)
	data_book = {'Sheet1':[]}
	
	
	#creating empty book (carefull: replacing!)# like in gematries
	other_book = pyexcel.Book(data_book)
	other_book.save_as(output_file)
	pendulum_xls=output_file
	# adding column titles for vibration file
	row=[				"datetime",
						"ohm_mean",
						"mean_freq",
						"coef_inter",
						"4min truth mean",
						"motion",
						"ambitus",
						"wide motion",
						"wide ambitus",
						"lm of ambitus",
						"lm_of_freq",
						"amplitude",
						"used_bands",
						"min_freq", 
						"max_freq", 
						"vibrato_freq",
						"vibrato_blur"
						]
	vibration_xls="vibration.xls"
	if vibration_xls in list_of_files:
		pass
	else:
		if long_term_rec:
			
			#creating empty book (carefull: replacing!)# like in gematries
			other_book = pyexcel.Book(data_book)
			other_book.save_as(vibration_xls)
			xls_add_row(vibration_xls, row)
			
			
			

	# adding column titles for pendulum file
	row=[				"datetime",
						"ohm_mean",
						"mean_freq","len of sample","coef_inter",
						"motion",
						"ambitus",
						"wide motion",
						"wide ambitus",
						"lm_of_freq",
						"amplitude",
						"used_bands",
						"min_freq", 
						"max_freq", 
						"vibrato_freq",
						"vibrato_blur"
						]
	xls_add_row(output_file, row)
			
		
		
	#works with an ino code uploaded into the arduino
	#ser = serial.Serial('/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_757303031393519130E1-if00', bytesize=8,baudrate=9600, xonxoff=True, timeout=2)#other arduino (attacked)
	ser = serial.Serial(Device_adress, bytesize=8,baudrate=9600, xonxoff=True, timeout=2)
	#print format(ser)
	count=0
	wait=0
	data=[]
	current_data=[]
	wide_motion_data=[]
	ambitus_data=[]
	freq_data=[]
	list_calm_data=[]
	lowres=False
	hires=True
	time_place=datetime.datetime.now()
	time_place2=datetime.datetime.now()
	lenfreq=0
	len_collec=0
	len_collec_w_amb=0
	countcalm=0
	blurry_count=0
	multiplier=10000.0
	band_width_data=[]
	min_freq_data=[]
	max_freq_data=[]
	color_mean=(0,0,0)
	mean_motion_5=0
	mean_display_deg_3=0
	ambitus_display_deg_3=0
	wide_mean_dspl=0
	wide_ambitus_dspl=0
	ambitus=0
	coef_amb_lm=0
	running_coefs=[]
	wide_coef_data=[]
	wide_coef_dspl=0
	coef_dspl=0
	coef_inter=0
	inter_coef_dspl=0
	low_ins_hi=[]
	list_gradient=[]
	dspl_gradient=[]
	
	coef_inter_10min_collec=[]
	wide_ambitus_dspl_10min=[]

	inter_color=(0,0,0)
	color=(255,255,255)
	color_wdamb=(0,0,0)
	counter = 0
	start=0
	t=0

	counter_2=0
	start_2=0
	t_2=0
	recorder=False

	
	exti=False
	counting=False
	mean_collection=[]
	colrow1=[]
	colrow2=[]
	collec=[]
	colrow_amb=[]
	x_list=[]
	pendulum_lever=5
	mean_freq=0
	hires_in_lowres=True
	hi_in_low_params=[500,14,100]#milliseconds (100-1000), number of recordings (64-7), length of sample (5-100)
	screen = pygame.display.set_mode((400,270))

	# attention le modèle linéaire a plus d'inertie que la courbe affichée
	# j'ai essayé de baisser le pendulum lever en dessous de 5 mais je ressens plus de justesse à ce chiffre
	#-------------------------------------------------------------------------------------------------------------------------
	#-------------------------------------------------------------------------------------------------------------------------
	center_vu=(100,200)
	center_vu2=(300,200)
	freq_display_deg_3=0
	data_motion=[]
	while not exti:	
		
		
		


		motion=0
		value= ser.readline()
		#print("value:",value)
		s=b"NA"
		v=b"NA"
		s2=b"NA"
		v2=b"NA"
		coef_linear_model="NA"
		
		
		if keyboard.is_pressed('r') and len(colrow1)>=pendulum_lever:
			print ('r is pressed')
			count=0
			counting=True
			
			
		if keyboard.is_pressed('q') and len(colrow1)>=pendulum_lever:
			print ('q is pressed')
			ennd=True
			exti=True
		
		#--------------------------------------------reading the value extracted from serial and getting an int
		
		digit=extract_digit(value, b"Sensor", [b"NA", b"in"])
		if digit != None:
			data.append(digit)			
		#here can be added readings on other analog input
					
			
		if len(data)<108:
			pass
			print ("len",len(data))
			print ("v2",v2)
		if len(data)>108: #minimum sample to get a frequency (first used 500)
		
			data.pop(0)# keep buffer of (that number of) values
			freq=plot_fft(data, 100.0, 0.01)
			freq_data.append(freq[0]*multiplier)
			display_freq=freq[0]*multiplier
			max_freq=1000
			freq_display_deg=180*display_freq/float(max_freq)
			

	
			
			
			min_freq_data.append(freq[3])
			max_freq_data.append(freq[4])
			band_width_data.append(int(freq[2]))
			if int(freq[0]*multiplier)<(multiplier/1000.0)*2:#calm threshold
				countcalm=countcalm+1
			else:
				list_calm_data.append(countcalm)
				countcalm=0
			if freq[1]>2:
				#print "blurry"
				blurry_count=blurry_count+1
				mult=int(freq[0]*multiplier)
				if b"." in s:
					s2=int(s.split(b".")[0])
				row=[datetime.datetime.now(),s2,mult,"blurry"]
			if freq[1]==1:
				mult=int(freq[0]*multiplier)
				if b"." in s:
					s2=int(s.split(b".")[0])
				row=[datetime.datetime.now(),s2,mult,"clear"]
		
			if hires_in_lowres:
				switch=hi_in_low_params[0]
			else:
				switch=1000
			low_ins_hi.append(freq_data[len(freq_data)-1])
			if len(low_ins_hi)>hi_in_low_params[2]:
				low_ins_hi.pop(0)
			if hires:
				d=math.fabs(float(datetime.datetime.strftime(datetime.datetime.now(),"%S.%f"))*1000-float(datetime.datetime.strftime(time_place, "%S.%f"))*1000)
				#print ("d:",d)
				if d>switch:#when the number of seconds is attained (hires is lower number of seconds)
					if counting:
						count+=1
						print ("counting",count)
					#recording calm moment count
					if len(list_calm_data)>0:
						maxcalm=max(list_calm_data)
						list_calm_data=[]
						countcalm=0
					else:
						if countcalm>0:
							maxcalm=countcalm
							countcalm=0
						else:
							countcalm=0
							maxcalm=0
					list_calm_data=[]
					vibrato=plot_vibrato_fft(freq_data, 500/10.0, 0.01)
					print (datetime.datetime.now())
					print()
					#print ("vibrato dominant freq:",vibrato[0])
					if float(vibrato[2])!=0:
					#	print ("vibrato blur percent:",vibrato[1],"/",float(vibrato[2])," %:",vibrato[1]/float(vibrato[2])*100.0)
						vibrato_blur=vibrato[1]/float(vibrato[2])*100.0
					else:
						vibrato_blur=100.0
					#print ("vibrato ambitus:",vibrato[3],vibrato[4])
					print()
					#adding means straight away
					if len(data)>0: 
						print ("moyenne hom",mean(data))
						#print(max(data))
						#print(min(data))
						amplitude=(max(data)-min(data))
						#adding mean freq to mean collection
						mean_collection.append(mean(data))#the values used for the lm are lowres
						colrow1.append(mean_collection)
						mean_collection=[]
					
					if len(colrow1)>pendulum_lever:
						#print ("to remove",len(colrow1)-pendulum_lever)
						for i in range(len(colrow1)-pendulum_lever):
							colrow1.pop(0)
					else:
						pass
					#	print ("still",pendulum_lever-len(colrow1)," values to get lm")
					#	print ("calculate lm is",calculate_lm)
				
					
					#linear regression of freq calculation
					
					if len(colrow1)>=pendulum_lever:#calculating lm only after 155 values stored
						colrow2=[]
						for i in range(len(colrow1)):
								x_list.append(i)
								colrow2.append(x_list)
								x_list=[]
							
						
						mean_collection_array=np.array(colrow1)
						x_list_array=np.array(colrow2)
						coef_linear_model="NA"
						coef_lm_of_lm="NA"
						if calculate_lm :
							model=LinearRegression()
							model.fit(mean_collection_array,x_list_array)
							if len(colrow1)>=pendulum_lever:#calculating lm only after 155 values stored
								coef_linear_model= model.coef_[0][0]
							#	print (len(mean_collection_array),"values linear model coef:",coef_linear_model)
									
						
					print ("current mean frequency",mean(freq_data))
					
					
					#calculating motion of freq
					last_mean_freq=mean_freq
					mean_freq=mean(freq_data)
					motion= -(last_mean_freq-mean_freq)
					
					data_motion.append(motion)
					if len(data_motion)>5:
						data_motion.pop(0)
					
					
					#calculating ambitus and its linear model
					
					if len(data_motion)==5:
						#print ("five last motion mean", mean(data_motion))
						mean_motion_5=mean(data_motion)
						wide_motion_data.append(mean_motion_5)
						ambitus=max(data_motion)-min(data_motion)
						ambitus_data.append(ambitus)
						#print ("remaining for starting wide ambitus",len(ambitus_data))
						#print ("remaining for wide ambitus", 6-len(colrow_amb))
						if len(ambitus_data)>5:
							collec.append(mean(ambitus_data))
							colrow_amb.append(collec)
							if len(colrow_amb)>5:
								colrow_amb.pop(0)
							collec=[]
							colrow2=[]
							x_list=[]
							for i in range(len(colrow_amb)):
								x_list.append(i)
								colrow2.append(x_list)
								x_list=[]
								
							
							if calculate_lm and len(colrow_amb)>4:
								mean_collection_array=np.array(colrow_amb)
								x_list_array=np.array(colrow2)
								model=LinearRegression()
								model.fit(mean_collection_array,x_list_array)
								if len(colrow_amb)>=5:#calculating lm only after 155 values stored
									coef_amb_lm= model.coef_[0][0]
								#	print (len(mean_collection_array),"wide ambitus linear model coef:",coef_amb_lm)
							
						if len(ambitus_data)>216:
							ambitus_data.pop(0)
						if len(wide_motion_data)>216:
							wide_motion_data.pop(0)
						
						wide_ambitus_dspl=math.fabs(180*coef_amb_lm/float(10))
						wide_ambitus_dspl_10min.append(wide_ambitus_dspl)
						
						
						if coef_amb_lm<0:
							color_wdamb=Calming_yes
						if coef_amb_lm>0:
							color_wdamb=Calming_no
						if coef_amb_lm==0:
							color_wdamb=(0,0,0)
						
						#print ("ambitus",ambitus)
					
						ambitus_display_deg_3=math.fabs(180*ambitus/float(700))
					
					
					
					#print ("motion:",motion)
					#print ("current mean bandwidth",mean(band_width_data))
					print ("-----------------------------------------------")
					# calculating coef of current line
					
					#print ("lowinshi:", len(low_ins_hi))
					if len(freq_data)>5:#5 is the length on witch the ambitus will be used for line coefs. This feature may be a bad idea
						#this value of 5 defines a good extract that will have a meaning
						echantillon=freq_data[len(freq_data)-5:len(freq_data)]
						#print ("len de echantillon",len (echantillon))	
						ech_ambitus=max(echantillon)-min(echantillon)
						lx=[]
						for dot in range(len(echantillon)):
							#print (int(plott2[dot]))
							if len(echantillon)!=1:
								lx.append((dot+1*ech_ambitus)/(len(echantillon)-1))
							else:
								lx.append(1)

						coefs_lines=[]
						i=0
						for dot in range(len(echantillon)):

							if dot>0:
								running_coefs.append(line_equation((lx[dot-1],echantillon[dot-1]),(lx[dot],echantillon[dot]))[1])
							
						#print ("coefs",coefs_lines)
						current_coef=running_coefs[len(running_coefs)-1]
						print ("current coef",current_coef)
						wide_coef_data.append(current_coef)
						if len(wide_coef_data)>500:
							wide_coef_data.pop(0)
						
						ech_coef_inter=[]
						if len(wide_coef_data)>12:
							ech_coef_inter=wide_coef_data[len(wide_coef_data)-12:len(wide_coef_data)]
						print("len wide coef:",len(wide_coef_data))
						coef_inter=mean(ech_coef_inter)
						print("coef inter:", coef_inter)
						coef_inter_10min_collec.append(coef_inter)
						if len(coef_inter_10min_collec)>50:
							coef_inter_10min_collec.pop(0)
							
						inter_coef_dspl=180*coef_inter/float(555)
						if inter_coef_dspl>0:
							inter_color=Truth_color#true
						if inter_coef_dspl<0:
							inter_color=Resistance_color#false
							inter_coef_dspl=-inter_coef_dspl
						if inter_coef_dspl==0:
							inter_color=(0,0,0)
						
						motion2=0
						if current_coef>0:
							color=Truth_color
							motion2=math.fabs(current_coef)
						if current_coef<0:
							color=Resistance_color
							motion2=math.fabs(current_coef)
						if current_coef==0:
							motion2=0
							color=Background_color
						if motion2<500:
							coef_dspl=math.fabs(180*motion2/float(500))
						else:
							coef_dspl=180
						wide_coef_dspl=180*mean(wide_coef_data)/float(111)
					
						
						list_gradient=[]
						dspl_gradient=[]
						for i in range (len(wide_coef_data)):
							origin_value=float(1*mean(wide_coef_data[len(wide_coef_data)-i:len(wide_coef_data)])/float(444))
							if origin_value>0:
								#list_gradient.append(math.log10(0.00001+origin_value)*66)
								list_gradient.append(origin_value*22)
							if origin_value<0:
								#list_gradient.append(-math.log10(0.00001+math.fabs(origin_value))*66)
								list_gradient.append(origin_value*22)
							
						
						if len(list_gradient)>1:
							for j in range (int(len(list_gradient)/1.0)):
								dspl_gradient.append(mean(list_gradient[j:j+1]))
						
						
						if wide_coef_dspl>0:
							color_mean=(0,255,0)	
						if wide_coef_dspl<0:
							color_mean=(255,0,0)	
							wide_coef_dspl=-wide_coef_dspl
						if wide_coef_dspl==0:
							color_mean=(0,0,0)
					
					if counting:
						
						if hires_in_lowres:
							row=[datetime.datetime.now(),mean(data),mean(low_ins_hi),len(low_ins_hi),coef_inter, motion,ambitus,mean(wide_motion_data),mean(ambitus_data),coef_linear_model,amplitude, mean(band_width_data),mean(min_freq_data), mean(max_freq_data),vibrato[0], vibrato_blur]
						else:
							row=[datetime.datetime.now(),mean(data),mean(freq_data),len(freq_data),coef_inter, motion,ambitus,mean(wide_motion_data),mean(ambitus_data),coef_linear_model,amplitude, mean(band_width_data),mean(min_freq_data), mean(max_freq_data),vibrato[0], vibrato_blur]
						print("recording row:"), row
						
						print("recording row:"), row
						xls_add_row(pendulum_xls, row)
					else:
						if long_term_rec:
							d2=int(datetime.datetime.strftime(datetime.datetime.now(),"%s"))-int(datetime.datetime.strftime(time_place2, "%s"))
							print (d2)
							if d2>60:#when the number of seconds is attained (lowres is a higher number of seconds)
								# data is always of len 108 it contains ohm measurements
								# freq data 
							
								row=[	datetime.datetime.now(),
										mean(data),
										mean(freq_data),
										coef_inter,
										mean(coef_inter_10min_collec), #this value shows global positivity of the time delay
										motion,
										ambitus,
										mean(wide_motion_data),
										mean(ambitus_data),
										mean(wide_ambitus_dspl_10min), #when this goes up there can be anger or circle thought if down calmness and dreamyness (a moving average can be necessary to see the clear variation
										coef_linear_model,# this seems quite talkative regarding the level of light it is the lm of freq
										amplitude, #amplitude of resistance variation if it goes down it can maybe indicate tireness
										mean(band_width_data),
										mean(min_freq_data), 
										mean(max_freq_data),
										vibrato[0], 
										vibrato_blur
									]
								xls_add_row(vibration_xls, row)
								coef_inter_10min_collec=coef_inter_10min_collec[len_collec:len(coef_inter_10min_collec)]
								len_collec=len(coef_inter_10min_collec)
								wide_ambitus_dspl_10min=wide_ambitus_dspl_10min[len_collec_w_amb:len(wide_ambitus_dspl_10min)]
								len_collec_w_amb=len(wide_ambitus_dspl_10min)
								time_place2=datetime.datetime.now()
					
					
					
					blurry_count=0		
					time_place=datetime.datetime.now()
					freq_data=freq_data[lenfreq:len(freq_data)]
					lenfreq=len(freq_data)
					band_width_data=[]#emptying everytime the mean is recorded
					min_max_freq_datamin_max_freq_data=[]
					
			if lowres:
				d3=int(datetime.datetime.strftime(datetime.datetime.now(),"%s"))-int(datetime.datetime.strftime(time_place, "%s"))
				if d3>10:#when the number of seconds is attained (lowres is a higher number of seconds)
					
					#recording calm moment count
					#calm moments recording were removed in ordered to be based on other data
			
					vibrato=plot_vibrato_fft(freq_data, 500/10.0, 0.01)
					print (datetime.datetime.now())
					print()
					print ("vibrato dominant freq:",vibrato[0])
					if float(vibrato[2])!=0:
						print ("vibrato blur percent:",vibrato[1],"/",float(vibrato[2])," %:",vibrato[1]/float(vibrato[2])*100.0)
						vibrato_blur=vibrato[1]/float(vibrato[2])*100.0
					else:
						vibrato_blur=100.0
					print ("vibrato ambitus:",vibrato[3],vibrato[4])
					print()
					#adding means straight away
					amplitude=(max(data)-min(data))
					print ("current mean frequency",mean(freq_data))
					print ("current mean bandwidth",mean(band_width_data))
					print ("----------------------------------------------")

					row=[			datetime.datetime.now(),
									mean(data),
									mean(freq_data),
									coef_linear_model,
									amplitude, 
									maxcalm, 
									blurry_count,
									mean(band_width_data),
									mean(min_freq_data), 
									mean(max_freq_data),
									vibrato[0], 
									vibrato_blur
						]
					blurry_count=0
					blind_add_row(row)
					time_place=datetime.datetime.now()
					#keeping only tail of freq data
					freq_data=freq_data[lenfreq:len(freq_data)]
					lenfreq=len(freq_data)
					band_width_data=[]#emptying everytime the mean is recorded
					min_max_freq_datamin_max_freq_data=[]
					
		

			screen.fill(Background_color)
			font = pygame.font.SysFont("liberationsans", 12)
			truth = font.render("Now Truth", True, (255, 255, 0))
			intensity=font.render("Now Intensity", True, (255, 255, 0))
			intruth=font.render("Intelligible Truth", True, (255, 255, 0))
			#last_18_min=font.render("Last 4 min truth", True, (255, 255, 0))
			calming=font.render("Moment is calming", True, (255, 255, 0))


	
			x=210-180/2.0
			
			#print ("len gradient:",len(list_gradient))
			
			#draw.circle(screen, (255,255,255), center_vu, 72, 1)
			#draw.circle(screen, (255,255,255), center_vu2, 72, 1)
			screen.blit(truth,(x-5 - truth.get_width(), 30-5 - truth.get_height() // 2))
			screen.blit(intruth,(x-5 - intruth.get_width(), 65-15 - intensity.get_height() // 2))
			#screen.blit(last_18_min,(x-5 - last_18_min.get_width(), 90-10 - last_18_min.get_height() // 2))
			
			screen.blit(intensity,(x-5 - intensity.get_width(), 120-10 - intensity.get_height() // 2))
			screen.blit(calming,(x-5 - calming.get_width(), 150-10 - calming.get_height() // 2))

			#print ("motion_deg", freq_display_deg_3)
			#draw.line(screen,color, center_vu2, gon_dot(center_vu2,12,72*9/10.0,180+freq_display_deg_3,1,0), 1)
			pygame.draw.line(screen,color, (x-2,30-5), (x+coef_dspl,30-5),10)
			pygame.draw.line(screen,inter_color, (x-2,65-15), (x+inter_coef_dspl,65-15),30)
			#pygame.draw.line(screen,color_mean, (x-2,90-10), (x+wide_coef_dspl,90-10),20)
			
			pygame.draw.line(screen,intensity_color, (x-2,120-10), (x+ambitus_display_deg_3,120-10),20)
			pygame.draw.line(screen,color_wdamb, (x-2,150-10), (x+wide_ambitus_dspl, 150-10),20)
			
			
			yvu=260#low end
			xvu=200#center
			
			width=5#column width widest 10
			l_max=40#how many to view lowest 20
			
			
			if len(dspl_gradient)<l_max:
				l=len(dspl_gradient)
			else:
				l=l_max
			for k in range(l):
				if dspl_gradient[k]>0:
					pygame.draw.line(screen,Truth_color, (xvu-(width*(l_max/2.0))+(k*width),yvu), (xvu-(width*(l_max/2.0))+(k*width),yvu-dspl_gradient[k]),width)
				if dspl_gradient[k]<0:
					pygame.draw.line(screen,Resistance_color, (xvu-(width*(l_max/2.0))+(k*width),yvu), (xvu-(width*(l_max/2.0))+(k*width),yvu+dspl_gradient[k]),width)
			#draw.line(screen,(255,255,255), center_vu, gon_dot(center_vu,12,72/3.0,180+freq_display_deg,1,0), 1)
			freq_display_deg_2=180*mean_freq/float(max_freq)
			#draw.line(screen,(0,255,255), center_vu, gon_dot(center_vu,12,50*9/10.0,180+freq_display_deg_2,1,0), 1)
			pygame.display.flip()

		if hires_in_lowres:
			max_count=hi_in_low_params[1]
		else:
			max_count=7

		if count>=max_count:
				exti=True
				
				#----------------------------------------this is a copy paste of a data display program---------------------------------------------------------------


	print ("now reading plot")

	
	def mean(list_name):
		if len(list_name)==0:
			return 0
		else:
			return sum(list_name)/float(len(list_name))
		

	def get_most_recent_file_name(path, filetype, element_of_name):
		list_of_files=[]
		directory=""
		fil=""
		for r,d,f in os.walk(path):#r root, d directory, f file
			for directory in d:
				pass
				#print ("dir",directory)
			for fil in f:
				#print ("file",fil)
				if fil.endswith("."+filetype) and element_of_name in fil:
					list_of_files.append(os.path.join(r,fil))
		# * means all if need specific format then *.csv
		if len(list_of_files)>0:
			latest_file = max(list_of_files, key=os.path.getctime)
			return latest_file
		else:
			return None
			

	def running_mean(x,N):
		cumsum=numpy.cumsum(numpy.insert(x,0,0))
		return (cumsum[N:] - cumsum[:-N]) / float(N)
		



	#-------------------------------opening filename
		
	Path_dat="./"
	filename=get_most_recent_file_name(Path_dat,"xls", "pendulum")
	#filename="oxygen_input_76_18_nov.xls"

	print (filename)
	sheet = get_data(filename)["Sheet1"]
	#print (sheet[1][1])#row, column
	plott=[]
	plott2= []





	#----------------------------------------defining viewed range
	time_st="11:30"
	time_sp="12:30"



	timehour_st=int(time_st.split(":")[0])
	timeminute_st=int(time_st.split(":")[1])

	timehour_sp=int(time_sp.split(":")[0])
	timeminute_sp=int(time_sp.split(":")[1])



	now=datetime.datetime.now()
	dateday=int(datetime.datetime.strftime(datetime.datetime.now(),"%d"))
	datemonth=int(datetime.datetime.strftime(datetime.datetime.now(),"%m"))
	dateyear=int(datetime.datetime.strftime(datetime.datetime.now(),"%Y"))


	print ("today",dateday, datemonth, dateyear)


	starttime=datetime.datetime(dateyear,datemonth,dateday,timehour_st,timeminute_st,00)
	stoptime=datetime.datetime(dateyear,datemonth,dateday,timehour_sp,timeminute_sp,00)


	#print ("starttime",starttime)

	#attention à minuit il y a un moment où l'heure n'est pas rajoutée à la suite de la date



	#---------------------------------------------preparing data part


	#creating data list for plotting lm of lm

	for row in sheet:
		date_r_day=int(datetime.datetime.strftime(datetime.datetime.now(),"%d"))
		date_r_month=int(datetime.datetime.strftime(datetime.datetime.now(),"%m"))
		date_r_year=int(datetime.datetime.strftime(datetime.datetime.now(),"%Y"))
		date_r_hour=int(datetime.datetime.strftime(datetime.datetime.now(),"%H"))
		date_r_minute=int(datetime.datetime.strftime(datetime.datetime.now(),"%M"))
		date_r_second=int(datetime.datetime.strftime(datetime.datetime.now(),"%S"))
		#print ("date read",date_r_day, date_r_month, date_r_year, date_r_hour, date_r_minute, date_r_second)
	 
		if row[0]!="NA" and row[0]!="datetime":
			#print (row[0])
			if type(row[0])!=str:
				#print(row[0])
				if (row[0]>starttime and row[0]<stoptime) or True:#condition canceled
					if row[2]!="NA" and row[2]!="mean_freq":
						plott.append(row[2])




	for row in sheet:
		#print (row[0])
		if type(row[0])!=str:
			if row[0]>starttime and row[0]<stoptime or True:#condition canceled
				if row[2]!="NA" and row[2]!="mean_freq":
					if row[0]!="NA" and row[0]!="datetime":
						plott2.append(row[0])
						
							
	lm_of_freq=[]
	plott4= []			

					

	for row in sheet:
		date_r_day=int(datetime.datetime.strftime(datetime.datetime.now(),"%d"))
		date_r_month=int(datetime.datetime.strftime(datetime.datetime.now(),"%m"))
		date_r_year=int(datetime.datetime.strftime(datetime.datetime.now(),"%Y"))
		date_r_hour=int(datetime.datetime.strftime(datetime.datetime.now(),"%H"))
		date_r_minute=int(datetime.datetime.strftime(datetime.datetime.now(),"%M"))
		date_r_second=int(datetime.datetime.strftime(datetime.datetime.now(),"%S"))
		#print ("date read",date_r_day, date_r_month, date_r_year, date_r_hour, date_r_minute, date_r_second)
	 
		if row[0]!="NA" and row[0]!="datetime":
			#print (row[0])
			if type(row[0])!=str:
				#print(row[0])
				if (row[0]>starttime and row[0]<stoptime) or True:#condition canceled
					if row[3]!="NA" and row[3]!="lm_of_freq":
						lm_of_freq.append(row[3])


	for row in sheet:
		#print (row[0])
		if type(row[0])!=str:
			if row[0]>starttime and row[0]<stoptime or True:#condition canceled
				if row[3]!="NA" and row[3]!="lm_of_freq":
					if row[0]!="NA" and row[0]!="datetime":
						plott4.append(row[0])





	lx=[]
	if len(plott)>0:
		ambitus = max(plott)-min(plott)
	else:
		ambitus=1


	for dot in range(len(plott)):
		#print (int(plott2[dot]))
		if len(plott)!=1:
			lx.append((dot+1*ambitus)/(len(plott)-1))
		else:
			lx.append(1)

	coefs_lines=[]
	i=0
	for dot in range(len(plott)):

		if dot>0:
			coefs_lines.append(line_equation((lx[dot-1],plott[dot-1]),(lx[dot],plott[dot]))[1])
		
	print ("coefs",coefs_lines)


	positive_cf=[]
	negative_cf=[]
	for item in coefs_lines:
		if item>0:
			positive_cf.append(item)
		else:
			negative_cf.append(item)

	print("-----------------------------------------------")

	general_mean=mean(coefs_lines)

	print ("general mean", general_mean)
	print ("positive cf mean", mean(positive_cf))
	print ("negative cf mean", mean(negative_cf))
	len_positive=len(positive_cf)
	len_negative=len(negative_cf)
	print ("len positive",len(positive_cf))
	print ("len negative",len(negative_cf))
	print ()
	if len(positive_cf)>0:
		print ("positive cf maximum", max(positive_cf))
	if len(negative_cf)>0:
		print ("negative cf maximum", min(negative_cf))
	print()

	no_intensity=0
	yes_intensity=0


	if len(negative_cf)>0 and len(positive_cf)>0 and float(min(negative_cf))!=0:
		yes_intensity=max(positive_cf)/ float(math.fabs(min(negative_cf)))
	else:
		if len(positive_cf)>0:
			yes_intensity=max(positive_cf)
		else:
			yes_intensity=0

	if len(positive_cf)>0 and len(negative_cf)>0 and float(max(positive_cf))!=0:
		no_intensity=math.fabs(min(negative_cf))/float(max(positive_cf))
	else:
		if len(negative_cf)>0:
			no_intensity==math.fabs(min(negative_cf))
		else:
			no_intensity=0

	print ("in short term")

	if len_positive>len_negative:
		print ("rather yes, intensity", math.fabs(yes_intensity))
		if math.fabs(yes_intensity)>10:
			print("clear answer")
	else:
		print ("rather no, intensity", math.fabs(no_intensity))
		if math.fabs(no_intensity)>2:
			print("clear answer")
	print()

	if (general_mean>0 and general_mean<10) or (general_mean<0 and general_mean>-10):
		blurred=True
		print ("blurred answer")
		


	print("-----------------------------------------------")




	positive_lm=[]
	negative_lm=[]

	for item in lm_of_freq:
		if item>0:
			positive_lm.append(item)
		else:
			negative_lm.append(item)

	print("-----------------------------------------------")
	#print ("positive lm mean", mean(positive_lm))
	#print ("negative lm mean", mean(negative_lm))

	print ()
	if len(positive_lm)>0:
		positive_lm_mean=max(positive_lm)
		#print ("positive lm maximum", max(positive_lm))
	else:
		positive_lm_mean=0
	if len(negative_lm)>0:
		negative_lm_mean=min(negative_lm)
		#print ("negative lm maximum", min(negative_lm))
	else:
		negative_lm_mean=0
		
	#print ("globaly")
	if  math.fabs(positive_lm_mean)> math.fabs(negative_lm_mean):
		pass
	#	print ("rather yes")
	else:
		pass
		#print ("rather no")
	print()



	#print("-----------------------------------------------")


	#--------------------------------output part



	#print ("freqs",plott)
	#print("mean freq",mean(plott))
	#print ("running mean", running_mean(plott,108))
	#print (type(running_mean(plott,108)))
	#print("times",plott2)
	#print(list(running_mean(plott,108)))



	#displaying lm of lm pure value
	ax=plt.figure()
	plt.rcParams['axes.facecolor']='#555555'
	plt.plot(plott2,plott, color="#55ee55")
	#plt.fill_between(plott2, plott, color="#33bb99")
	if not ennd :
		plt.show()
	





