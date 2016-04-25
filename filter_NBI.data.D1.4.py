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

import sys,re,getopt
from collections import defaultdict
import itertools
sys.path.append('parsing.data.utils')
from misc_utils import *
import filter_data_matrix

loel_based_input_file = 'NBIconcIndLoelData_s0.050000.csv'
conc_dep_input_file = 'NBIconcDepDataForModelling_s0.050000.csv' #filtering should be carried out consistently!
ID_key = 'NBI Material Identifier'

######################################################
############Manually specified filtering details######
######################################################
threshold = 60 #columns with fewer than this number of 'non-missing' entries in the LOEL data input should be removed...


# #ids_to_ignore were identified as follows: 
# #<N.B.>:<REMEMBER: IF UPDATING OF ids_to_ignore BASED UPON bioCondition2InconsistentIDs and pcMeasurementDetails2InconsistentIDs IS COMMENTED OUT => IT WAS UNCLEAR EXACTLY WHICH NM RECORDS WERE ASSOCIATED WITH SUFFICIENTLY INCONSISTENT EXPERIMENTAL DETAILS TO WARRANT THEIR BEING EXCLUDED!>
ids_to_ignore = []

# bioCondition2InconsistentIDs = defaultdict(list) #N.B. The biological test conditions considered below were identified via inspecting nbi_1.xls 'NBI-EMZ Exp. Design' worksheet and manually identifying those fields which were understood to correspond to biological test conditions
# #based on manually inspecting NBIconcIndData.csv, IDs associated with inconsistent/unspecified values for the following biological test conditions were identified:
# bioCondition2InconsistentIDs['Primary Exposure Route'] = ['16.0'] #'inhalation' vs. 'dermal' #does inconsistency in this actually matter, as this might not indicate experimental protocol inconsistency as opposed to a different in vivo mechanism of action? <TO DO>: GO OVER THIS POINT
# bioCondition2InconsistentIDs['Primary Exposure Delivery'] = [] #all 'waterborne'
# bioCondition2InconsistentIDs['Secondary Exposure Route'] = ['16.0','178.0','186.0','182.0','108.0','111.0'] #these were unspecified, as opposed to 'oral'#does inconsistency in this actually matter, as this might not indicate experimental protocol inconsistency as opposed to a different in vivo mechanism of action? <TO DO>: GO OVER THIS POINT
# bioCondition2InconsistentIDs['Secondary Exposure Delivery'] = ['16.0','178.0','186.0','182.0','108.0','111.0'] #these were all blank, rather than 'waterborne' #can we assume that unspecified experimental conditions are consistent??? <TO DO>: GO OVER THIS POINT
# bioCondition2InconsistentIDs['Tertiary Exposure Route'] = [] #all blank
# bioCondition2InconsistentIDs['Tertiary Exposure Delivery'] = [] #all blank
# bioCondition2InconsistentIDs['Exposure Organism'] = [] #all 'zebrafish'
# bioCondition2InconsistentIDs['Exposure Organism Life stage'] = [] #all 'embryo'
# bioCondition2InconsistentIDs['Exposure Length Classification'] = [] #majority of these are blank, vs. 'sub-chronic' => decided not to exclude IDs based on (possible) discrepancies here!
# bioCondition2InconsistentIDs['Duration of Exposure (hours)'] = ['155.0','153.0','178.0','185.0','150.0','156.0','149.0','154.0','147.0','152.0','151.0','157.0','158.0','148.0'] #these IDs were associated with either missing values (178.0) or 114 or 120 hours vs. 112 hours for the remaining NMs
# bioCondition2InconsistentIDs['Exposure Organism Gender'] = [] #all 'mixed'
# bioCondition2InconsistentIDs['Exposure Organism Average Weight (mg)'] = [] #all '1' or '1 mg'
# bioCondition2InconsistentIDs['Exposure Organism Initial Age (hours post-fertilization at start of exposure)'] = ['155.0','161.0','153.0','171.0','173.0','185.0','160.0','150.0','156.0','149.0','154.0','174.0','147.0','159.0','152.0','151.0','157.0','170.0','158.0','172.0','148.0'] #these IDs were 6 (185.0) or 7 as opposed to 8
# bioCondition2InconsistentIDs['Continuity of Exposure'] = [] #all 'Continuous'
# bioCondition2InconsistentIDs['Exposure Temperature (Celsius)'] = [] #all between 23-27 OR blank: I am going to assume that this means all experiments were carried out at "room temperature" and the observed variations do not matter! #<TO DO?>:REVISIT THIS DECISION
# bioCondition2InconsistentIDs['Exposure Media'] = [] #all 'fish water' or 'Fishwater'
# bioCondition2InconsistentIDs['Media Composition'] = [] #around 39 blank and remainder '0.1 Instant Ocean Salts'. I am *assuming* that these details may, in fact, all be consistent! #<TO DO?>:REVISIT THIS DECISION
# bioCondition2InconsistentIDs['Media pH'] = [] #all between 7-7.2 OR blank: I am going to assume that this means all experiments were carried out at "physiological pH" and the observed variations do not matter! #<TO DO?>:REVISIT THIS DECISION
# bioCondition2InconsistentIDs['Nanomaterial Preparation'] = [] #most (89) blank - but the remaining entries seem highly inconsistent (i.e. described different kinds of sonication, vortexing or stirring to varying degrees of detail) *For now, I cannot decide which entries should be excluded??? #<TO DO?>:REVISIT THIS DECISION

# #ids_to_ignore += list(set(list(itertools.chain(*[bioCondition2InconsistentIDs[key] for key in bioCondition2InconsistentIDs]))))
# #del key

# pcMeasurementDetails2InconsistentIDs = defaultdict(list) #N.B. The PC assessment methods considered below were identified via inspecting nbi_1.xls 'NBI Material' worksheet and manually identifying those fields which were understood to correspond to PC assessment methods
# #based on manually inspecting NBIconcIndData.csv, IDs associated with inconsistent/unspecified values for the following PC assessment methods were identified:
# pcMeasurementDetails2InconsistentIDs['Method of Size Measurement'] = [] #a majority of entries are blank, the remaining entries indicate considerable inconsistency! I cannot afford to throw away such a significant amount of data??? #<TO DO?>:REVISIT THIS DECISION
# pcMeasurementDetails2InconsistentIDs['Instrument Used for Size Measurement'] = [] #almost all entries are blank and the meaning of 2 out of the 3 remaining entries ('as reported') is not clear!
# pcMeasurementDetails2InconsistentIDs['Method Used to Determine Surface Area'] = [] #these entries are all blank, except in one case; also, since the 'Surface Area (Core + Shell + Ligands) (mm2)' (only other column referring to surface area) is only provided in two cases, this column is largely irrelevant
# pcMeasurementDetails2InconsistentIDs['Surface Charge: Method'] = [] #all entries are blank
# pcMeasurementDetails2InconsistentIDs['Solubility Reference Temperature (Celsius)'] = [] #all but three entries are blank [these three entries are all = 25]


#ids_to_ignore += list(set(list(itertools.chain(*[pcMeasurementDetails2InconsistentIDs[key] for key in pcMeasurementDetails2InconsistentIDs]))))
#del key

print 'ids_to_ignore=',ids_to_ignore

#initial columns_to_delete (which are supplemented in main(...)) were identified as follows:
columns_to_delete = []

#columns_to_delete += (pcMeasurementDetails2InconsistentIDs.keys()+bioCondition2InconsistentIDs.keys()) #based on manual inspection of nbi_1.xls 'NBI Material' and'NBI-EMZ Exp. Design' worksheets (see above). these were not considered to be relevant descriptors of NMs (as opposed to experimental details/metadata) which could be used for grouping
columns_to_delete += ['Exposure Metric / Assay','Study Factor(s)','Exposure Length Classification'] #based on manual inspection of NBIconcIndData.csv. These columns do not seem to contain any relevant entries
columns_to_delete += ['Nanomaterial Preparation','Experimental Notes','Types of Impurities','Synthesis Process','Purity','Particle Descriptor']#based on manual inspection of NBIconcIndData.csv. These columns seem to contain 'too difficult to standardise' free text entries #<N.B.>: Excluding 'Types of Impurities' from analysis may not be a problem as (1) majority (101/114) of entries are blank, (2) non-endotoxin containing/assessed entries indicate > 99% pure #<TO DO?>:CONSIDER WHETHER THE ENDOTOXIN CONTAINING ENTRIES SHOULD BE ADDED TO THE ids_to_ignore list???
#columns_to_delete += ['Primary Particle Size: Min. (nm)','Primary Particle Size: Max (nm)'] #the removal of these columns was simply designed to try and get a larger final dataset (due to eventual removal of any rows with missing values)!


cols_for_which_missing_values_ok = []


####################################################

def getLOELdataFileIDs(loel_data_file,ID_key):
	rows = getCSVdictRows(csv_file=loel_data_file)
	
	IDs = [ROW[ID_key] for ROW in rows]
	del ROW
	assert len(IDs) == len(set(IDs))
	
	return IDs

def main():
	global columns_to_delete
	global ids_to_ignore
	global loel_based_input_file
	global conc_dep_input_file
	global threshold
	
	############################
	opts,args = getopt.getopt(sys.argv[1:],'l:c:t:',['loel_based_input_file=','conc_dep_input_file=','threshold='])
	
	for o,v in opts:
		if '-l' == o:
			loel_based_input_file = v
		if '-c' == o:
			conc_dep_input_file = v
		if '-t' == o:
			threshold = int(v)
	
	print '='*50
	print 'Options:'
	print 'loel_based_input_file=',loel_based_input_file
	print 'conc_dep_input_file=',conc_dep_input_file
	print 'threshold=',threshold
	print '='*50
	############################
	
	print 'THE START'
	
	filter_data_matrix.reportNumberOfNonMissingEntriesPerColumn(input_file=loel_based_input_file)
	
	print '='*50
	print 'Filtering ',loel_based_input_file
	columns_with_no_entries = filter_data_matrix.findColumnsWithLessThanXentries(loel_based_input_file,x=1)
	
	print 'columns_with_no_entries=',columns_with_no_entries
	
	columns_to_delete += [col for col in columns_with_no_entries if not col in cols_for_which_missing_values_ok]
	try:
		del col
	except NameError:
		pass
	
	columns_with_too_few_entries = filter_data_matrix.findColumnsWithLessThanXentries(loel_based_input_file,x=threshold)
	
	print 'columns_with_too_few_entries (less than %d)=' % threshold,columns_with_too_few_entries
	
	columns_to_delete += [col for col in columns_with_too_few_entries if not col in cols_for_which_missing_values_ok]
	try:
		del col
	except NameError:
		pass
	
	columns_with_constant_entries = filter_data_matrix.findColumnsWithConstantEntries(loel_based_input_file) #N.B. Text-data normalisation is required for this to work properly (e.g. in raw NBI data, "Exposure Organism Average Weight (mg)" is reported as "1" and "1 mg")
	
	print 'columns_with_constant_entries=',columns_with_constant_entries
	
	columns_to_delete += [col for col in columns_with_constant_entries if not 'Set' == col] #'Set' is a column inserted as expected by the clustering script
	del col
	
	columns_to_delete = list(set(columns_to_delete))
	
	filtered_loel_based_input_file = loel_based_input_file
	
	filtered_loel_based_input_file = filter_data_matrix.dropPredefinedColumns(filtered_loel_based_input_file,columns_to_delete)
	
	filtered_loel_based_input_file = filter_data_matrix.dropPredefinedRows(filtered_loel_based_input_file,id_col_title=ID_key,forbidden_ids=ids_to_ignore)
	
	filtered_loel_based_input_file = filter_data_matrix.dropIncompleteRows(filtered_loel_based_input_file,cols_for_which_missing_values_ok)
	
	columns_to_delete += [col for col in filter_data_matrix.findColumnsWithConstantEntries(filtered_loel_based_input_file) if not 'Set' == col]#'Set' is a column inserted as expected by the clustering script
	del col
	
	columns_to_delete = list(set(columns_to_delete))
	
	print 'columns_to_delete=',columns_to_delete
	
	filtered_loel_based_input_file = filter_data_matrix.dropPredefinedColumns(filtered_loel_based_input_file,columns_to_delete)
	
	print 'FILTERED ',loel_based_input_file
	print '='*50
	
	print '='*50
	print 'Consistently filtering ',conc_dep_input_file
	
	columns_to_delete = [re.sub('(_loel)','',col) for col in columns_to_delete]
	del col
	
	print 'columns_to_delete=',columns_to_delete
	
	IDs_in_filtered_loel_data = getLOELdataFileIDs(filtered_loel_based_input_file,ID_key)
	
	IDs_in_original_loel_data = getLOELdataFileIDs(loel_based_input_file,ID_key)
	
	ids_to_ignore += [ID for ID in IDs_in_original_loel_data if not ID in IDs_in_filtered_loel_data]
	del ID
	ids_to_ignore = list(set(ids_to_ignore))
	
	print 'ids_to_ignore=',ids_to_ignore
	
	filtered_conc_dep_input_file = conc_dep_input_file
	
	filtered_conc_dep_input_file = filter_data_matrix.dropPredefinedRows(filtered_conc_dep_input_file,id_col_title=ID_key,forbidden_ids=ids_to_ignore)
	
	#filter_data_matrix.dropPredefinedColumns(filtered_conc_dep_input_file,columns_to_delete)
	
	print 'Consistently FILTERED ',conc_dep_input_file
	print '='*50
	
	print 'THE END'
	
	return 0 

if __name__ == '__main__':
	sys.exit(main())

