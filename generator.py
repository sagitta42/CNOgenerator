from math import ceil

#----------------------------------------------------------

## ENTER YOUR CHOICES HERE

# total number of fits
NFITS_min = 0 # including
NFITS_max = 1100 # not including
# number of fits per one submission file
NBATCH = 100
# path to the input root files
INPUT = '/p/project/cjikp20/jikp2001/BxFitterData/final_senp3_full' # full exposure
#INPUT = '/p/project/cjikp20/jikp2001/BxFitterData/final_senp3_half' # half exposure
#INPUT = '/p/project/cjikp20/jikp2001/BxFitterData/senst'

#----------------------------------------------------------

import sys
from creator import * 

#----------------------------------------------------------

def generator(metal, inj, fit, var, penalty, random, lst):
    '''
    0) metal: metallicity (hz or lz)
    1) inj: injected CNO (1 or 0)
    2) fit: how to fit CNO (fixed or free)
    3) var: energy variable (npmts_dt1, npmts_dt2 or nhits)
    4) penalty: species to put penalty on (e.g. Bi210) (optional)
    5) random: species to make randomized mean for (e.g. Bi210) (optional)
    6) list: list of input numbers (alternative to from  Nmin to Nmax)               
    '''

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
    
    for pen in penalty:
        if not ((pen in ICC) or (pen == 'pp/pep') or penalty == 'none'):
            print '\nOptions for penalty:', ','.join(ICC.keys())
            return
   
    for rand in random:
        if not (rand in ICC or random == 'none'):
            print '\nOptions for random:', ','.join(ICC.keys())
            return

    ## for now ignore nhits
    if not var in ['npmts_dt1', 'npmts_dt2']:
        print '\nOptions for energy variable: npmts_dt1 or npmts_dt2 (nhits NOT implemented)\n'
        return


    ## ---------------------------------

    ## init
    s = Submission(metal, inj, fit, var, NFITS_min, NFITS_max, penalty, random, lst)
    
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
    inpfolder = INPUT if lst == 'none' else None # if list given, check which exposure; if not given, take the one specified on top of this file
    s.fitfiles(NBATCH, inpfolder)
    
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
    userinput = sys.argv[1:]
    
    if not len(userinput) in range(4,8):
        print
        print 'Examples:'
        print 'python generator.py hz 0 free npmts_dt1'
        print 'python generator.py hz 0 free npmts_dt1 list=list_of_input_numbers.list'
        print 'python generator.py hz 0 free npmts_dt1 penalty=Bi210'
        print 'python generator.py hz 0 free npmts_dt1 random=Bi210'
        print 'python generator.py hz 0 free npmts_dt1 random=Bi210,C14'
        print 'python generator.py hz 0 free npmts_dt1 penalty=pp,pep random=Bi210,C14'
        print 'python generator.py hz 0 free npmts_dt1 penalty=pp,pep random=Bi210,C14 list=good_root_5000_nums.list'
        print 'python generator.py hz 0 free npmts_dt1 penalty=pp/pep random=Bi210,C14 list=good_root_5000_nums.list'
        print 'python generator.py hz 0 free npmts_dt1 penalty=pp,pep,Kr85 random=Bi210,C14 list=good_root_full_nums_1100.list'
        print
        sys.exit(1)

    params = userinput[:4] # the first four are always there e.g. hz 0 free npmts_dt1

    ## penalty and random options
    opts = {}
    for opt in ['penalty', 'random', 'list']:
        opts[opt] = 'none'

    for opt in ['penalty', 'random', 'list']:
        for inp in userinput[4:]:
            if opt in inp:
                opts[opt] = inp.split('=')[1] if opt == 'list' else inp.split('=')[1].split(',')
            
    params += [opts['penalty'], opts['random'], opts['list']]

    print params
        
    generator(*params)
