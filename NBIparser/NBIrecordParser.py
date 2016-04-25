'''
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

NBIrecordParser.py : 
This file defines NBIrecord() class for loading data from an individual nbi_<ID>.xls file as exported from the NBI Knowledgebase:http://nbi.oregonstate.edu/
[Further information about the NBI Knowledgebase can be found in the following publications: 
(1)Liu et al. 2013 http://dx.doi.org/10.2147/IJN.S40742; (2)Tang et al. 2013 http://dx.doi.org/10.2147/IJN.S40974; (3) Harper et al. 2008 http://dx.doi.org/10.1504/IJNT.2008.016552]

NBIrecord() class inserts workbook data into <instance of NBIrecord()>.dataDict


It can also be used as a script, which will print the <instance of NBIrecord()>.dataDict contents, and corresponding input file name, for a commandline specified NBI workbook:
python NBIrecordParser.py -i nbi_<ID>.xls

Dependencies:
1. Python interpreter. http://python.org/ Python version >= 2.5 (at least) is required. Python version 2.7.3 is recommended since all code development employed this version of Python.
2. xlrd,xlwt packages from http://www.python-excel.org/ [versions 0.9.2 and 0.7.5 of xlrd and xlwt were used respectively for development]
3. unicodecsv packages from https://pypi.python.org/pypi/unicodecsv [version 0.9.4 was used for development]
'''
#######################
#######Globals#########
#######################
allowed_NBI_sheet_types = ['NBI Material','NBI-EMZ Exp. Design','NBI-EMZ Data'] #must be kept consistent with def extractData(self):
#######################
import sys,os,re,getopt,csv,glob
from collections import defaultdict
dir_of_this_file = re.sub('(NBIrecordParser\.py)','',os.path.abspath(__file__)) #<TO DO?>:UPDATE THIS AS THIS WILL NOT WORK IF A CORRESPONDING PYC FILE EXISTS (WHICH WAS CREATED AFTER THE LAST CHANGE TO THIS FILE)!!!! CONSIDER USING THE inspect MODULE? (ACTUALLY, MODIFIED .cleanUp() METHOD MAY AVOID THIS PROBLEM!)
sys.path.append(r'%sutils' % dir_of_this_file)
from os_ind_delimiter import delimiter
try:
	from fixTxtContents import fixContents
	from xls2txt import changeXls2txtFiles
	from xlsExcelSave import saveXlsFileInExcel
except Exception,err_msg:
	print __doc__
	print 'Error occured!\n',err_msg
	sys.exit(1)
#######################

class NBIrecord():
	
	def __init__(self,nbi_xls_file,input_extension_regex=re.compile('(\.xls$)')):
		print 'Parsing ',nbi_xls_file
		self.nbi_xls_file = nbi_xls_file
		self.input_extension_regex = input_extension_regex
		self.dataDict = defaultdict(dict)
		self.txt_sheets = []
		
	
	def convert2TxtSheets(self):
		
		saveXlsFileInExcel(xls_file=self.nbi_xls_file)
		
		orig_txt_files = changeXls2txtFiles(xls_file=self.nbi_xls_file,input_extension_regex=self.input_extension_regex)
		
		self.txt_sheets += [fixContents(input_file=txt_file) for txt_file in orig_txt_files]
	
	def idTxtSheetType(self,txt_sheet_name):
		type = re.sub('(\.txt$)','',txt_sheet_name).split('_s')[1]
		assert type in allowed_NBI_sheet_types, "txt file:%s\ntype:%s\n" % (txt_sheet_name,type)
		return type
	
	def extractRows(self,txt_sheet_name):
		f_in = open(txt_sheet_name,'rb')
		try:
			reader = csv.reader(f_in,delimiter='\t',quotechar='"')
			try:
				rows = [ROW for ROW in reader]
			finally:
				del reader
				del ROW
		finally:
			f_in.close()
			del f_in
		return rows
	
	def prepareDatum(self,str):
		try:
			return round(float(str),12) #inspection of nbi_1.xls (formulae cells copied and pasted as values) => no number was reported up to more than 16 dp, but initial inspection of code output suggested some numbers differed from their Excel values by less than 10^-16; however, further comparison between some expected and Python extracted values suggested differences of the order of 10^-12
		except ValueError:
			return str.strip()
	
	def extractDataFromNamedRow(self,ROW,row_name):
		if not row_name == ROW[0]:
			return None
		else:
			return self.prepareDatum(ROW[1])
	
	def reportDuplicates(self,a_list):
		assert type([]) == a_list
		assert not 0 == len(a_list)
		
		e2c = defaultdict(int)
		for e in a_list:
			e2c[e] += 1
		del e
		
		return [e for e in e2c if e2c[e] > 1]
	
	def extractAllDataFromNamedRows(self,relevant_non_ontology_row_names,txt_sheet_name):
		#################################################
		try:
			assert len(relevant_non_ontology_row_names) == len(set(relevant_non_ontology_row_names)), "Duplicates in relevant_non_ontology_row_names???"
		except AssertionError,err_msg:
			print err_msg
			print self.reportDuplicates(relevant_non_ontology_row_names)
			sys.exit(1)
		###############################################
		
		rows = self.extractRows(txt_sheet_name)
		assert not 0 == len(rows)
		
		for row_name in relevant_non_ontology_row_names:
			try:
				value_in_here = [self.extractDataFromNamedRow(ROW,row_name) for ROW in rows]
				del ROW
				value_in_here = [part for part in value_in_here if not part is None]
				del part
				assert 1 == len(value_in_here), "%d rows with the following name were found:%s" % (len(value_in_here),row_name)
				
				if '' == value_in_here[0]:
					row_value = None
				else:
					row_value = value_in_here[0]
				del value_in_here
				
				self.dataDict[self.idTxtSheetType(txt_sheet_name)][row_name] = row_value
				del row_value
			except Exception,err_msg:
				print err_msg
				print 'Error encountered when trying to get data for this row name:',row_name
				sys.exit(1)
	
	def extractData_from_Material_sheet(self,txt_sheet_name):
		assert 'NBI Material' == self.idTxtSheetType(txt_sheet_name), "%s is NOT a NBI Material sheet!" % txt_sheet_name
		print '-'*50
		print 'Extracting data from this NBI Material sheet:',txt_sheet_name
		
		###############################################
		relevant_non_ontology_row_names = ['NBI Material Identifier'] #<TO DO>:UPDATE CODE TO EXTRACT ONTOLOGY DETAILS IN THE FUTURE
		relevant_non_ontology_row_names.append('Particle Descriptor')
		relevant_non_ontology_row_names.append('Investigator / Material Data Contributor: Name')
		relevant_non_ontology_row_names.append('Investigator / Material Data Contributor: Affiliation')
		relevant_non_ontology_row_names.append('Investigator / Material Data Contributor: Email')
		relevant_non_ontology_row_names.append('Material Type')
		relevant_non_ontology_row_names.append('Manufacture Date')
		relevant_non_ontology_row_names.append('Manufacturer')
		relevant_non_ontology_row_names.append('Synthesis Process')
		relevant_non_ontology_row_names.append('Synthesis Precursors')
		relevant_non_ontology_row_names.append('Purity')
		relevant_non_ontology_row_names.append('Types of Impurities')
		#relevant_non_ontology_row_names.append('Primary Particle / Material Core Data:') #<TO DO?>: CONSIDER SUB-DIVIDING self.dataDict structure
		relevant_non_ontology_row_names.append('Primary Particle Size: Avg. (nm)')
		relevant_non_ontology_row_names.append('Primary Particle Size: Min. (nm)')
		relevant_non_ontology_row_names.append('Primary Particle Size: Max (nm)')
		relevant_non_ontology_row_names.append('Method of Size Measurement')
		relevant_non_ontology_row_names.append('Instrument Used for Size Measurement')
		relevant_non_ontology_row_names.append('Core Shape')
		relevant_non_ontology_row_names.append('Core Structure')
		relevant_non_ontology_row_names.append('Crystal Structure')
		relevant_non_ontology_row_names.append('Core Atomic Composition')
		relevant_non_ontology_row_names.append('Number of Core Atoms')
		relevant_non_ontology_row_names.append('Mass Core Atoms (ng)')
		#relevant_non_ontology_row_names.append('Core Shell / Coating (if present):') 
		relevant_non_ontology_row_names.append('Shell Composition')
		relevant_non_ontology_row_names.append('Shell Surface Shape')
		relevant_non_ontology_row_names.append('Shell Linkage')
		#relevant_non_ontology_row_names.append('Surface Linkages / Ligands (if present):')
		relevant_non_ontology_row_names.append('Outermost Surface Functional Groups')
		relevant_non_ontology_row_names.append('Surface Chemistry Linkage Group / Type')
		relevant_non_ontology_row_names.append('Density of Surface Covered with Ligands (%)')
		relevant_non_ontology_row_names.append('Minimum Number of Ligands')
		relevant_non_ontology_row_names.append('Maximum Nunber of Ligands')
		#relevant_non_ontology_row_names.append('Complete Material:')
		relevant_non_ontology_row_names.append('Mass of Core + Shell + Linkages and Ligands (ng)')
		relevant_non_ontology_row_names.append('Surface Area (Core + Shell + Ligands) (mm2)')
		relevant_non_ontology_row_names.append('Method Used to Determine Surface Area')
		relevant_non_ontology_row_names.append('Surface Charge: (positive, negative, neutral)')
		relevant_non_ontology_row_names.append('Surface Charge: Value')
		relevant_non_ontology_row_names.append('Surface Charge: Method')
		relevant_non_ontology_row_names.append('Redox Potential (volts)')
		relevant_non_ontology_row_names.append('Solubility / Dispersity Medium')
		relevant_non_ontology_row_names.append('Maximum Solubility Amount (ppm)')
		relevant_non_ontology_row_names.append('Solubility Reference Temperature (Celsius)')
		relevant_non_ontology_row_names.append('Hydrophilic')
		relevant_non_ontology_row_names.append('Lipophilic')
		relevant_non_ontology_row_names.append('Stability of Dispersions')
		relevant_non_ontology_row_names.append('Publication Authors')
		relevant_non_ontology_row_names.append('Publication Year')
		relevant_non_ontology_row_names.append('Publication Journal')
		relevant_non_ontology_row_names.append('Publication Title')
		relevant_non_ontology_row_names.append('Publication DOI')
		###############################################
		
		self.extractAllDataFromNamedRows(relevant_non_ontology_row_names,txt_sheet_name)
		
		print '-'*50
	
	def extractData_from_EMZexperiDesign_sheet(self,txt_sheet_name):
		assert 'NBI-EMZ Exp. Design' == self.idTxtSheetType(txt_sheet_name), "%s is NOT a NBI-EMZ Exp. Design sheet!" % txt_sheet_name
		print '-'*50
		print 'Extracting data from this EMZ Exp. Design sheet:',txt_sheet_name
		
		###############################################
		relevant_non_ontology_row_names = ['NBI Experiment ID'] #<TO DO>:UPDATE CODE TO EXTRACT ONTOLOGY DETAILS IN THE FUTURE
		relevant_non_ontology_row_names.append('NBI Material Identifier')
		relevant_non_ontology_row_names.append('Exposure Metric / Assay')
		relevant_non_ontology_row_names.append('Primary Exposure Route')
		relevant_non_ontology_row_names.append('Primary Exposure Delivery')
		relevant_non_ontology_row_names.append('Secondary Exposure Route')
		relevant_non_ontology_row_names.append('Secondary Exposure Delivery')
		relevant_non_ontology_row_names.append('Tertiary Exposure Route')
		relevant_non_ontology_row_names.append('Tertiary Exposure Delivery')
		relevant_non_ontology_row_names.append('Study Factor(s)') #<Q.><IS THIS A SECTION HEADER?><TO DO?>: CONSIDER SUB-DIVIDING self.dataDict structure
		relevant_non_ontology_row_names.append('Exposure Organism')
		relevant_non_ontology_row_names.append('Exposure Organism Life stage')
		relevant_non_ontology_row_names.append('Exposure Length Classification')
		relevant_non_ontology_row_names.append('Duration of Exposure (hours)')
		relevant_non_ontology_row_names.append('Investigation Title')
		relevant_non_ontology_row_names.append('Investigation Description')
		relevant_non_ontology_row_names.append('Investigator Name')
		relevant_non_ontology_row_names.append('Investigator Affiliation')
		relevant_non_ontology_row_names.append('Investigator Email')
		relevant_non_ontology_row_names.append('Study Start Date')
		relevant_non_ontology_row_names.append('Exposure Organism Gender')
		relevant_non_ontology_row_names.append('Exposure Organism Average Weight (mg)')
		relevant_non_ontology_row_names.append('Exposure Organism Initial Age (hours post-fertilization at start of exposure)')
		relevant_non_ontology_row_names.append('Continuity of Exposure')
		relevant_non_ontology_row_names.append('Exposure Temperature (Celsius)')
		relevant_non_ontology_row_names.append('Exposure Media')
		relevant_non_ontology_row_names.append('Media Composition')
		relevant_non_ontology_row_names.append('Media pH')
		relevant_non_ontology_row_names.append('Material Zeta Potential in Media (mV)')
		relevant_non_ontology_row_names.append('Stable Average Agglomerate Size in Media (nm)')
		relevant_non_ontology_row_names.append('Stable Agglomerate Size in Media Minimum (nm)')
		relevant_non_ontology_row_names.append('Stable Agglomerate Size in Media Maximum (nm)')
		relevant_non_ontology_row_names.append('Nanomaterial Preparation')
		relevant_non_ontology_row_names.append('Experimental Notes')
		relevant_non_ontology_row_names.append('LC50 (ppm)')
		relevant_non_ontology_row_names.append('NOAEL (ppm)')
		relevant_non_ontology_row_names.append('Weighted EZ Metric EC50 (ppm)')
		relevant_non_ontology_row_names.append('Additive EZ Metric EC50 (ppm)')
		relevant_non_ontology_row_names.append('Publication Authors')
		relevant_non_ontology_row_names.append('Publication Year')
		relevant_non_ontology_row_names.append('Publication Journal')
		relevant_non_ontology_row_names.append('Publication Title')
		relevant_non_ontology_row_names.append('Publication DOI')
		###############################################
		
		self.extractAllDataFromNamedRows(relevant_non_ontology_row_names,txt_sheet_name)
		
		print '-'*50
	
	def idEMZdataMainTitlesRow(self,rows):
		foundMainTitlesRow = False
		
		row_index = 0
		
		for ROW in rows:
			if 'Dosage Concentrations Used (ppm)' == ROW[0]:
				assert not foundMainTitlesRow , "Found EMZ Data 'main titles row' for the second time???"
				main_titles_row_index = row_index
				foundMainTitlesRow = True
			row_index += 1
		
		assert foundMainTitlesRow , "EMZ Data 'main titles row' was never found???"
		
		return main_titles_row_index
	
	def idEMZdataMaxDosageConcRow(self,main_titles_row_index,rows):
		
		start_row_index = (main_titles_row_index+2)
		
		row_index = start_row_index
		for ROW in rows[start_row_index:]:
			if not type(1.0) == type(self.prepareDatum(ROW[0])):
				max_dc_row_index = (row_index-1) #<TO DO?>:SEE IF THIS CAN BE UPDATED AS THIS WOULD FAIL IF THERE WERE EMPTY DOSAGE CONCENTRATION COLUMN ENTRIES [BUT THIS IS NOT VERY LIKELY TO HAPPEN???]
				break
			row_index += 1
		
		return max_dc_row_index
	
	def idEMZdataHpfCols(self,main_titles_row_index,rows):
		hpf_ROW = rows[(main_titles_row_index-1)]
		
		
		for col_index in range(0,len(hpf_ROW)):
			if '24 hpf evaluation' == self.prepareDatum(hpf_ROW[col_index]):
				hpf_24_col_index = col_index
			elif '120 hpf evaluation' == self.prepareDatum(hpf_ROW[col_index]):
				hpf_120_col_index = col_index
			else:
				assert '' == self.prepareDatum(hpf_ROW[col_index]), "Unexpected entry in 'hpf row' (index:%d):%s" % ((main_titles_row_index-1),hpf_ROW[col_index])
		
		assert hpf_24_col_index < hpf_120_col_index #required for def matchEMZdataColId2ExperiVarName(self,main_titles_row_index,hpf_24_col_index,hpf_120_col_index,rows):
		
		return hpf_24_col_index,hpf_120_col_index
	
	def matchEMZdataColId2ExperiVarName(self,main_titles_row_index,hpf_24_col_index,hpf_120_col_index,rows):
		
		colId2ExperiVarName = {}
		
		for col_index in range(0,len(rows[main_titles_row_index])): #col_index values should be consistent across all rows!
			if col_index < hpf_24_col_index:
				colId2ExperiVarName[col_index] = self.prepareDatum(rows[main_titles_row_index][col_index])
			else:
				if col_index < hpf_120_col_index:
					hpf_qualifier = self.prepareDatum(rows[(main_titles_row_index-1)][hpf_24_col_index])
				else:
					hpf_qualifier = self.prepareDatum(rows[(main_titles_row_index-1)][hpf_120_col_index])
				
				if '' == self.prepareDatum(rows[main_titles_row_index][col_index]):
					if not 'no' == self.prepareDatum(rows[(main_titles_row_index+1)][col_index]):
						break #we've reached the end of the data columns!
					else:
						assert not '' == self.prepareDatum(rows[main_titles_row_index][(col_index-1)]), "Unexpected column: index=%d,main titles row value=%s,main titles row *preceding column* value=%s" % (col_index,rows[main_titles_row_index][col_index],rows[main_titles_row_index][(col_index-1)])
						
						colId2ExperiVarName[col_index] = '%s_%s_no' % (hpf_qualifier,self.prepareDatum(rows[main_titles_row_index][(col_index-1)]))
				else:
					assert 'yes' == self.prepareDatum(rows[(main_titles_row_index+1)][col_index]), "Unexpected column: index=%d,main titles row value=%s" % (col_index,rows[main_titles_row_index][col_index])
					
					colId2ExperiVarName[col_index] = '%s_%s_yes' % (hpf_qualifier,self.prepareDatum(rows[main_titles_row_index][col_index]))
		
		col_ids = colId2ExperiVarName.keys()
		col_ids.sort()
		assert col_ids == range(0,len(rows[main_titles_row_index])), "Unexpected col_ids:%s" % str(col_ids)
		del col_ids
		
		
		return colId2ExperiVarName
	
	def matchEMZdataRowId2ExperiVarName2Value(self,max_dc_row_index,main_titles_row_index,hpf_24_col_index,hpf_120_col_index,rows):
		
		colId2ExperiVarName = self.matchEMZdataColId2ExperiVarName(main_titles_row_index,hpf_24_col_index,hpf_120_col_index,rows)
		
		rowId2experiVarName2Value = defaultdict(dict)
		
		for row_index in range((main_titles_row_index+2),(max_dc_row_index+1)):
			for col_index in range(0,len(rows[main_titles_row_index])): #col_index values should be consistent across all rows!
				
				assert type(1.0) == type(self.prepareDatum(rows[row_index][col_index])), "Non-numeric concentration/bioactivity in EMZ Data worksheet row %d, column %d:%s [N.B. main_titles_row_index=%d and max_dc_row_index=%d" % (row_index,col_index,rows[row_index][col_index],main_titles_row_index,max_dc_row_index) #potentially, this could fail if there was missing data....
				
				rowId2experiVarName2Value[row_index][colId2ExperiVarName[col_index]] = self.prepareDatum(rows[row_index][col_index])
		
		return rowId2experiVarName2Value
	
	def extractData_from_EMZdata_sheet(self,txt_sheet_name):
		assert 'NBI-EMZ Data' == self.idTxtSheetType(txt_sheet_name), "%s is NOT a NBI-EMZ Data sheet!" % txt_sheet_name
		print '-'*50
		print 'Extracting data from this NBI-EMZ Data sheet:',txt_sheet_name
		
		rows = self.extractRows(txt_sheet_name)
		assert not 0 == len(rows)
		
		main_titles_row_index = self.idEMZdataMainTitlesRow(rows)
		max_dc_row_index = self.idEMZdataMaxDosageConcRow(main_titles_row_index,rows)
		hpf_24_col_index,hpf_120_col_index = self.idEMZdataHpfCols(main_titles_row_index,rows)
		
		
		self.dataDict[self.idTxtSheetType(txt_sheet_name)] = self.matchEMZdataRowId2ExperiVarName2Value(max_dc_row_index,main_titles_row_index,hpf_24_col_index,hpf_120_col_index,rows) #<TO DO?>:USE DOSAGE CONCENTRATION VALUES AS KEYS RATHER THAN row IDs
		
		if 'nbi_1.xls' == self.nbi_xls_file.split(delimiter())[-1]:#<TO DO?>:ASSUME THE SAME NUMBER OF DOSAGE CONCENTRATIONS ARE ALWAYS TESTED AND ALWAYS APPLY THIS TEST
			print 'Checking self.dataDict[%s] entry against expected number of evaluated dosage concentrations for nbi_1.xls' % self.idTxtSheetType(txt_sheet_name)
			assert 8 == len(self.dataDict[self.idTxtSheetType(txt_sheet_name)].keys()), "len(self.dataDict[self.idTxtSheetType(txt_sheet_name)].keys())=%d???" % len(self.dataDict[self.idTxtSheetType(txt_sheet_name)].keys())
		
		print '-'*50
	
	def extractData(self):
		
		self.convert2TxtSheets()
		
		for txt_sheet_name in self.txt_sheets:
			type = self.idTxtSheetType(txt_sheet_name)
			
			if 'NBI Material' == type:
				self.extractData_from_Material_sheet(txt_sheet_name)
			elif  'NBI-EMZ Exp. Design' == type:
				self.extractData_from_EMZexperiDesign_sheet(txt_sheet_name)
			elif 'NBI-EMZ Data' == type:
				self.extractData_from_EMZdata_sheet(txt_sheet_name)
			else:
				print 'Unrecognised sheet type %s for %s' % (type,txt_sheet_name)
				sys.exit(1)
	
	def cleanUp(self):
		print 'Deleting text files used to read data into instance of NBIrecord() class'
		for file in self.txt_sheets:
			assert os.path.isfile(file), r"self.txt_sheets entry %s is not a file???" % file
			os.remove(file)
		del file
		print 'Deleting pyc files in the directory of this module file (os.path.abspath(__file__) will not work once .py compiled to .pyc!)'
		for file in glob.glob(r'%s%s*pyc' % (dir_of_this_file,delimiter())):
			os.remove(file)

def main():
	cleanUp = False
	#====================
	opts,args = getopt.getopt(sys.argv[1:],'ci:',['cleanUp=True','input_file='])
	
	for o,v in opts:
		if '-i' == o:
			input_file = r'%s' % re.sub('"','',v)
		if '-c' == o:
			cleanUp = True
	#=====================
	
	anNBIrecord = NBIrecord(input_file)
	anNBIrecord.extractData()
	
	print 'File parsed:',anNBIrecord.nbi_xls_file
	print 'txt_sheets:',anNBIrecord.txt_sheets
	print 'data contents:',anNBIrecord.dataDict
	if cleanUp:
		anNBIrecord.cleanUp()
	
	return 0

if __name__ == '__main__':
	sys.exit(main())


