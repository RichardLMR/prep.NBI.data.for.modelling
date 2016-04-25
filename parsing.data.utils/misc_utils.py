# ***********************
# The research leading to the development of this program has received funding from the European Union Seventh Framework Programme (FP7/2007-2013) under grant agreement number 309837 (NanoPUZZLES project).
# http://wwww.nanopuzzles.eu
# ************************
#########################################################################################################
# Copyright (c) 2014 Liverpool John Moores University
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at
# your option) any later version.

# THIS PROGRAM IS MADE AVAILABLE FOR DISTRIBUTION WITHOUT ANY FORM OF WARRANTY TO THE 
# EXTENT PERMITTED BY APPLICABLE LAW.  THE COPYRIGHT HOLDER PROVIDES THE PROGRAM \"AS IS\" 
# WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT  
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
# PURPOSE. THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE PROGRAM LIES
# WITH THE USER.  SHOULD THE PROGRAM PROVE DEFECTIVE IN ANY WAY, THE USER ASSUMES THE
# COST OF ALL NECESSARY SERVICING, REPAIR OR CORRECTION. THE COPYRIGHT HOLDER IS NOT 
# RESPONSIBLE FOR ANY AMENDMENT, MODIFICATION OR OTHER ENHANCEMENT MADE TO THE PROGRAM 
# BY ANY USER WHO REDISTRIBUTES THE PROGRAM SO AMENDED, MODIFIED OR ENHANCED.

# IN NO EVENT UNLESS REQUIRED BY APPLICABLE LAW OR AGREED TO IN WRITING WILL THE 
# COPYRIGHT HOLDER BE LIABLE TO ANY USER FOR DAMAGES, INCLUDING ANY GENERAL, SPECIAL,
# INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OR INABILITY TO USE THE
# PROGRAM (INCLUDING BUT NOT LIMITED TO LOSS OF DATA OR DATA BEING RENDERED INACCURATE
# OR LOSSES SUSTAINED BY THE USER OR THIRD PARTIES OR A FAILURE OF THE PROGRAM TO 
# OPERATE WITH ANY OTHER PROGRAMS), EVEN IF SUCH HOLDER HAS BEEN ADVISED OF THE 
# POSSIBILITY OF SUCH DAMAGES.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#########################################################################################################
import sys,re,csv
#########################################################################################################
def getNewFileName(suffix,csv_file):
	assert re.search('(\.csv$)',csv_file), "csv_file:%s???" % csv_file
	new_csv_file = re.sub('(\.csv$)',suffix,csv_file)
	assert not new_csv_file == csv_file
	
	return new_csv_file

def getCSVfileTitlesInOrder(csv_file):
	assert re.search('(\.csv$)',csv_file)
	
	f_in = open(csv_file,'rb')
	try:
		reader = csv.reader(f_in,delimiter=',',quotechar='"')
		try:
			titles = reader.next()
		finally:
			del reader
	finally:
		f_in.close()
		del f_in
	
	return titles

def getCSVdictRows(csv_file):
	f_in = open(csv_file,'rb')
	try:
		reader = csv.DictReader(f_in)
		data = [LINE for LINE in reader]
		del LINE
	finally:
		f_in.close()
		del f_in
	
	return data

def writeCSVoutput(new_csv_file,data,output_columns):
	
	f_out = open(new_csv_file,'wb')
	try:
		writer = csv.DictWriter(f_out,fieldnames=output_columns)
		try:
			colDict = dict(zip(output_columns,output_columns))
			writer.writerow(colDict)
			del colDict
			
			for row in data:
				writer.writerow(row)
		finally:
			del writer
	finally:
		f_out.close()
		del f_out


