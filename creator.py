import os
from math import ceil
import numpy as np
import random as rnd
rnd.seed(1)

class Submission():
    def __init__(self, metal, inj, fit, var, nfits_min, nfits_max, penalty, random, lst):
        '''
        metal (str): 'hz' or 'lz'
        inj (str): '1' or '0'
        fit (str): 'free' or 'fixed'
        var (str): 'npmts_dt1' or 'npmts_dt2'
        nfits_min, nfits_max (int): min and max number of the input files (e.g. from 0 to 10000, or 0 to 5000 etc)
        penalty (str): species to which penalty should be applied (currently only Bi210). Penalty defined in ICC at the bottom of this file
        random (list of str): species for which the mean is randomized for each fit (create separate species cc) (currently only Bi210)
        lst (str): path to list of input numbers (alternative to nfits_min and nfits_max)                              
        '''
        self.metal = metal
        self.inj = inj
        self.fit = fit
        self.var = var
        self.penalty = penalty # to be constrained
        self.random = random # penalty + randomized mean
        self.inpnums = range(nfits_min, nfits_max) if lst == 'none' else np.array(open(lst).readlines()).astype(int)
        
        ## corr. fitoptions and species lists filenames
        self.cfgname = 'fitoptions/fitoptions_' + metal + '_' + inj + '_' + var + '.cfg'
        pen = '' if self.penalty == 'none' else '_' + '-'.join(self.penalty) + '-penalty'
        penicc = '-' + self.metal if 'pp' in self.penalty else ''

        ran = '' if self.random == 'none' else '_' + '-'.join(self.random) + '-random'
        self.iccname = 'species_list/species_' + fit + pen + penicc + ran + '.icc'
        
        ## corr. histograms inside of the input file
        self.cnofolder = metal + '_cno_' + inj # e.g. hz_cno_1
        self.cnohisto = 'cno_' + metal + '_' + inj
        
        ## folder for everything related to the given configuration
        comboname = metal + '_' + inj + '_cno_' + fit + pen + ran + '_' + var
        self.outfolder = 'fit_' + comboname 
        ## subfolder for the output log files
        self.logfolder = 'logs_' + comboname
        ## subfolder for fit.sh files 
        self.fitfolder = 'fits_' + comboname
        ## subfolder for sbatch.sh files
        self.batchfolder = 'sbatch_' + comboname 
        

    def output(self):
        # do not create if already exists
        if os.path.exists(self.outfolder):
            print 'Folder', self.outfolder, 'already exists!'
            return True
            
        os.mkdir(self.outfolder) # create output folder
        print 'Folder for given fit parameters setup:', self.outfolder + '/'
        return False
        
        
    def fitfiles(self, nbatch, input_folder):
        ''' Create .sh fit files for given parameters (20 files) '''

        num_fits = len(self.inpnums)
        # folder to store the fitfiles
        os.mkdir(self.outfolder + '/' + self.fitfolder)
        print '|'
        print ' - Subfolder for fit files:', self.fitfolder + '/'
        print '|\t(', self.fitfolder + '_X.sh, X = 0..' + str(int(ceil(num_fits*1./nbatch))) + ' )'
        print '|\t( each fit = max ' + str(nbatch) + ' lines)'

        # folder to store the batch files
        os.mkdir(self.outfolder + '/' + self.batchfolder)
        print '|'
        print ' - Subfolder with corr. batch files:', self.batchfolder + '/'
        print '|\t(', self.batchfolder + '_X.sh, X = 0..' + str(int(ceil(num_fits*1./nbatch))) +  ' )'
        print '|\t( each submission = 1 fit*.sh )'
        
        # for now instead of 10 000 use 100, not 500 per file but 5 (20 files)
        fitfile = None 
#        fitfile = open('.temp','w') # dummy
    
        counter = 0

        for i in self.inpnums:             
            ## every 5 files do:
            if(counter % nbatch == 0):
                if fitfile:
                    prev_name = fitfile.name
                    fitfile.close()
                    make_executable(prev_name) # chmod +x
            
                findex = int(counter / nbatch)
                # will be accessed in self.batch()
                self.fitname = self.fitfolder + '_' + str(findex) + '.sh'

                fitfile = open(self.outfolder + '/' + self.fitfolder + '/' + self.fitname, 'w')
                # the fitter thinks it's in the spectralfit folder
                print >> fitfile, '#!/bin/bash'
                print >> fitfile, 'EXEC="./spectralfit"'
                ## add to batch file (when we hit a new findex)
                self.batch(findex)

            # the 5th line is the one that will be copied many times for each input file: full or relative path to the input root file
            inputname = input_folder + '/Senf_' + str(i) + '.root' # Senh for half exposure, Senf for full!
            logname = 'sen_' + str(i) + '_' + self.metal + '_' + self.inj + '_' + 'cno_' + self.fit + '_' + self.var + '.log'
           
            if self.random == 'none':
                # the same species list for all fits
                print >> fitfile, '$EXEC', inputname, self.cnofolder + '/TFC_sub/Hsub_' + self.cnohisto + '_0_' + self.var, self.cfgname, self.iccname, '2>&1 | tee', self.outfolder + '/' + self.logfolder + '/' + logname
            else:
                # different species list
                print >> fitfile, '$EXEC', inputname, self.cnofolder + '/TFC_sub/Hsub_' + self.cnohisto + '_0_' + self.var, self.cfgname, self.iccname.split('.')[0] + '_' + str(i) + '.icc', '2>&1 | tee', self.outfolder + '/' + self.logfolder + '/' + logname

            counter+=1
            
        # last file
        prev_name = fitfile.name
        fitfile.close()
        make_executable(prev_name) # chmod +x

    
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
        
        # line 13: fit variable MC
        cfglines[12] =     'fit_variable_MC = ' + self.var + '\n'

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

        # line 103: dark noise
        cfglines[102] = 'dark_noise_window = win' + self.var[-1] + '\n'
        
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

        # extra: free (default) or penalty
        if self.penalty != 'none':
            for pensp in self.penalty:
                line_num, line = ICC[pensp]
                if pensp in ['pp','pep']:
                    icclines[line_num] = line[self.metal]
                else:
                    icclines[line_num] = line
        
        ## save file
        if self.random == 'none':
            # one species list for all fits
            outfile = open(self.iccname, 'w')
            outfile.writelines(icclines)
            outfile.close()
            print '\tcreator.py: iccfile : generated'
        else:
            # different one for each fit
            for i in self.inpnums: 
                for ransp in self.random:
                    line_num, line = ICC[ransp]
                    mn = rnd.gauss(RND[ransp][0], RND[ransp][1]) # mean
                    lineparts = line.split(',')
                    lineparts[5] = ' ' + str(round(mn,2)) + ' '
                    lineparts[7] = ' ' + str(round(mn,2)) + ' '
                    icclines[line_num] = ','.join(lineparts)
                
                outfile = open(self.iccname.split('.')[0] + '_' + str(i) + '.icc', 'w')
                outfile.writelines(icclines)
                outfile.close()
            
            num_fits = len(self.inpnums) 
            print '\tcreator.py: iccfiles: generated (', num_fits, 'files )'




    def logfiles(self):
        ''' Create output folder for the log files '''
        os.mkdir(self.outfolder + '/' + self.logfolder)
        print '|'
        print ' - Subfolder for future log files:', self.logfolder + '/'
        print '|\t( sen_X_' + self.metal + '_' + self.inj + '_' + 'cno_' + self.fit + '_' + self.var + '.log'


    def batch(self, findex):
        ''' Create jureca batch submission files '''
            
        batchname = self.outfolder + '/' + self.batchfolder + '/' + self.batchfolder + '_' + str(findex) + '.sh'
        batchfile = open(batchname, 'w')

        ## batch file template
        sublines = open('templates/sbatch_submission_template.sh').readlines()
        
        # last line: our fit
        # will submit sbatch being located in the fitter folder, so it will call relative to that position; and the fitter being called will also be relative spectral fitter core folder
        sublines[-1] = 'srun ' + self.outfolder + '/' +  self.fitfolder + '/' + self.fitname
        
        ## save
        batchfile.writelines(sublines)
        batchfile.close()
        make_executable(batchname) # chmod +x


def make_executable(path):
    ''' chmod +x the file'''
    mode = os.stat(path).st_mode
    mode |= (mode & 0o444) >> 2    # copy R bits to X
    os.chmod(path, mode)


CNOICC = {'fixed': '   { "nu(CNO)",      -1,   kCyan,   kSolid,  2,    0.,   "fixed", 0.,  50. },\n',
            'free': '{ "nu(CNO)",      -1,   kCyan,   kSolid,  2,    5.36,   "free", 0.,  50. },\n'}

# penalty: line number is line - 1 (i.e. line 1 is 0)
ICC = {
    'Bi210': [27, '{ "Bi210",        -1,   kSpring, kSolid,  2,    17.5,    "penalty",  17.5,  2.0 },\n'],
    'C14': [13, '{ "C14",          -1,   kViolet, kSolid,  2,    3.456e+6, "penalty", 3.456e+6, 17.28e+4 },\n'],
    'pp': [17, {'hz': '{ "nu(pp)",       -1,   kRed,   kSolid,  2,    131.1,   "penalty",  131.1., 1.4 },\n', 'lz': '{ "nu(pp)",       -1,   kRed,   kSolid,  2,    132.2,   "penalty",  132.2,  1.4 },\n'}],
    'pep': [19, {'hz': '{ "nu(pep)",      -1,   kCyan,   kSolid,  2,    2.74,   "penalty", 2.74,  0.04 },\n', 'lz': '{ "nu(pep)",      -1,   kCyan,   kSolid,  2,    2.78,   "penalty", 2.78,  0.04 },\n'}]
}

RND = {'Bi210': [10,2], 'C14': [3456000, 172800]}
