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
import os,sys,getopt,re,platform

def saveXlsFileInExcel(xls_file):
	
	'''
	This function is designed to open and save an Excel "....xls" file using Excel (using the same name as the original file) i.e. it will fail if you do not have Excel installed and/or you are not running Windows.
	The purpose of this function is to ensure that values created via Excel formulae can be correctly extracted via the Python module xlrd.
	'''
	
	try:
		assert 'Windows' == platform.system(), "saveXlsFileinExcel(xls_file) cannot work as you are not running this program under the Windows OS!"
		tmp_WScript = 'tmp.vbs'
		f_out = open(tmp_WScript,'wb')
		try:
			f_out.write('Set excelFileParser = CreateObject("Excel.Application")\r\n')
			f_out.write('Set openWorkBook = excelFileParser.Workbooks.Open("%s")\r\n' % os.path.abspath(xls_file))
			f_out.write('openWorkBook.save\r\n')
			f_out.write('openWorkBook.Application.Quit\r\n')
		finally:
			f_out.close()
			del f_out
		
		#assert 0 == os.system('WScript %s' % tmp_WScript)#, "The temporary VBS script created for the purpose of opening and saving %s, under the same name, would not run!" % xls_file #Actually, assert 0 === os.system(<command>) will not work here! VBS error should pop up on the screen if any error occurs!
		os.system('WScript %s' % tmp_WScript)
		
		os.remove(tmp_WScript)
	except AssertionError,ass_msg:
		print ass_msg
		print __doc__

def main():
	print 'THE START'
	
	#####################
	opts,args = getopt.getopt(sys.argv[1:],'i:',['xls_file='])
	for o,v in opts:
		if '-i' == o:
			xls_file = re.sub('"','',v)
	######################
	
	saveXlsFileInExcel(xls_file)
	
	print 'THE END'
	
	return 0

if __name__ == '__main__':
	sys.exit(main())
