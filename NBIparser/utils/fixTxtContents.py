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

import re,sys,csv,os,shutil

def modifyColTitleOrContentItem(col_title_or_content_item):
	
	col_title_or_content_item = re.sub('(\r|\n|\t)',' ',col_title_or_content_item)
	
	#col_title_or_content_item = re.sub('(\s*;\s*)',';',col_title_or_content_item)
	
	#col_title_or_content_item = re.sub('(\s*:\s*)',':',col_title_or_content_item)
	
	#col_title_or_content_item = re.sub('(\s*\[\s*)','[',col_title_or_content_item)
	
	col_title_or_content_item = col_title_or_content_item.strip()
	
	return col_title_or_content_item


def getRows(tab_delimited_text_file):
	
	f_in = open(tab_delimited_text_file,'rb') #note to self:'rb' not used for ITN parser...
	try:
		try:
			reader = csv.reader(f_in,delimiter='\t',quotechar='"')
			rows = [ROW for ROW in reader] #first ROW is a list of column titles, including internal line endings if applicable
		finally:
			del reader
	finally:
		f_in.close()
		del f_in
	
	return rows

def fixContents_step1_here(input_file,intermediate_name):
	
	f_out = open(intermediate_name,'wb')
	try:
		for row in getRows(input_file):
			f_out.write('\t'.join([modifyColTitleOrContentItem(part) for part in row])+'\n')
	finally:
		f_out.close()
		del f_out


def fixContents(input_file,intermediate_name='tmp.txt'):
	
	print '='*50
	print 'Updating %s via intermediate file %s' % (input_file,intermediate_name)
	
	fixContents_step1_here(input_file,intermediate_name)
	
	shutil.copyfile(intermediate_name,input_file)
	
	os.remove(intermediate_name)
	print '='*50
	
	return input_file
