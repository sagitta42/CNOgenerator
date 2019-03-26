from math import ceil

#----------------------------------------------------------

## ENTER YOUR CHOICES HERE

# total number of fits
NFITS = 5
# number of fits per one submission file
NBATCH = 2
# path to the input root files
INPUT = 'Sensitivity_Tests_Mariia'

#----------------------------------------------------------

import sys
from creator import * 

#----------------------------------------------------------

def generator(metal, inj, fit, var):
	'''
	0) metal: metallicity (hz or lz)
	1) inj: injected CNO (1 or 0)
	2) fit: how to fit CNO (fixed or free)
	3) var: energy variable (npmts_dt1, npmts_dt2 or nhits)
	'''


#	metal = arg[0]
#	inj = arg[1]
#	fit = arg[2]
#	var = arg[3]

	## ---------------------------------
	## technical checks

	if not metal in ['hz','lz']:
		print '\nOptions for metallicity: hz or lz\n'
		return

	if not inj in ['0','1']:
		print '\nOptions for CNO injected: 1 or 0\n'
		return

	if not fit in ['fixed','free']:
		print '\nOptions for CNO fit: fixed or free\n'
		return

	## for now ignore nhits
	if not var in ['npmts_dt1', 'npmts_dt2']:
		print '\nOptions for energy variable: npmts_dt1 or npmts_dt2 (nhits NOT implemented)\n'
		return


	## ---------------------------------

	## init
	s = Submission(metal, inj, fit, var, NFITS)
	
	print # readability
	print '#######################################'
	print
	
	## folder for given configuration (for submission files and output log file folder)
	outfolder_exists = s.output()

	if(outfolder_exists):
		print
		print '#######################################'
		return
	
	
	## main .sh fit files: split 10000 fits into files of 500 fits (-> 20 files)
	## also batch files (in parallel)
	s.fitfiles(NBATCH, INPUT)
	
	## output folder for the log files
	s.logfiles()

	print # readability
	
	## corresponding cfg file
	if not os.path.exists('fitoptions'):
		os.mkdir('fitoptions')
	
	s.cfgfile() # create cfg file if needed

	## corresponding species list
	if not os.path.exists('species_list'):
		os.mkdir('species_list')

	s.iccfile() # create species list if needed

	print #readability
	print '#######################################'
	print



if __name__ == '__main__':
	params = sys.argv[1:]
	
	if len(params) != 4:
		print
		print 'Example: python generator.py hz 0 free npmts_dt1'
		print
		sys.exit(1)

	generator(*params)
