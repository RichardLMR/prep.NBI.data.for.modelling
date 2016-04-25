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

import unicodecsv as csv #see https://pypi.python.org/pypi/unicodecsv and http://docs.python.org/2/library/csv.html
from xlrd import open_workbook
import re

def changeXls2txtFiles(xls_file,input_extension_regex):
	
	all_txt_files = []
	
	book = open_workbook(xls_file)
	
	
	
	for sheet in book.sheets():
		
		
		txt_file = input_extension_regex.sub('_s%s.txt' % sheet.name,xls_file)
		
		print '*'*50
		print 'Converting sheet no. %s in %s to a tab-delimited .txt file:%s.' % (sheet.name,xls_file,txt_file)
		
		output = open(txt_file,'wb')
		try:
			writer = csv.writer(output, delimiter='\t',quotechar='"', quoting=csv.QUOTE_ALL)#alternatives: QUOTE_MINIMAL,QUOTE_NONUMERIC
			try:
				for row_index in range(sheet.nrows):
					row_list = []
					for col_index in range(sheet.ncols):
						row_list.append(sheet.cell(row_index,col_index).value)
						#sheet.name,row_index,col_index)
						#print 'Gets to here!'
					try:
						writer.writerow(row_list)
					except UnicodeEncodeError:
						writer.writerow(['UnicodeEncodeError']*len(row_list))
						print 'ERROR: UnicodeEncodeError encountered for this row:',row_list
						#sys.exit(1)
			finally:
				del writer
		finally:
			output.close()
			del output
		
		print 'CONVERTED %s to a tab-delimited .txt file:%s.' % (xls_file,txt_file)
		print '*'*50
		
		all_txt_files.append(txt_file)
		
		
		
	return all_txt_files