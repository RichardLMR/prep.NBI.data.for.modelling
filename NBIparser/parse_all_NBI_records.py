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
import sys,re,getopt,glob,time
from NBIrecordParser import NBIrecord
sys.path.append('utils')
from os_ind_delimiter import delimiter

def main():
	################
	opts,args = getopt.getopt(sys.argv[1:],'d:',['dir_with_nbi_records='])
	for o,v in opts:
		if '-d' == o:
			dir_with_nbi_records = r'%s' % re.sub('"','',v)
	#################
	
	print '='*50
	print 'Parsing NBI Knowledgebase records found in this directory:',dir_with_nbi_records
	start = time.clock()
	
	
	ok_parse_count = 0
	bad_parse_count = 0
	for input_file in glob.glob(r'%s%snbi_*.xls' % (dir_with_nbi_records,delimiter())):
		print '#'*50
		anNBIrecord = NBIrecord(input_file)
		try:
			anNBIrecord.extractData()
			anNBIrecord.cleanUp()
			ok_parse_count += 1
		except Exception,err_msg:
			print '!'*50
			print 'Problem parsing this file: ',input_file
			print err_msg
			bad_parse_count += 1
			print '!'*50
		del anNBIrecord
		print '#'*50
	
	end = time.clock()
	print 'SUCCESSFULLY PARSED %d NBI Knowledgebase records found in this directory:' % ok_parse_count,dir_with_nbi_records
	print 'PROBLEMS ENCOUNTERED WHEN PARSING %d NBI Knowledgebase records found in this directory:' % bad_parse_count,dir_with_nbi_records
	print 'Time taken = (roughly) %.f minutes.' % (end-start)/60.0
	print '='*50
	
	return 0

if __name__ == '__main__':
	sys.exit(main())
