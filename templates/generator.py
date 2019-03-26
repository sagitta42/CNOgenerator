import sys

from creator import * # creating files

def generator(arg):
	'''
	0) metal: metallicity (hz or lz)
	1) inj: injected CNO (1 or 0)
	2) fit: how to fit CNO (fixed or free)
	3) var: energy variable (npmts_dt1, npmts_dt2 or nhits)
	'''

	if len(arg) != 4:
		print 'Example: python generator.py hz 0 free npmts_dt1'
		return

	metal = arg[0]
	inj = arg[1]
	fit = arg[2]
	var = arg[3]

	## ---------------------------------
	## technical checks

	if not metal in ['hz','lz']:
		print 'Options for metallicity: hz or lz'
		return

	if not inj in ['0','1']:
		print 'Options for CNO injected: 1 or 0'
		return

	if not fit in ['fixed','free']:
		print 'Options for CNO fit: fixed or free'
		return

	if not var in ['npmts_dt1', 'npmts_dt2', 'nhits']:
		print 'Options for energy variable: npmts_dt1, npmts_dt2 or nhits'
		return

	## for now ignore nhits
	if var == 'nhits':
		'Nhits not available now'
		return

	## ---------------------------------

	## init
	s = Submission(metal, inj, fit, var)
	print # readability
	print '#######################################'
	print
	
	## folder for given configuration (for submission files and output log file folder)
	outfolder_exists = s.output()

	if(outfolder_exists):
		return
	
	## main .sh fit files: split 10000 fits into files of 500 fits (-> 20 files)
	## also batch files (in parallel)
	s.fitfiles()
	
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






params = sys.argv[1:]
generator(params)
