import os

class Submission():
	def __init__(self, metal, inj, fit, var):
		self.metal = metal
		self.inj = inj
		self.fit = fit
		self.var = var
		
		## corr. fitoptions and species lists filenames
		self.cfgname = 'fitoptions/fitoptions_' + metal + '_' + inj + '_' + var + '.cfg'
		self.iccname = 'species_list/species_' + fit + '.icc'
		
		## corr. histograms inside of the input file
		self.cnofolder = metal + '_cno_' + inj # e.g. hz_cno_1
		self.cnohisto = 'cno_' + metal + '_' + inj
		
		## folder for everything related to the given configuration
		self.outfolder = 'fit_' + metal + '_' + inj + '_cno_' + fit + '_' + var 
		## folder for the output log files
		self.logfolder = 'logs_' + self.metal + '_' + self.inj + '_cno_' + self.fit + '_' + self.var
		## our fit filename: "core" name, will have 20 of these each one 500 fits; name of the folder
		self.fitfolder = 'fits_' + metal + '_' + inj + '_' + 'cno_' + fit + '_' + var
		self.batchfolder = 'sbatch_' + metal + '_' + inj + '_' + 'cno_' + fit + '_' + var
		

	def output(self):
		# do not create if already exists
		if os.path.exists(self.outfolder):
			print 'Folder', self.outfolder, 'already exists!'
			return True
			
		os.mkdir(self.outfolder) # create output folder
		print 'Folder for given fit parameters setup:', self.outfolder + '/'
		return False
		
		
	def fitfiles(self):
		''' Create .sh fit files for given parameters (20 files) '''
	
		# folder to store the fitfiles
		os.mkdir(self.outfolder + '/' + self.fitfolder)
		print '|'
		print ' - Subfolder for fit files:', self.fitfolder + '/'
		print '|\t(', self.fitfolder + '_X.sh, X = 0..20 )'
		print '|\t( each fit = 500 lines)'

		# folder to store the batch files
		os.mkdir(self.outfolder + '/' + self.batchfolder)
		print '|'
		print ' - Subfolder with corr. batch files:', self.batchfolder + '/'
		print '|\t(', self.batchfolder + '_X.sh, X = 0..20 )'
		print '|\t( each submission = 1 fit*.sh )'
		
		# for now instead of 10 000 use 100, not 500 per file but 5 (20 files)
		fitfile = open('.temp','w') # dummy
		
		for i in range(100):
			findex = int(i / 5)
			# will be accessed in self.batch()
			self.fitname = self.fitfolder + '_' + str(findex) + '.sh'
			
			## every 5 files do:
			if(i % 5 == 0):
				fitfile.close()
				fitfile = open(self.outfolder + '/' + self.fitfolder + '/' + self.fitname, 'w')
				# the first 4 lines are the same
				print >> fitfile, '#!/bin/bash'
				print >> fitfile, 'BASE="../../../build_separate_noOMP"'
				print >> fitfile, 'EXEC="${BASE}/examples/spectralfit/src/spectralfitter"'
				## add to batch file (when we hit a new findex)
				self.batch(findex)
	
			# the 5th line is the one that will be copied many times for each input file
			inputname = 'some_path/Sen_' + str(i) + '.root'
			logname = 'sen_' + str(i) + '_' + self.metal + '_' + self.inj + '_' + 'cno_' + self.fit + '_' + self.var + '.log'
			
			print >> fitfile, '$EXEC', inputname, self.cnofolder + '/TFC_sub/Hsub_' + self.cnohisto + '_0_' + self.var, '../../' + self.cfgname, '../../' + self.iccname, '2>&1 | tee', '../' + self.logfolder + '/' + logname

	
	def cfgfile(self):
		''' Create a fitoptions file corresponding to the given configuration (if needed) '''
			## name of the cfg file
		print 'Fitoptions:', self.cfgname
		
		## if file already exists, do nothing
		if os.path.exists(self.cfgname):
			return
			
		## otherwise generate from a template
		cfglines = open('templates/fitoptions_template.cfg').readlines()
		
		# line 3: fit variable --> always npmts? not npmts_dt1 or dt2?
		# cfglines[2] = 'fit_variable = ' + var
		
		# line 13: fit variable MC (?)
		# do nothing for now
		
		# line 82: user data
		cfglines[81] = 'user_data_hist_name = ' + self.cnofolder + '/User_Data/user_data_' + self.cnohisto  + '_0_' + self.var + '\n'
		
		# line 83: user ref
		cfglines[82] = 'user_ref_hist_name = multivariate/multivariate_lkl_%d_' + self.var + '\n'
		
		# line 90: complementary histo
		cfglines[89] = 'complementary_histo_name = ' + self.cnofolder + '/TFC_tagged/Htag_' + self.cnohisto + '_0_' + self.var + '\n'
		
		# line 91: r dist
		cfglines[90] = 'rdist_data_hist_name = ' + self.cnofolder + '/Rdist_Data/rdist_data_' + self.cnohisto + '_0_' + self.var + '\n'
		
		# line 92: rdist ref
		cfglines[91] = 'rdist_ref_hist_name = multivariate/multivariate_rdist_%d_' + self.var + '\n'
		
		## save file
		outfile = open(self.cfgname, 'w')
		outfile.writelines(cfglines)
		outfile.close()
		print '\tcreator.py: cfgfile : generated'


	def iccfile(self):
		''' Create a species list corresponding to the given configuration (if needed) '''
		print 'Species list:', self.iccname
		## if file already exists, do nothing
			
		if os.path.exists(self.iccname):
			return
			
		## otherwise generate from a template
		icclines = open('templates/species_list_template.icc').readlines()

		# line 21: cno fixed or free
		icclines[20] = CNOICC[self.fit]
		
		## save file
		outfile = open(self.iccname, 'w')
		outfile.writelines(icclines)
		outfile.close()
		print '\tcreator.py: iccfile : generated'



	def logfiles(self):
		''' Create output folder for the log files '''
		os.mkdir(self.outfolder + '/' + self.logfolder)
		print '|'
		print ' - Subfolder for future log files:', self.logfolder + '/'
		print '|\t( sen_X_' + self.metal + '_' + self.inj + '_' + 'cno_' + self.fit + '_' + self.var + '.log, X = 0..10000 )'


	def batch(self, findex):
		''' Create jureca batch submission files '''
			
		batchname = self.outfolder + '/' + self.batchfolder + '/' + self.batchfolder + '_' + str(findex) + '.sh'
		batchfile = open(batchname, 'w')

		## batch file template
		sublines = open('templates/sbatch_submission_template.sh').readlines()
		
		# last line: our fit
		sublines[-1] = 'srun ../' + self.fitfolder + '/' + self.fitname
		
		## save
		batchfile.writelines(sublines)
		batchfile.close()



CNOICC = {'fixed': '   { "nu(CNO)",      -1,   kCyan,   kSolid,  2,    0.,   "fixed", 0.,  50. },\n',
            'free': '{ "nu(CNO)",      -1,   kCyan,   kSolid,  2,    5.36,   "free", 0.,  50. },\n'}
