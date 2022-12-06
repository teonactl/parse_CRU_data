# Python script for converting datasets from  the CRUdata datasets.
# 
# @teonactl  06/12/2022 
#
# Example use for temp_lutherbacher_su and temp_xoplaki_spcal culating a single year dataset (1500):
# python parse_CRU_data.py -suf temp_luterbacher_su.txt -spf temp_xoplaki_sp.txt -r 70 -c 130 -urlo 39.75 -urla 69.75 -lllo -24.75 -llla 35.25 -y_sta 1500 -y_sto 1500
#
# Example use for prec_pauling_sp and prec_pauling_su calculating a single year dataset (1500):
# python parse_CRU_data.py -suf prec_pauling_su.txt -spf prec_pauling_sp.txt -r 82 -c 140 -urlo 39.75 -urla 70.75 -lllo -29.75 -llla 30.25 -y_sta 1500 -y_sto 1500
#
# Use -map or --show_map to simulate a map instead of writing the data to disk
#
##########################################
# CONSTANT RELATIONSHIP TABLE            #
##########################################
# FOR TEMP DATA :	                     #
# grid extension:    					 #
# LAT    			LON                  # DATASET RELATED CUSTOMIZATION 
# 35.25N-69.75N / 24.75W-39.75E          # See --> https://crudata.uea.ac.uk/cru/projects/soap/data/recon/#paul05
# years: 1500 to 2002		             # 
# grid dimensions : 130 cols x 70  rows  #	
#----------------------------------------#
# FOR PREC DATA:                         #
# grid extension:    					 #
# LAT    			LON                  #
# 30.25N-70.75N / 29.75W-39.75E          #
# years: 1500 to 2000                    #
# grid dimensions : 140 cols x 82 rows   #
##########################################


# Imports
import argparse
import json
import csv
from os.path import exists
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon
import matplotlib.colors

# Args Parser
parser = argparse.ArgumentParser( prog = 'scrape_CRU_data',
                    description = 'Python script for converting datasets from  the CRUdata datasets.',
                    epilog = '@teonactl  06/12/2022')

parser.add_argument("-suf", "--summer_file", required=True)
parser.add_argument("-spf", "--spring_file", required=True)
parser.add_argument("-c", "--columns_n", required=True)
parser.add_argument("-r", "--rows_n", required=True)
parser.add_argument("-urlo", "--up_right_lon", required=True)
parser.add_argument("-urla", "--up_right_lat", required=True)
parser.add_argument("-lllo", "--low_left_lon", required=True)
parser.add_argument("-llla", "--low_left_lat", required=True)
parser.add_argument("-y_sta", "--year_start", required=True)
parser.add_argument("-y_sto", "--year_stop", required=True)
parser.add_argument("-map", "--show_map", required=False)


args = parser.parse_args()
print(f'Extracting summer data from  {args.summer_file}...')
print(f'Extracting spring data from  {args.spring_file}...')
print(f'Using  {args.columns_n} columns and {args.rows_n} rows...')
print(f'From year {args.year_start} to  {args.year_stop} ')
print(f'Using point LON: {args.up_right_lon} LAT: {args.up_right_lat} for top right...')
print(f'Using point LON: {args.low_left_lon} LAT: {args.low_left_lat} for down left...')

# Clear previous files 

su_exists = exists(f"{args.summer_file}.json")
sp_exists = exists(f"{args.spring_file}.json")
csv_exists = exists(f"{args.spring_file[:-4].split('_')[0]}_result.csv")
if csv_exists:
	print("A result file for this dataset already exist:")
	print(f"{args.spring_file[:-4].split('_')[0]}_result.csv")
	print("Move the file or change its name before proceding..")
	sys.exit()

if su_exists or sp_exists:
	try:
		os.remove(f"{args.summer_file}.json") 
		os.remove(f"{args.summer_file}.json")
		print("Previous json deleted...")
	except Exception:
		print("Previous json not deleted..")

# Extracting all lines from files
lines_su = []
with open(args.summer_file, "r") as f:
	for i in f.readlines():
		lines_su.append(i)
print("Len summer file: ", len(lines_su))
lines_sp = []
with open(args.spring_file, "r") as f:
	for i in f.readlines():
		lines_sp.append(i)
print("Len spring file: ", len(lines_sp))

try:
	len(lines_sp)==len(lines_su)

except Exception:
	print("Datasets not mergeable, different number of rows...")
	sys.exit()

# If the line has only 2 elements, write a new Year in result dict
su_db = {}
allines_su= []
for i in lines_su :
	line = i.strip().split("\t")
	if len(line)==2:
		su_db[line[0]] = []
	else:
		allines_su.append(line)

sp_db = {}
allines_sp= []
for i in lines_sp :
	line = i.strip().split("\t")
	if len(line)==2:
		sp_db[line[0]] = []
	else:
		allines_sp.append(line)

# Write the other lines except the year's ones, check if the result is still divisible for n of rows
for ob in su_db:
	su_db[ob] =allines_su[:int(args.rows_n)]
	allines_su = allines_su[int(args.rows_n):]
	if not len(allines_su)%int(args.rows_n)==0:
		print(f"Error: wrong number of rows in{args.summer_file}"*100)
		sys.exit()
for ob in sp_db:
	sp_db[ob] =allines_sp[:int(args.rows_n)] 
	allines_sp = allines_sp[int(args.rows_n):]
	if not len(allines_sp)%int(args.rows_n)==0:
		print(f"Error: wrong number of rows in{args.spring_file}"*100)
		sys.exit()

# Transform dict in json
json_object_su = json.dumps(su_db, indent = 4)
json_object_sp = json.dumps(sp_db, indent = 4)

print("Writing jsons...", len(json_object_sp))
with open (f"{args.summer_file[:-4]}.json", "w+") as of:
	of.write(json_object_su)
with open (f"{args.spring_file[:-4]}.json", "w+") as of:
	of.write(json_object_sp)
print("Creating a map..")

# Create a basemap using the interested area coordinates
m = Basemap( projection='cyl',
 llcrnrlat =float(args.low_left_lat )+ 0.25, llcrnrlon =float(args.low_left_lon) -0.25, # cit. "(all coordinates given here denote the centre of each box)"
 urcrnrlat =float(args.up_right_lat)+ 0.25 , urcrnrlon= float(args.up_right_lon) -0.25
 )

# Create a grid from the map using the user feeded dimensions
fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111)
m.etopo(scale=0.5, alpha=0.5)
m.drawcoastlines()
lons, lats, x, y = m.makegrid(int(args.columns_n), int(args.rows_n), returnxy=True)
m.scatter(x, y)

# Recreate the original paper's grid
quadri = []
for x, lon in enumerate(lons[::-1]):

	for i, lo in enumerate(lons[::-1][x]):
		low_left = [lons[::-1][x][i], lats[::-1][x][i]-0.5 ]
		low_right = [lons[::-1][x][i]+0.5, lats[::-1][x][i]-0.5 ]
		hig_left = [lons[::-1][x][i], lats[::-1][x][i] ]
		hig_right = [lons[::-1][x][i]+0.5, lats[::-1][x][i]]
		quad = [hig_left, hig_right, low_right, low_left]
		quadri.append(quad)


patches = []
centers = []



# Open previously made jsons and check the result is coerent
with open(f"{args.summer_file[:-4]}.json", "r") as  suf:
	summer = json.load(suf)

with open(f"{args.spring_file[:-4]}.json", "r") as  suf:
	spring = json.load(suf)

try:
	len(summer) ==len(spring)
except Exception :
	print("ERROR: wrong number of rows in one file!!")
	sys.exit()




# Make a flat list (just like our maps "quadri" list)
summer_l = [ ]
spring_l = [ ]
for r in summer:
	for d in summer[r]:
		for c in d:
			summer_l.append(c) 
for r in spring:
	for d in spring[r]:
		for c in d:
			spring_l.append(c) 


# Check coherence
try:
	len(summer_l)/len(summer) ==len(centers)
except Exception :
	print("ERROR: wrong number of rows / centers!!")
	sys.exit()

# Build a sample map for debugging, colors adapted for temp map..
if args.show_map :
	su=summer[args.show_map]
else: 
	su=summer["1500"]
year = []
for i in su:
	year = year + i

def cb(i):
	#print(*args)
	c = float(year[i])
	if args.spring_file[:-4].split('_')[0] == "temp":
		if c == -99.999:
			return "white"
		if -20 > c<= -30:
			return "black"
		if  -15>= c > -20 :
			return "purple"
		if  -10 >= c > -15:
			return "blue"
		if -5 >=c > -10:
			return "cyan"
		if  0>=c > -5:
			return "turquoise"
		if 2.5 >=c > 0:
			return "green"
		if 5 >= c > 2.5:
			return "greenyellow"
		if 10>=c > 5:
			return "yellow"
		if  12.5 > c > 10:
			return "orange"
		if 15>=c > 12.5:
			return "red"
		if 20 >= c > 15:
			return "darkorchid"
		if  c > 20 :
			return "purple"
		else :
			return "white"
	
	elif args.spring_file[:-4].split('_')[0] == "prec":
		if c<= -30:
			return "white"
		if  50 > c > 0:
			return "red"
		if  100 >= c > 50:
			return "orangered"
		if 150 >=c > 100:
			return "orange"
		if  200 >=c > 150:
			return "yellow"
		if  250 >= c > 200:
			return "greenyellow"
		if 300 >=c > 250:
			return "green"
		if  350 >=c > 300:
			return "lightseagreen"
		if 400 >=c > 350:
			return "turquoise"
		if 450>=c > 400:
			return "cyan"
		if 500>=c > 450:
			return "deepskyblue"
		if 550>=c > 500:
			return "dodgerblue"
		if 600>=c > 550:
			return "royalblue"
		if 650>=c > 600:
			return "mediumblue"
		if 700>=c > 650:
			return "red"
		if c > 700:
			return "black"		

	else:
		print("Data type not supported")
		sys.exit()

# Calc the center of every square area in "quadri" and populate "centers" flat list
for i, q in enumerate(quadri):
	square = np.array(q)
	p = Polygon(square, facecolor=cb(i))

	patches.append(p)
	center = (square[0][0] + 0.25,square[0][1] - 0.25 )
	centers.append(center)

p = PatchCollection(patches,  edgecolor='k',match_original=True, linewidths=1.5)
ax.add_collection(p)

# Show the map and exit [for debug purposes]
if args.show_map:
	print("SHOWING MAP FOR YEAR "+args.show_map+" FOR DEBUGGING...")
	plt.title( f"{args.spring_file[:-4].split('_')[0]} map for  for year {args.show_map}")
	#plt.colorbar(cmap = custom_map, ticks=[-99, 30] )
	plt.show()
	sys.exit()


# Start creating a new file (csv) with the recipe:
# YEAR, LON_CENTER, LAT_CENTER, SUMMER_DATA, SPRING_DATA
# Every center is from a squared area 0.5° by 0.5°
rows =[]
with open(f"{args.spring_file[:-4].split('_')[0]}_result.csv", "w+") as f:
	csvwriter = csv.writer(f)

	csvwriter.writerow(["yr","lon_c","lat_c",f"{args.summer_file[:-4].split('_')[0]}_su",f"{args.spring_file[:-4].split('_')[0]}_sp"])

	for i, anno in enumerate(range(int(args.year_start), int(args.year_stop)+1)):
		print("WRITING...")
		print(f" {anno} to {int(args.year_stop)} ")
		for c, center in enumerate(centers):

			row = [ str(anno) , center[0],center[1], summer_l.pop(0), spring_l.pop(0)]
			rows.append(row)
			csvwriter.writerow(row)

print(f" FINISHED, writed {len(rows)} rows !" )

