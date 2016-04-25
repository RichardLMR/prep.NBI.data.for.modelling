# ***********************
# The research leading to the development of this program has received funding from the European Union Seventh Framework Programme (FP7/2007-2013) under grant agreement number 309837 (NanoPUZZLES project).
# http://wwww.nanopuzzles.eu
# ************************
#########################################################################################################
# test_1.py
# Implements unit tests This file was adapted from test_1.py obtained from version 0.1 of the following project:http://code.google.com/p/generic-qsar-py-utils/
# Copyright (c) 2013 Syngenta
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

#########################
project_name = 'NBIrecordParser'
run_tests_levels_below_top_dir = 1
this_test_levels_below_top_dir = 2
#########################
#************************
import sys,re,os,glob
cwd = os.getcwd()
for level in range(1,(run_tests_levels_below_top_dir+1)):
	os.chdir('..')
	#print os.getcwd()
del level
sys.path.append('utils')
from os_ind_delimiter import delimiter
os.chdir(cwd)
del cwd
project_modules_to_test_dir = delimiter().join(os.path.abspath(__file__).split(delimiter())[:-(this_test_levels_below_top_dir+1)])
print 'project_modules_to_test_dir=',project_modules_to_test_dir
sys.path.append(project_modules_to_test_dir)
sys.path.append(r'%s%sutils' %(project_modules_to_test_dir,delimiter()))
dir_of_the_current_test = delimiter().join(os.path.abspath(__file__).split(delimiter())[:-1])
print 'dir_of_the_current_test=',dir_of_the_current_test
sys.path.append(dir_of_the_current_test)
import unittest
from collections import defaultdict
#************************


class test_1(unittest.TestCase):
	
	# def clean_up_if_all_checks_passed(self,specific_files_not_to_delete):
		# all_files_to_delete = [file_name for file_name in glob.glob(r'%s%s*' % (delimiter().join(os.path.abspath(__file__).split(delimiter())[:-1]),delimiter())) if not re.search('(.\py$)',file_name) and not file_name in specific_files_not_to_delete]
		
		# for FILE_TO_DELETE in all_files_to_delete:
			# os.remove(FILE_TO_DELETE)
			# assert not os.path.exists(FILE_TO_DELETE), " This still exists: \n %s" % FILE_TO_DELETE
			# print 'Removed this temporary file: ', FILE_TO_DELETE
	
	# def compareOriginalAndNewFiles(self,orig_file,new_file):
		
		# print '-'*50
		# print 'Comparing: '
		# print orig_file
		# print 'to:'
		# print new_file
		# print '-'*50
		
		# file2Contents = {}
		
		# for file_name in [orig_file,new_file]:
			# f_in = open(file_name)
			# try:
				# file2Contents[file_name] = ''.join([re.sub(r'\r|\n','<EOL>',LINE) for LINE in f_in.readlines()])
				# del LINE
			# finally:
				# f_in.close()
				# del f_in
		# del file_name
		
		
		# assert file2Contents[orig_file] == file2Contents[new_file], " These files do not match: \n %s \n %s \n" % (orig_file,new_file)
	
	# def checkStillWorks(self,all_input_files,all_new_files):
		# all_orig_output_files_to_be_compared_as_required_for_unittesting = []
		# for new_file in all_new_files:
			# file_ext = new_file.split('.')[-1]
			# orig_file = re.sub('(\.%s$)' % file_ext,' - Copy.%s' % file_ext,new_file)
			# all_orig_output_files_to_be_compared_as_required_for_unittesting.append(orig_file)
			# self.compareOriginalAndNewFiles(orig_file,new_file)
		
		# files_not_to_delete = all_input_files+all_orig_output_files_to_be_compared_as_required_for_unittesting
		# self.clean_up_if_all_checks_passed(specific_files_not_to_delete=files_not_to_delete)
	
	def createExpected_nbi_1_xls_data(self):
		
		from write_expected_nbi_1_xls_data import expected_nbi_1_xls_data
		
		return expected_nbi_1_xls_data
	
	def analyseDictDifferences(self,dict1,dict2):
		print '*'*50
		print 'Determining differences between two dictionaries.' #c.f.https://groups.google.com/forum/#!topic/comp.lang.python/HAZFTHcQ1pI
		s_dict1 = set(dict1)
		s_dict2 = set(dict2)
		keys_in_dict2_not_dict1 = s_dict2 - s_dict1
		keys_in_dict1_not_dict2 = s_dict1 - s_dict2
		common_keys_with_different_values = set([key for key in s_dict1 & s_dict2 if dict1[key] != dict2[key]])
		del key
		print 'keys_in_dict2_not_dict1=',keys_in_dict2_not_dict1
		print 'keys_in_dict1_not_dict2=',keys_in_dict1_not_dict2
		print 'common_keys_with_different_values=',common_keys_with_different_values
		if not 0 == len(common_keys_with_different_values):
			print 'Corresponding simple (not dictionary) values will be printed below (after applying this function recursively to find them if necessary):'
			for key in common_keys_with_different_values:
				if (not (type(defaultdict(dict)) == type(dict1[key])) and not (type(defaultdict(dict)) == type(dict2[key])) and not (type({}) == type(dict1[key])) and not (type({}) == type(dict2[key]))) or (not type(dict1[key])==type(dict2[key])):
					print '-'*50
					print 'key=',key
					print 'dict1[key]=',dict1[key]
					print 'dict2[key]=',dict2[key]
					print '-'*50
				else:
					self.analyseDictDifferences(dict1[key],dict2[key])
		print '*'*50
	
	def seeIfDataDictsIdentical(self,expected,real):
		bothDataDictsIdentical =False
		
		if expected == real: #this seems naive, but the following suggests this should work: http://stackoverflow.com/questions/4527942/comparing-two-dictionaries-in-python
			bothDataDictsIdentical = True
		else:
			self.analyseDictDifferences(dict1=expected,dict2=real)
		
		
		return bothDataDictsIdentical
	
	def test_seeIfDataDictsIdentical(self):
		##############################
		print 'Running unittests for this project: ', project_name
		print 'Running this unittest: ', self._testMethodName
		##############################
		###################################
		#I need to make sure self.seeIfDataDictsIdentical(expected,real) will work for a dict of defaultdicts and dicts as anNBIrecord.dataDict (currently!) is!
		###################################
		
		#******************************************
		toy_d_1 = {'td1_k1':1.0,'td1_k2':'c'}
		toy_d_2 = {'td2_k1':1.5,'td2_k2':'x'}
		toy_dd = defaultdict(dict)
		toy_dd[1]['toy_dd_k1_1'] = 22.0
		toy_dd[2]['toy_dd_k2_1'] = 14.0
		
		toy = {'A':toy_d_1,'B':toy_d_2,'C':toy_dd}
		#******************************************
		
		#Following is copied,pasted and adapted from toy construction as I wish to test comparison of independently created dictionaries: beware copying in Python! http://stackoverflow.com/questions/2465921/how-to-copy-a-dictionary-and-only-edit-the-copy
		
		#******************************************
		matches_toy_d_1 = {'td1_k1':1.0,'td1_k2':'c'}
		matches_toy_d_2 = {'td2_k1':1.5,'td2_k2':'x'}
		matches_toy_dd = defaultdict(dict)
		matches_toy_dd[1]['toy_dd_k1_1'] = 22.0
		matches_toy_dd[2]['toy_dd_k2_1'] = 14.0
		
		matches_toy = {'A':matches_toy_d_1,'B':matches_toy_d_2,'C':matches_toy_dd}
		#******************************************
		
		#******************************************
		same_keys_some_diff_values_to_toy_d_1 = {'td1_k1':-1.0,'td1_k2':'c*'}
		same_keys_some_diff_values_to_toy_d_2 = {'td2_k1':1.5,'td2_k2':'x*'}
		same_keys_some_diff_values_to_toy_dd = defaultdict(dict)
		same_keys_some_diff_values_to_toy_dd[1]['toy_dd_k1_1'] = 21.0
		same_keys_some_diff_values_to_toy_dd[2]['toy_dd_k2_1'] = 14.0
		
		same_keys_some_diff_values_to_toy = {'A':same_keys_some_diff_values_to_toy_d_1,'B':same_keys_some_diff_values_to_toy_d_2,'C':same_keys_some_diff_values_to_toy_dd}
		#******************************************
		
		#******************************************
		just_one_more_key_vs_toy_d_1 = {'td1_k1':1.0,'td1_k2':'c'}
		just_one_more_key_vs_toy_d_2 = {'td2_k1':1.5,'td2_k2':'x'}
		just_one_more_key_vs_toy_dd = defaultdict(dict)
		just_one_more_key_vs_toy_dd[1]['toy_dd_k1_1'] = 22.0
		just_one_more_key_vs_toy_dd[2]['toy_dd_k2_1'] = 14.0
		just_one_more_key_vs_toy_dd[2]['toy_dd_k2_2'] = 17.0
		
		just_one_more_key_vs_toy = {'A':just_one_more_key_vs_toy_d_1,'B':just_one_more_key_vs_toy_d_2,'C':just_one_more_key_vs_toy_dd}
		#******************************************
		
		assert self.seeIfDataDictsIdentical(expected=matches_toy,real=toy)
		assert not self.seeIfDataDictsIdentical(expected=same_keys_some_diff_values_to_toy,real=toy)
		assert not self.seeIfDataDictsIdentical(expected=just_one_more_key_vs_toy,real=toy)
	
	def test_extractData(self):
		'''
		This test loads data from nbi_1.xls into an instance of the class NBIrecord() and checks that the data extracted matches the expected structured data object.
		nbi_1.xls is an exported record from the NBI Knowledgebase database (http://nbi.oregonstate.edu/) kindly provided in April 2014 by Dr Stacey Harper and Bryan Harper.
		[Further information about the NBI Knowledgebase can be found in the following publications: 
		(1)Liu et al. 2013 http://dx.doi.org/10.2147/IJN.S40742; (2)Tang et al. 2013 http://dx.doi.org/10.2147/IJN.S40974; (3) Harper et al. 2008 http://dx.doi.org/10.1504/IJNT.2008.016552]
		'''
		##############################
		print 'Running unittests for this project: ', project_name
		print 'Running this unittest: ', self._testMethodName
		print self.test_extractData.__doc__
		##############################
		
		from NBIrecordParser import NBIrecord
		
		anNBIrecord = NBIrecord(r'%s%snbi_1.xls' % (dir_of_the_current_test,delimiter()))
		anNBIrecord.extractData()
		anNBIrecord.cleanUp()
		
		real = anNBIrecord.dataDict
		del anNBIrecord
		
		expected = self.createExpected_nbi_1_xls_data()
		
		#############
		#####Debug###
		#############
		#del real['NBI-EMZ Data']
		#del expected['NBI-EMZ Data']
		#############
		
		assert self.seeIfDataDictsIdentical(expected,real)
