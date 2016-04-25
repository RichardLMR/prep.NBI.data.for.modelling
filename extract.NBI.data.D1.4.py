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

This script extracts data from the nbi_<number>.xls files exported from the NBI Knowledgebase database (http://nbi.oregonstate.edu/) kindly provided in April 2014 by Dr Stacey Harper and Bryan Harper.
It then writes this data to one of two versions (concentration independent OR concentration dependent data) of a single text file for subsequent analysis for the purpose of deliverable D1.4 within the EU project NanoPUZZLES (http://www.nanopuzzles.eu/).
N.B. (1) Some records may not be parsed correctly by this script [due to their structure deviating from what was expected]: the identity of these records will be written to a separate csv output file.
N.B. (2) This script depends upon the "NBIparser" code (NBIrecordParse.py and associated "utils" and "tests"), which should be located in a subdirectory of the directory containing this script called "NBIparser".
[Further information about the NBI Knowledgebase can be found in the following publications: 
(1)Liu et al. 2013 http://dx.doi.org/10.2147/IJN.S40742; (2)Tang et al. 2013 http://dx.doi.org/10.2147/IJN.S40974; (3) Harper et al. 2008 http://dx.doi.org/10.1504/IJNT.2008.016552]
'''
###################################
###############Imports#############
###################################
import os,sys,re,glob,getopt,time,csv,logging
from collections import defaultdict
import functools,itertools
sys.path.append('parsing.data.utils')
from misc_utils import getCSVfileTitlesInOrder,getCSVdictRows,writeCSVoutput
sys.path.append('NBIparser')
from NBIrecordParser import NBIrecord
cwd = os.getcwd()
os.chdir('NBIparser')
#print os.getcwd()
sys.path.append('utils')
from os_ind_delimiter import delimiter
os.chdir(cwd)
del cwd
####################
#The following module was downloaded from https://gist.github.com/jeetsukumaran/2189099#file-fishers_exact_test-py (12/08/14)
####################
import fishers_exact_test
###################################
###############Key globals#########
###################################
#----------------------------------
debug = False
#----------------------------------
conc_dep_raw_output_file = 'NBIrawConcDepData.csv'
conc_dep_modelling_input = 'NBIconcDepDataForModelling.csv'
loel_based_output_file = 'NBIconcIndLoelData.csv'
ok_file = 'NBIokRecords.csv' #summarises records used to generate con_dep_output_file/loel_based_output_file
rejects_file = 'NBIproblemRecords.csv'
#****************************************
nmLocation2ID = {'NBI Material':'NBI Material Identifier','NBI-EMZ Exp. Design':'NBI Material Identifier'}
#****************************************
#****************************************
commonTitle2Location = {}
commonTitle2Location['Particle Descriptor'] = 'NBI Material'
commonTitle2Location['Material Type']='NBI Material'
commonTitle2Location['Synthesis Process']='NBI Material'
commonTitle2Location['Synthesis Precursors']='NBI Material'
commonTitle2Location['Purity']='NBI Material'
commonTitle2Location['Types of Impurities']='NBI Material'
commonTitle2Location['Primary Particle Size: Avg. (nm)']='NBI Material'
commonTitle2Location['Primary Particle Size: Min. (nm)']='NBI Material'
commonTitle2Location['Primary Particle Size: Max (nm)']='NBI Material'
commonTitle2Location['Method of Size Measurement']='NBI Material'
commonTitle2Location['Instrument Used for Size Measurement']='NBI Material'
commonTitle2Location['Core Shape']='NBI Material'
commonTitle2Location['Core Structure']='NBI Material'
commonTitle2Location['Crystal Structure']='NBI Material'
commonTitle2Location['Core Atomic Composition']='NBI Material'
commonTitle2Location['Number of Core Atoms']='NBI Material'
commonTitle2Location['Mass Core Atoms (ng)']='NBI Material'
commonTitle2Location['Shell Composition']='NBI Material'
commonTitle2Location['Shell Surface Shape']='NBI Material'
commonTitle2Location['Shell Linkage']='NBI Material'
commonTitle2Location['Outermost Surface Functional Groups']='NBI Material'
commonTitle2Location['Surface Chemistry Linkage Group / Type']='NBI Material'
commonTitle2Location['Density of Surface Covered with Ligands (%)']='NBI Material'
commonTitle2Location['Minimum Number of Ligands']='NBI Material'
commonTitle2Location['Maximum Nunber of Ligands']='NBI Material'
commonTitle2Location['Mass of Core + Shell + Linkages and Ligands (ng)']='NBI Material'
commonTitle2Location['Surface Area (Core + Shell + Ligands) (mm2)']='NBI Material'
commonTitle2Location['Method Used to Determine Surface Area']='NBI Material'
commonTitle2Location['Surface Charge: (positive, negative, neutral)']='NBI Material'
commonTitle2Location['Surface Charge: Value']='NBI Material'
commonTitle2Location['Surface Charge: Method']='NBI Material'
commonTitle2Location['Redox Potential (volts)']='NBI Material'
commonTitle2Location['Solubility / Dispersity Medium']='NBI Material'
commonTitle2Location['Maximum Solubility Amount (ppm)']='NBI Material'
commonTitle2Location['Solubility Reference Temperature (Celsius)']='NBI Material'
commonTitle2Location['Hydrophilic']='NBI Material'
commonTitle2Location['Lipophilic']='NBI Material'
commonTitle2Location['Stability of Dispersions']='NBI Material'
commonTitle2Location['Exposure Metric / Assay']='NBI-EMZ Exp. Design'
commonTitle2Location['Primary Exposure Route']='NBI-EMZ Exp. Design'
commonTitle2Location['Primary Exposure Delivery']='NBI-EMZ Exp. Design'
commonTitle2Location['Secondary Exposure Route']='NBI-EMZ Exp. Design'
commonTitle2Location['Secondary Exposure Delivery']='NBI-EMZ Exp. Design'
commonTitle2Location['Tertiary Exposure Route']='NBI-EMZ Exp. Design'
commonTitle2Location['Tertiary Exposure Delivery']='NBI-EMZ Exp. Design'
commonTitle2Location['Study Factor(s)']='NBI-EMZ Exp. Design'
commonTitle2Location['Exposure Organism']='NBI-EMZ Exp. Design'
commonTitle2Location['Exposure Organism Life stage']='NBI-EMZ Exp. Design'
commonTitle2Location['Exposure Length Classification']='NBI-EMZ Exp. Design'
commonTitle2Location['Duration of Exposure (hours)']='NBI-EMZ Exp. Design'
commonTitle2Location['Exposure Organism Gender']='NBI-EMZ Exp. Design'
commonTitle2Location['Exposure Organism Average Weight (mg)']='NBI-EMZ Exp. Design'
commonTitle2Location['Exposure Organism Initial Age (hours post-fertilization at start of exposure)']='NBI-EMZ Exp. Design'
commonTitle2Location['Continuity of Exposure']='NBI-EMZ Exp. Design'
commonTitle2Location['Exposure Temperature (Celsius)']='NBI-EMZ Exp. Design'
commonTitle2Location['Exposure Media']='NBI-EMZ Exp. Design'
commonTitle2Location['Media Composition']='NBI-EMZ Exp. Design'
commonTitle2Location['Media pH']='NBI-EMZ Exp. Design'
commonTitle2Location['Material Zeta Potential in Media (mV)']='NBI-EMZ Exp. Design'
commonTitle2Location['Stable Average Agglomerate Size in Media (nm)']='NBI-EMZ Exp. Design'
commonTitle2Location['Stable Agglomerate Size in Media Minimum (nm)']='NBI-EMZ Exp. Design'
commonTitle2Location['Stable Agglomerate Size in Media Maximum (nm)']='NBI-EMZ Exp. Design'
commonTitle2Location['Nanomaterial Preparation']='NBI-EMZ Exp. Design'
commonTitle2Location['Experimental Notes']='NBI-EMZ Exp. Design'
#****************************************
# concIndTitle2Location = {}
# concIndTitle2Location['LC50 (ppm)']='NBI-EMZ Exp. Design'
# concIndTitle2Location['NOAEL (ppm)']='NBI-EMZ Exp. Design'
# concIndTitle2Location['Weighted EZ Metric EC50 (ppm)']='NBI-EMZ Exp. Design'
# concIndTitle2Location['Additive EZ Metric EC50 (ppm)']='NBI-EMZ Exp. Design'
#****************************************
#****************************************
concDepTitle2Location = {}
concDepTitle2Location['Dosage Concentrations Used (ppm)']='NBI-EMZ Data'
#concDepTitle2Location['Weighted EZ Metric Score']='NBI-EMZ Data'
#concDepTitle2Location['Additive EZ Metric Score']='NBI-EMZ Data'
#****************************************
expected_number_of_doses = 8
#****************************************
effect_specific_regex = re.compile('([0-9]+ hpf evaluation_[a-z]+_)',re.IGNORECASE)
examples_to_check_effect_specific_regex = ['120 hpf evaluation_So_yes','24 hpf evaluation_M_yes','120 hpf evaluation_PF_yes']
for example in examples_to_check_effect_specific_regex:
	assert effect_specific_regex.search(example), "%s???" % example
	assert 'yes' == effect_specific_regex.sub('',example), "%s???" % example
del example,examples_to_check_effect_specific_regex
#****************************************
default_sig_tresh = 0.05 #for LOEL calculations; p-values less than this => significantly greater effect than control
pvalue_column_suffix = '_vsZeroPvalue'
loel_column_suffix = '_loel'
#****************************
ID_key = list(set(nmLocation2ID.values()))[0]
dose_key = 'Dosage Concentrations Used (ppm)'
#****************************
default_loel = 100000.0 #chosen to be ('much') greater than the largest observed dose concentration
####################################

def writeRecordsFile(recording_rejects,records_list):
	if recording_rejects:
		file_name = rejects_file
	else:
		file_name = ok_file
	f_out = open(file_name,'wb')
	try:
		for file in records_list:
			f_out.write(file+'\r\n')
	finally:
		f_out.close()
		del f_out

def getConcDepEffectSpecificTitles(anNBIrecord_dataDict,effect_specific_regex):
	effect_specific_titles = []
	
	new_suffix = 'effect'
	
	for key in anNBIrecord_dataDict['NBI-EMZ Data'][anNBIrecord_dataDict['NBI-EMZ Data'].keys()[0]]:
		if effect_specific_regex.search(key):
			old_suffix = effect_specific_regex.sub('',key)
			assert 'yes' == old_suffix or 'no' == old_suffix, "key=%s,old_suffix=%s???" % (key,old_suffix)
			effect_specific_titles.append('%s%s' % (re.sub('(%s)' % old_suffix,'',key),new_suffix))
	effect_specific_titles = list(set(effect_specific_titles))
	
	return effect_specific_titles

def getSpecificEffectPrefix(specific_effect_title):
	return re.sub('(_effect)','',specific_effect_title) #c.f. def getConcDepEffectSpecificTitles(anNBIrecord_dataDict,effect_specific_regex):

def getConcDepTitles(anNBIrecord_dataDict,commonTitle2Location,concDepTitle2Location,effect_specific_regex,nmLocation2ID):
	
	titles = list(set(nmLocation2ID.values())) 
	assert 1 == len(titles), "titles (after just adding NM ID title!)=%s???" % str(titles)
	titles += commonTitle2Location.keys()
	
	titles += concDepTitle2Location.keys()
	titles += getConcDepEffectSpecificTitles(anNBIrecord_dataDict,effect_specific_regex)
	
	if debug:
		######################
		##########Debug#######
		######################
		print 'titles=',titles
		######################
	
	return titles

def readID(anNBIrecord_dataDict,TITLE,nmLocation2ID):
	possible_ids = []
	for sheet in nmLocation2ID.keys():
		possible_ids.append(anNBIrecord_dataDict[sheet][TITLE])
	assert 1 == len(set(possible_ids)),"Inconsistent IDs:%s" % str(possible_ids)
	
	return {TITLE:possible_ids[0]}

def readConcIndValues(anNBIrecord_dataDict,TITLE,locationDict):
	##########################
	#This function is for reading concentration independent values directly, as opposed to calculating them as will be required for biological effect specific LOELs!
	#########################
	
	assert not 'NBI-EMZ Data' == locationDict[TITLE]
	
	return {TITLE:anNBIrecord_dataDict[locationDict[TITLE]][TITLE]}


def calculateEffect(yes_counts,no_counts):
	#13/08/14: Only change to generation of conc_dep_raw_output_file (since extract.NBI.data (6).zip version checked) was the following change to this function
	
	#effect = yes_counts/(yes_counts+no_counts) #c.f. Liu et al. 2013. I think this is correct? <TO DO>:DOUBLE CHECK
	
	for counts in [yes_counts,no_counts]:
		assert int(counts) == float(counts) #This should catch values which are not integers
	del counts
	
	effect = "y:%d;n:%d" % (yes_counts,no_counts)
	
	return effect

def getAllConcDepRowValues(anNBIrecord_dataDict,titles,concDepTitle2Location,effect_specific_regex):
	
	sheet = concDepTitle2Location['Dosage Concentrations Used (ppm)']
	
	all_rows_allConcDepTitles2Values = []
	
	for row_number in anNBIrecord_dataDict[sheet].keys():
		allConcDepTitles2Values = {}
		
		for TITLE in titles:
			if not effect_specific_regex.search(TITLE):
				allConcDepTitles2Values[TITLE] = anNBIrecord_dataDict[sheet][row_number][TITLE]
			else:
				specific_effect_prefix = getSpecificEffectPrefix(specific_effect_title=TITLE)
				allConcDepTitles2Values[TITLE] = calculateEffect(yes_counts=anNBIrecord_dataDict[sheet][row_number]['%s_yes' % specific_effect_prefix],no_counts=anNBIrecord_dataDict[sheet][row_number]['%s_no' % specific_effect_prefix])
		
		all_rows_allConcDepTitles2Values.append(allConcDepTitles2Values)
	
	return all_rows_allConcDepTitles2Values

def getRowEntries(anNBIrecord_dataDict,titles,commonTitle2Location,concDepTitle2Location,effect_specific_regex,nmLocation2ID):
	
	rows = [] #this must be a list of dictionaries [each matching entries in titles:row values]
	
	commonTitles2Values = {}
	
	possible_ID_titles = [TITLE for TITLE in titles if TITLE==nmLocation2ID.values()[0]]
	assert 1==len(possible_ID_titles),"possible_ID_titles=%s???" % str(possible_ID_titles)
	del TITLE
	
	commonTitles2Values.update(readID(anNBIrecord_dataDict,possible_ID_titles[0],nmLocation2ID))
	
	for TITLE in titles:
		if TITLE in commonTitle2Location:
			commonTitles2Values.update(readConcIndValues(anNBIrecord_dataDict,TITLE,locationDict=commonTitle2Location))
	del TITLE
	
	remaining_titles = [TITLE for TITLE in titles if not TITLE in commonTitles2Values.keys()]
	del TITLE
	assert not 0 == len(remaining_titles)
	
	
	all_rows_allConcDepTitles2Values = getAllConcDepRowValues(anNBIrecord_dataDict,remaining_titles,concDepTitle2Location,effect_specific_regex)
	
	for rowEntriesDict in all_rows_allConcDepTitles2Values:
		finalRowDict = {}
		finalRowDict.update(commonTitles2Values)
		finalRowDict.update(rowEntriesDict)
		rows.append(finalRowDict)
		
		if debug:
			############################
			########Debug###############
			############################
			print 'finalRowDict=',finalRowDict
			############################
	
	return rows

def processData(anNBIrecord_dataDict,conc_dep_titles,commonTitle2Location,concDepTitle2Location,effect_specific_regex,nmLocation2ID):
	
	if conc_dep_titles is None:
		create_new_files = True
		conc_dep_titles = getConcDepTitles(anNBIrecord_dataDict,commonTitle2Location,concDepTitle2Location,effect_specific_regex,nmLocation2ID)
	else:
		create_new_files = False
	
	if debug:
		###########################
		#############Debug#########
		###########################
		print 'conc_dep_titles (which should have been generated via getConcDepTitles(...)=',conc_dep_titles
		#print 'conc_ind_titles (which should have been generated via getConcDepTitles(...)=',conc_ind_titles
		###########################
	
	if debug:
		###########################
		#############Debug#########
		###########################
		print 'current titles (which should have been generated via getConcDepTitles(...)=',conc_dep_titles
		###########################
	
	if create_new_files:
		f_out = open(conc_dep_raw_output_file,'wb')
		try:
			writer = csv.DictWriter(f_out,fieldnames=conc_dep_titles,delimiter=',',quotechar='"')
			try:
				writer.writerow(dict(zip(conc_dep_titles,conc_dep_titles)))
			finally:
				del writer
		finally:
			f_out.close()
			del f_out
	f_out = open(conc_dep_raw_output_file,'ab')
	try:
		writer = csv.DictWriter(f_out,fieldnames=conc_dep_titles,delimiter=',',quotechar='"')
		try:
			rows = getRowEntries(anNBIrecord_dataDict,conc_dep_titles,commonTitle2Location,concDepTitle2Location,effect_specific_regex,nmLocation2ID)
			for ROW in rows:
				writer.writerow(ROW)
			del ROW
			del rows
		finally:
			del writer
	finally:
		f_out.close()
		del f_out
	
	
	
	return conc_dep_titles

def getConc2Effect(ID_key,dose_key,ID,effect,all_lines):
	
	relevant_lines = [line for line in all_lines if ID == line[ID_key]]
	del line
	
	conc2Effect = {}
	
	for line in relevant_lines:
		conc2Effect[float(line[dose_key])] = line[effect]
	
	assert len(relevant_lines) == len(conc2Effect.keys()), "Duplicated concentrations???"
	
	return conc2Effect

def effectLabel2YNcounts(effect_label):
	#structure of an effect label should match the return value from def calculateEffect(yes_counts,no_counts):"y:%f;n:%f"
	
	y = int(effect_label.split("y:")[1].split(";")[0]) #ValueError expected to be raised if string does not correspond to an *integer*
	
	n = int(effect_label.split("n:")[1])
	
	return y,n 

def getZeroDoseComparisonPValue(zero_dose_effect,dose_effect):
	
	zero_dose_y,zero_dose_n = effectLabel2YNcounts(zero_dose_effect)
	
	dose_y,dose_n = effectLabel2YNcounts(dose_effect)
	
	table = [[dose_y,zero_dose_y],[dose_n,zero_dose_n]] #construction of table like this and choice of fishers_exact_test.FishersExactTest(table).left_tail_p() based on www.sheffield.ac.uk/polopoly_fs/1.43998!/file/tutorial-9-fishers.pdf [13/08/14] 
	
	pos_association_pvalue = fishers_exact_test.FishersExactTest(table).left_tail_p() #alternative hypothesis: effect with non-zero dose is genuinely greater than effect with zero dose
	
	return pos_association_pvalue

def getConc2PValue(ID_key,dose_key,ID,effect,all_lines):
	
	print '#'*50
	print 'Obtaining conc2Pvalue for ID=%s,effect=%s' % (ID,effect)
	print '#'*50
	
	conc2Effect = getConc2Effect(ID_key,dose_key,ID,effect,all_lines)
	
	concentrations = conc2Effect.keys()
	concentrations.sort()
	
	try:
		assert 0.0 == concentrations[0],"concentrations[0]=%f" % concentrations[0]
		
		conc2PValue = {}
		conc2PValue[0.0] = None
		
		
		for conc in concentrations[1:]:
			conc2PValue[conc] = getZeroDoseComparisonPValue(zero_dose_effect=conc2Effect[0.0],dose_effect=conc2Effect[conc])
	except AssertionError,e:
		logging.exception(e)
		del e
		conc2PValue = dict(zip(concentrations,[None]*len(concentrations)))
	
	return conc2PValue

def addZeroDoseComparisonPValues(conc_dep_raw_output_file,ok_list,ID_key,dose_key):
	assert re.search('(\.csv$)',conc_dep_raw_output_file),"conc_dep_raw_output_file=%s???" % conc_dep_raw_output_file
	new_output = re.sub('(\.csv$)','_plus.pvalues.csv',conc_dep_raw_output_file)
	
	f_in = open(conc_dep_raw_output_file,'rb')
	try:
		reader = csv.DictReader(f_in,delimiter=',',quotechar='"')
		try:
			all_lines = [line for line in reader]
			del line
		finally:
			del reader
	finally:
		f_in.close()
		del f_in
	
	all_ids = list(set([line[ID_key] for line in all_lines]))
	del line
	#<CHECK THAT ALL IDs [ASSOCIATED WITH DIFFERENT NBI RECORDS] ARE UNIQUE!>
	assert len(all_ids) == len(ok_list), "len(all_ids)=%d,len(ok_list)=%d???" % (len(all_ids),len(ok_list))
	
	bio_effects = [TITLE for TITLE in getCSVfileTitlesInOrder(csv_file=conc_dep_raw_output_file) if effect_specific_regex.search(TITLE)]
	del TITLE
	
	id2Effect2conc2PValue = defaultdict(functools.partial(defaultdict,dict))
	
	for ID in all_ids:
		for effect in bio_effects:
			id2Effect2conc2PValue[ID][effect] = getConc2PValue(ID_key,dose_key,ID,effect,all_lines)
	del effect
	del ID
	del all_ids
	
	new_titles = getCSVfileTitlesInOrder(csv_file=conc_dep_raw_output_file)+[effect+pvalue_column_suffix for effect in bio_effects]
	del effect
	assert len(new_titles) == len(set(new_titles)),"addZeroDoseComparisonPValues(...):new_titles not unique:%s???" % str(new_titles)
	
	f_out = open(new_output,'wb')
	try:
		try:
			writer = csv.DictWriter(f_out,fieldnames=new_titles,delimiter=',',quotechar='"')
			writer.writerow(dict(zip(new_titles,new_titles)))
			
			for line in all_lines:
				#====================================================================
				assert float(line[dose_key]) < default_loel,"ID=%s;concentration=%s???" % (line[ID_key],line[dose_key])
				#====================================================================
				assert type({}) == type(line), "type(line)=%s???" % type(line)
				
				e2p = {}
				for effect in bio_effects:
					e2p[effect+pvalue_column_suffix] = id2Effect2conc2PValue[line[ID_key]][effect][float(line[dose_key])]
				
				line.update(e2p)
				
				del e2p
				
				writer.writerow(line)
				
		finally:
			del writer
	finally:
		f_out.close()
		del f_out
	
	return new_output

def supplementNBIdata(integrated_nbi_data_csv):
	##################
	supplement_col_title = 'NBI Data Supplement Description'
	assert re.search('(\.csv$)',integrated_nbi_data_csv),"integrated_nbi_data_csv to be supplemented=%s???" % integrated_nbi_data_csv
	new_file = re.sub('(\.csv$)','_supp.csv',integrated_nbi_data_csv)
	assert not new_file == integrated_nbi_data_csv, "new_file=integrated_nbi_data_csv to be supplemented=%s???" % integrated_nbi_data_csv
	##################
	
	rows = getCSVdictRows(integrated_nbi_data_csv)
	
	new_titles = getCSVfileTitlesInOrder(integrated_nbi_data_csv)
	
	new_titles += [supplement_col_title]
	
	#This field is just required for clustering script
	new_titles += ['Set']
	
	#*******************************
	#Add expected "Core Atomic Composition" value
	for ROW in rows:
		if not ROW['NBI Material Identifier'] in ['135.0','133.0','134.0','132.0']:
			ROW[supplement_col_title] = None
		else:
			ROW[supplement_col_title] = '"Core Atomic Composition" updated to "Lead Sulfide"'
			ROW["Core Atomic Composition"] = "Lead Sulfide"
		
		#======================================
		#This field is just required for clustering script
		ROW['Set'] = 'TRAIN'
		#======================================
	del ROW
	#*******************************
	
	writeCSVoutput(new_csv_file=new_file,data=rows,output_columns=new_titles)
	
	return new_file

def normaliseNBIdata(integrated_nbi_data_csv):
	##################
	assert re.search('(\.csv$)',integrated_nbi_data_csv),"integrated_nbi_data_csv to be normalised=%s???" % integrated_nbi_data_csv
	new_file = re.sub('(\.csv$)','_norm.csv',integrated_nbi_data_csv)
	assert not new_file == integrated_nbi_data_csv, "new_file=integrated_nbi_data_csv to be normalised=%s???" % integrated_nbi_data_csv
	##################
	
	rows = getCSVdictRows(integrated_nbi_data_csv)
	
	new_titles = getCSVfileTitlesInOrder(integrated_nbi_data_csv)
	
	
	
	#*******************************
	#=======================================
	collectionOfNonUniversallyApplicableFields = {} #*N.B.* We are *assuming* that these field values might be set to '', rather than  'none' in some cases AND that a combination of 'none'  and '' values means the '' values are genuine missing values!
	collectionOfNonUniversallyApplicableFields['Core Shell / Coating (if present):'] = ['Shell Composition','Shell Surface Shape','Shell Linkage']
	collectionOfNonUniversallyApplicableFields['Surface Linkages / Ligands (if present):'] = ['Outermost Surface Functional Groups','Surface Chemistry Linkage Group / Type','Density of Surface Covered with Ligands (%)','Minimum Number of Ligands','Maximum Nunber of Ligands']
	#=======================================
	
	#=======================================
	#Text based normalisation based on manual observations
	field2NonStandardValuesThenStandardValue = {} #field2NonStandardValuesThenStandardValue[field] = [tuple_1,tuple_2,...]; each tuple: (list_of_non_standard_values,standard_value)
	field2NonStandardValuesThenStandardValue["Exposure Organism Average Weight (mg)"] = [(['1 mg'],'1.0')]
	field2NonStandardValuesThenStandardValue['Exposure Media'] = [(['Fishwater','fishwater'],'fish water')]
	field2NonStandardValuesThenStandardValue['Core Atomic Composition'] = [(['europium (iii) oxide [eu2o3]'],'europium oxide [eu2o3]')]
	#=======================================
	
	#=======================================
	listOfgenericNonStandardValuesThenStandardValue = [(['na'],'none')]
	#========================================
	
	new_rows = []
	
	for ROW in rows:
		#=======================================
		for field in field2NonStandardValuesThenStandardValue:
			for combination in field2NonStandardValuesThenStandardValue[field]:
				#--------------
				assert type([]) == type(combination[0]),'field=%s;list_of_non_standard_values=%s?' % (field,str(combination[0]))
				assert type('x') == type(combination[1]),'field=%s;standard_value=%s?' % (field,str(combination[1]))
				assert not combination[1] in combination[0],'field=%s;list_of_non_standard_values=%s;standard_value=%s?' % (field,str(combination[0]),combination[1])
				#-------------
				if ROW[field] in combination[0]:
					ROW[field] = combination[1]
				#else:
				#	assert field2NonStandardValuesThenStandardValue[field][1] == ROW[field], "Unexpected %s=%s" % (field,ROW[field])
			del combination
		del field
		#=======================================
		
		#=======================================
		for combination in listOfgenericNonStandardValuesThenStandardValue:
			#-------------------
			assert type(combination) == type(('a','b')),"combination=%s?" % str(combination)
			assert type(combination[0]) == type([]),"combination=%s?" % str(combination)
			assert type(combination[1]) == type('a'),"combination=%s?" % str(combination)
			assert not combination[1] in combination[0],"combination=%s?" % str(combination)
			#-------------------
			for field in ROW:
				if ROW[field] in combination[0]:
					ROW[field] = combination[1]
				#else:
				#	assert combination[1] == ROW[field], "Unexpected: %s=%s;combination=%s" % (field,ROW[field],str(combination))
			del field
		del combination
		#=======================================
		
		for field_collection in collectionOfNonUniversallyApplicableFields:
			number_of_blank_fields = len([field for field in collectionOfNonUniversallyApplicableFields[field_collection] if '' == ROW[field]])
			del field
			if number_of_blank_fields == len(collectionOfNonUniversallyApplicableFields[field_collection]):
				for field in collectionOfNonUniversallyApplicableFields[field_collection]:
					ROW[field] = 'none'
				del field
		del field_collection
		#=======================================
		
		new_rows.append(ROW)
	del ROW
	del rows
	#*******************************
	
	writeCSVoutput(new_csv_file=new_file,data=new_rows,output_columns=new_titles)
	
	return new_file

def evaluateTestedDoses(nbi_conc_dep_data_file,ID_key,dose_key,expected_number_of_doses,filter=True):
	###############
	if filter:
		assert re.search('(\.csv$)',nbi_conc_dep_data_file),"nbi_conc_dep_data_file=%s???" % nbi_conc_dep_data_file
		new_data_file = re.sub('(\.csv$)','_doseBasedFilt.csv',nbi_conc_dep_data_file)
		assert not new_data_file == nbi_conc_dep_data_file,"new_data_file=nbi_conc_dep_data_file=%s???" % nbi_conc_dep_data_file
	else:
		new_data_file = nbi_conc_dep_data_file
	dose_seqs_record = 'doseSequencesRecord.csv'
	##############
	
	rows = getCSVdictRows(nbi_conc_dep_data_file)
	
	
	
	id2doses = defaultdict(list)
	id2rows = defaultdict(list)
	
	for ROW in rows:
		id2doses[ROW[ID_key]].append(float(ROW[dose_key]))
		id2rows[ROW[ID_key]].append(ROW)
	del ROW,rows
	
	id2ZeroDoseMissing = defaultdict(bool)
	id2UnexpectedNoDoses = defaultdict(bool)
	
	f_out = open(dose_seqs_record,'wb')
	try:
		f_out.write('ID,doses,ZeroDoseMissing,UnexpectedNoDoses\n')
		for ID in id2doses:
			id2doses[ID].sort()
			if not 0.0 == id2doses[ID][0]:
				id2ZeroDoseMissing[ID] = True
			if not expected_number_of_doses == len(id2doses[ID]):
				id2UnexpectedNoDoses[ID] = True
			f_out.write('%s,%s,%s,%s\n' % (ID,";".join([str(v) for v in id2doses[ID]]),str(id2ZeroDoseMissing[ID]),str(id2UnexpectedNoDoses[ID])))
		del ID
	finally:
		f_out.close()
		del f_out
	
	if filter:
		titles = getCSVfileTitlesInOrder(nbi_conc_dep_data_file)
		
		rows = list(itertools.chain(*[id2rows[ID] for ID in id2rows if not (id2ZeroDoseMissing[ID])]))# or id2UnexpectedNoDoses[ID]
		
		############
		#Debug:
		############
		if debug:
			print 'After filtering applied via evaluateTestedDoses(...):rows=',rows
		############
		
		writeCSVoutput(new_csv_file=new_data_file,data=rows,output_columns=titles)
	
	return new_data_file

def getNonZeroConc2PValue(ID_key,dose_key,ID,effect_pvalue_col_title,all_lines):
	
	relevant_lines = [line for line in all_lines if ID == line[ID_key]]
	del line
	
	nonZeroConc2PValue = {}
	
	for line in relevant_lines:
		if 0.0 == float(line[dose_key]):
			assert '' == line[effect_pvalue_col_title], "ID=%s,effect_pvalue_col_title=%s,line[dose_key]=%s,but line[effect_pvalue_col_title]=%s???" % (ID,effect_pvalue_col_title,line[dose_key],line[effect_pvalue_col_title])
		else:
			if not '' == line[effect_pvalue_col_title]: 
				nonZeroConc2PValue[float(line[dose_key])] = float(line[effect_pvalue_col_title])
			else:#c.f. def getConc2PValue(ID_key,dose_key,ID,effect,all_lines):, this is expected to happen when no zero concentration dosage was considered - this data cannot be used to derive a valid LOEL
				nonZeroConc2PValue = None
				break
	
	
	return nonZeroConc2PValue

def calculateLOEL(nonZeroConc2PValue,sig_thresh):
	
	concentrations = nonZeroConc2PValue.keys()
	concentrations.sort(reverse=True)
	
	#----------------------------
	for conc_index in range(0,len(concentrations)):
		if not conc_index == (len(concentrations)-1):
			assert concentrations[conc_index] > concentrations[(conc_index+1)]
	del conc_index
	assert not 0.0 in concentrations
	assert 0 == len([c for c in concentrations if not type(0.1)==type(c)])
	del c
	#----------------------------
	
	loel = None
	
	for conc_index in range(0,len(concentrations)):
		if nonZeroConc2PValue[concentrations[conc_index]] < sig_thresh:
			loel = concentrations[conc_index]
			if conc_index > 0:
				assert 0 == len([c_i for c_i in range(0,len(concentrations))[:conc_index] if not nonZeroConc2PValue[concentrations[c_i]] < sig_thresh]), "Not all concentrations above, or at LOEL, are associated with effects which are statistically significantly greater than the zero concentration effect???"
				del c_i
		else:
			break
	
	return loel

def getEffectSpecificLOEL(ID_key,dose_key,ID,effect_pvalue_col_title,all_lines,sig_thresh):
	nonZeroConc2PValue = getNonZeroConc2PValue(ID_key,dose_key,ID,effect_pvalue_col_title,all_lines)
	
	if nonZeroConc2PValue is None:
		return None
	else:
		return calculateLOEL(nonZeroConc2PValue,sig_thresh)

def findDuplicates(list_x):
	assert type([]) == type(list_x)
	
	e2c = defaultdict(int)
	
	for e in list_x:
		e2c[e] += 1
	del e
	
	return [e for e in e2c if e2c[e] > 1]

def check_findDuplicates():
	assert [] == findDuplicates(['b','a','c'])
	assert ['b'] == findDuplicates(['b','a','b','c'])

check_findDuplicates()

def convertToLOELdata(loel_based_output_file,pre_loel_output,sig_thresh,ID_key,dose_key):
	assert re.search('(\.csv$)',pre_loel_output),"pre_loel_output=%s???" % pre_loel_output
	assert re.search('(\.csv$)',loel_based_output_file),"loel_based_output_file=%s???" % loel_based_output_file
	
	f_in = open(pre_loel_output,'rb')
	try:
		reader = csv.DictReader(f_in,delimiter=",",quotechar='"')
		try:
			all_lines = [line for line in reader]
			del line
		finally:
			del reader
	finally:
		f_in.close()
		del f_in
	
	all_ids = list(set([line[ID_key] for line in all_lines]))
	del line
	
	
	bio_effect_pvalue_col_titles = [TITLE for TITLE in getCSVfileTitlesInOrder(csv_file=pre_loel_output) if re.search('(%s)' % pvalue_column_suffix,TITLE)]
	del TITLE
	
	bio_effect_loel_col_titles = []
	
	id2Effect2LOEL = defaultdict(dict)
	
	
	for effect_pvalue_col_title in bio_effect_pvalue_col_titles:
		
		effect_loel_col_title = re.sub('(%s)' % pvalue_column_suffix,loel_column_suffix,effect_pvalue_col_title)
		
		bio_effect_loel_col_titles.append(effect_loel_col_title)
		
		for ID in all_ids:
			id2Effect2LOEL[ID][effect_loel_col_title] = getEffectSpecificLOEL(ID_key,dose_key,ID,effect_pvalue_col_title,all_lines,sig_thresh)
	
	del effect_pvalue_col_title
	del effect_loel_col_title
	del ID
	del bio_effect_pvalue_col_titles
	
	new_titles = [TITLE for TITLE in getCSVfileTitlesInOrder(csv_file=pre_loel_output) if not effect_specific_regex.search(TITLE) and not dose_key == TITLE]
	del TITLE
	new_titles += bio_effect_loel_col_titles
	#del bio_effect_loel_col_titles
	
	try:
		assert len(new_titles) == len(set(new_titles)),"convertToLOELdata(...):new_titles not unique:%s???" % str(new_titles)
	except AssertionError,e:
		logging.exception(e)
		print 'Duplicated titles are ',findDuplicates(new_titles)
		sys.exit(1)
	
	extra_titles = [title for title in all_lines[0].keys() if not title in new_titles]
	del title
	
	f_out = open(loel_based_output_file,'wb')
	try:
		try:
			writer = csv.DictWriter(f_out,fieldnames=new_titles,delimiter=',',quotechar='"')
			writer.writerow(dict(zip(new_titles,new_titles)))
			
			for ID in all_ids:
				
				
				matching_lines = [line for line in all_lines if ID == line[ID_key]]
				del line
				assert not 0 == len(matching_lines),"convertToLOELdata(...):ID=%s,matching_lines=%s???" % (ID,str(matching_lines))
				line = matching_lines[0]
				del matching_lines
				assert type({}) == type(line), "type(line)=%s???" % type(line)
				
				line.update(id2Effect2LOEL[ID])
				
				#======================================
				#If no LOEL can be derived, set the LOEL to an arbitarily high dose concentration!
				for loel_col in bio_effect_loel_col_titles:
					if line[loel_col] is None:
						line[loel_col] = default_loel
				del loel_col
				#======================================
				
				for EXTRA_TITLE in extra_titles:
					del line[EXTRA_TITLE]
				del EXTRA_TITLE
				
				writer.writerow(line)
				
		finally:
			del writer
	finally:
		f_out.close()
		del f_out
	
	return id2Effect2LOEL

def getConcDepModellingInput(pre_loel_output,id2Effect2LOEL,dose_key,ID_key,sig_tresh):
	
	
	new_titles = getCSVfileTitlesInOrder(pre_loel_output)
	new_titles = [title for title in new_titles if not re.search('(%s)' % pvalue_column_suffix,title)]
	del title
	
	bio_effect_titles = [title for title in new_titles if effect_specific_regex.search(title)]
	del title
	
	rows = getCSVdictRows(pre_loel_output)
	
	new_rows = []
	
	for ROW in rows:
		if 0.0 == float(ROW[dose_key]):
			continue
		#******************************
		corresponding_zero_dose_row_candidates = [some_row for some_row in rows if some_row[ID_key] == ROW[ID_key] and 0.0 == float(some_row[dose_key])]
		del some_row
		assert 1 == len(corresponding_zero_dose_row_candidates), "ID=%s,corresponding_zero_dose_row_candidates=%s???" % (ROW[ID_key],str(corresponding_zero_dose_row_candidates))
		
		corresponding_zero_dose_row = corresponding_zero_dose_row_candidates[0]
		
		del corresponding_zero_dose_row_candidates
		#*********************************
		
		for bio_eff in bio_effect_titles:
			if id2Effect2LOEL[ROW[ID_key]][bio_eff+loel_column_suffix] is None:
				ROW[bio_eff] = 0.0
				del ROW[bio_eff+pvalue_column_suffix]
				continue
			if float(id2Effect2LOEL[ROW[ID_key]][bio_eff+loel_column_suffix]) > float(ROW[dose_key]):
				ROW[bio_eff] = 0.0
				del ROW[bio_eff+pvalue_column_suffix]
				continue
			
			assert float(ROW[bio_eff+pvalue_column_suffix]) < sig_tresh,"ID=%s,bio_eff=%s,P-VALUE=%f,sig_thresh=%f???" % (ROW[ID_key],bio_eff,float(ROW[bio_eff+pvalue_column_suffix]),sig_thresh)
			
			del ROW[bio_eff+pvalue_column_suffix]
			
			dose_y,dose_n = effectLabel2YNcounts(effect_label=ROW[bio_eff])
			
			try:
				provisional_dose_effect = float(dose_y)/(float(dose_y)+float(dose_n))
			except ZeroDivisionError:
				provisional_dose_effect = 0.0
				assert sig_tresh > 1, "An effect of zero can only be statistically significant if sig_thresh>1! ID=%s,bio_eff=%s,P-VALUE=%f,sig_thresh=%f???" % (ROW[ID_key],bio_eff,float(ROW[bio_eff+pvalue_column_suffix]),sig_thresh)
			
			zero_dose_y,zero_dose_n = effectLabel2YNcounts(effect_label=corresponding_zero_dose_row[bio_eff])
			
			
			try:
				zero_dose_effect = float(zero_dose_y)/(float(zero_dose_y)+float(zero_dose_n))
			except ZeroDivisionError:
				zero_dose_effect = 0.0
				print "#WARNING: this statistically significant dose effect may not be valid as no test subjects were in the corresponding control group! ID=%s,bio_eff=%s,P-VALUE=%f,sig_thresh=%f???" % (ROW[ID_key],bio_eff,float(ROW[bio_eff+pvalue_column_suffix]),sig_thresh)
			dose_effect = provisional_dose_effect - zero_dose_effect
			
			
			ROW[bio_eff] = str(dose_effect)
		
		new_rows.append(ROW)
	del ROW
	del rows
	
	writeCSVoutput(new_csv_file=conc_dep_modelling_input,data=new_rows,output_columns=new_titles)

def main():
	global debug
	global default_sig_tresh
	global conc_dep_modelling_input
	global loel_based_output_file
	
	print __doc__
	
	################
	opts,args = getopt.getopt(sys.argv[1:],'di:s:',['dir_with_nbi_records=','default_sig_tresh='])
	for o,v in opts:
		if '-d' == o:
			debug = True
		if '-i' == o:
			dir_with_nbi_records = r'%s' % re.sub('"','',v)
		if '-s' == o:
			default_sig_tresh = float(v)
	#################
	
	####################
	assert re.search('(\.csv$)',conc_dep_modelling_input),"conc_dep_modelling_input=%s?" % conc_dep_modelling_input
	conc_dep_modelling_input = re.sub('(\.csv$)','_s%f.csv' % default_sig_tresh,conc_dep_modelling_input)
	assert re.search('(\.csv$)',loel_based_output_file),"loel_based_output_file=%s?" % loel_based_output_file
	loel_based_output_file = re.sub('(\.csv$)','_s%f.csv' % default_sig_tresh,loel_based_output_file)
	####################
	
	print '='*50
	print 'Parsing NBI Knowledgebase records found in this directory:',dir_with_nbi_records
	print 'in order to generate %s' % conc_dep_raw_output_file
	print '(prior to generating %s and %s)' % (conc_dep_modelling_input,loel_based_output_file)
	start = time.clock()
	
	
	ok_list = []
	rejects_list = []
	
	conc_dep_titles = None
	
	for input_file in glob.glob(r'%s%snbi_*.xls' % (dir_with_nbi_records,delimiter())):
		print '#'*50
		anNBIrecord = NBIrecord(input_file)
		try:
			anNBIrecord.extractData()
			
			conc_dep_titles = processData(anNBIrecord.dataDict,conc_dep_titles,commonTitle2Location,concDepTitle2Location,effect_specific_regex,nmLocation2ID)
			
			ok_list.append(input_file.split(delimiter())[-1])
		except Exception,e:
			print '!'*50
			print 'Problem parsing this file: ',input_file
			logging.exception(e)
			del e
			rejects_list.append(input_file.split(delimiter())[-1])
			print '!'*50
		anNBIrecord.cleanUp()
		del anNBIrecord
		print '#'*50
	
	
	writeRecordsFile(recording_rejects=False,records_list=ok_list)
	writeRecordsFile(recording_rejects=True,records_list=rejects_list)
	
	print 'SUCCESSFULLY PARSED %d NBI Knowledgebase records found in this directory:' % len(ok_list),dir_with_nbi_records
	print 'in order to generate %s' % conc_dep_raw_output_file
	print '(prior to generating %s and %s)' % (conc_dep_modelling_input,loel_based_output_file)
	print 'PROBLEMS ENCOUNTERED WHEN PARSING %d NBI Knowledgebase records found in this directory:' % len(rejects_list),dir_with_nbi_records
	print '='*50
	
	pre_loel_output = addZeroDoseComparisonPValues(conc_dep_raw_output_file,ok_list,ID_key,dose_key)
	
	pre_loel_output = supplementNBIdata(integrated_nbi_data_csv=pre_loel_output)
	
	pre_loel_output = normaliseNBIdata(integrated_nbi_data_csv=pre_loel_output)
	
	pre_loel_output = evaluateTestedDoses(pre_loel_output,ID_key,dose_key,expected_number_of_doses,filter=True)
	
	id2Effect2LOEL = convertToLOELdata(loel_based_output_file,pre_loel_output,default_sig_tresh,ID_key,dose_key)
	
	getConcDepModellingInput(pre_loel_output,id2Effect2LOEL,dose_key,ID_key,default_sig_tresh)
	
	end = time.clock()
	print 'Total time taken = (roughly) %.f minutes.' % ((end-start)/60.0)
	
	return 0

if __name__ == '__main__':
	sys.exit(main())
