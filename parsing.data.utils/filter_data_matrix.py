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
import sys,re,csv,getopt
try:
	from misc_utils import getNewFileName,getCSVfileTitlesInOrder,getCSVdictRows,writeCSVoutput
except ImportError:
	pass #This should only occur if importing this code when running code in another working directory; the code being run should separately import misc_utils, as well as the functions from this file, so this failure should not matter.

def valueIsMissing(ostensible_value):
	if '' == ostensible_value or 'unknown' == ostensible_value.lower():
		return True
	else:
		return False

def removeExtraColumns(data,output_columns):
	for row in data:
		for key in row.keys():
			if not key in output_columns:
				del row[key]
		del key
	del row
	
	return data

def dropPredefinedColumns(csv_file,columns_to_delete):
	suffix = '_dpc.csv'
	
	new_csv_file = getNewFileName(suffix,csv_file)
	
	data = getCSVdictRows(csv_file)
	
	output_columns = [col_title for col_title in getCSVfileTitlesInOrder(csv_file) if not col_title in  columns_to_delete]
	del col_title
	
	data = removeExtraColumns(data,output_columns)
	
	writeCSVoutput(new_csv_file,data,output_columns)
	
	return new_csv_file

def rowHasMissingEntries(csv_row,cols_for_which_missing_values_ok):
	
	keys_to_check = [key for key in csv_row.keys() if not key in cols_for_which_missing_values_ok]
	del key
	
	if 0 == len([key for key in keys_to_check if valueIsMissing(csv_row[key])]):
		return False
	else:
		return True

def colHasMissingEntries(col_title,data):
	
	if 0 == len([row for row in data if valueIsMissing(row[col_title])]):
		return False
	else:
		return True


def dropIncompleteRows(csv_file,cols_for_which_missing_values_ok):
	suffix = '_dr.csv'
	
	new_csv_file = getNewFileName(suffix,csv_file)
	
	data = [csv_row for csv_row in getCSVdictRows(csv_file) if not rowHasMissingEntries(csv_row,cols_for_which_missing_values_ok)]
	del csv_row
	
	writeCSVoutput(new_csv_file,data,output_columns=getCSVfileTitlesInOrder(csv_file))
	
	return new_csv_file

def dropIncompleteColumns(csv_file):
	suffix = '_dc.csv'
	
	new_csv_file = getNewFileName(suffix,csv_file)
	
	data = getCSVdictRows(csv_file)
	
	output_columns = [col_title for col_title in getCSVfileTitlesInOrder(csv_file) if not colHasMissingEntries(col_title,data)]
	del col_title
	
	data = removeExtraColumns(data,output_columns)
	
	writeCSVoutput(new_csv_file,data,output_columns)
	
	return new_csv_file

def rowHasForbiddenID(csv_row,id_col_title,forbidden_ids):
	
	if csv_row[id_col_title] in forbidden_ids:
		return True
	else:
		return False

def dropPredefinedRows(csv_file,id_col_title,forbidden_ids):
	suffix = '_dpr.csv'
	
	new_csv_file = getNewFileName(suffix,csv_file)
	
	data = [csv_row for csv_row in getCSVdictRows(csv_file)]
	del csv_row
	
	#==========================
	#Just checking:
	assert type([]) == type(forbidden_ids)
	all_ids = [csv_row[id_col_title] for csv_row in data]
	del csv_row
	for ID in forbidden_ids:
		assert ID in all_ids, "This ID must have been specified incorrectly:%s!" % ID
	del all_ids
	#==========================
	
	data = [csv_row for csv_row in data if not rowHasForbiddenID(csv_row,id_col_title,forbidden_ids)]
	del csv_row
	
	writeCSVoutput(new_csv_file,data,output_columns=getCSVfileTitlesInOrder(csv_file))
	
	return new_csv_file

def countColEntries(col_title,data):
	
	return len([row for row in data if not valueIsMissing(row[col_title])])


def findColumnsWithLessThanXentries(input_file,x):
	
	data = getCSVdictRows(input_file)
	
	return [col_title for col_title in getCSVfileTitlesInOrder(input_file) if x > countColEntries(col_title,data)]

def findColumnsWithConstantEntries(input_file):
	
	data = getCSVdictRows(input_file)
	
	cols_with_const_entries = []
	
	for title in getCSVfileTitlesInOrder(input_file):
		if 1 == len(set([ROW[title] for ROW in data])):
			cols_with_const_entries.append(title)
	
	return cols_with_const_entries

def reportNumberOfNonMissingEntriesPerColumn(input_file):
	
	print '*'*50
	print 'Reporting the number of non-missing entries per column in the following file:',input_file
	data = getCSVdictRows(input_file)
	
	for title in getCSVfileTitlesInOrder(input_file):
		print 'title=%s,count=%d' % (title,countColEntries(title,data))
	
	print 'REPORTED the number of non-missing entries per column in the following file:',input_file
	print '*'*50

# def main():
	
	# columns_to_delete = []
	
	# #######################
	# opts,args = getopt.getopt(sys.argv[1:],'i:c:',['input_file=','columns_to_delete='])
	# for o,v in opts:
		# if '-i' == o:
			# input_file = r'%s' % re.sub('"','',v)
		# if '-c' == o:
			# columns_to_delete = re.sub('"','',v).split(";")
	# try:
		# del o,v,opts,args
	# except NameError:
		# pass
	# ######################
	
	# print 'THE START'
	
	
	# if not 0 == len(columns_to_delete):
		# csv_file = dropPredefinedColumns(input_file,columns_to_delete)
	# else:
		# csv_file = input_file
	
	# csv_file = dropIncompleteRows(csv_file)
	
	# csv_file = dropIncompleteColumns(csv_file)
	
	
	
	# print 'THE END'
	
	# return 0

# if __name__ == '__main__':
	# sys.exit(main())
