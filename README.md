## Example usage

```
python generator.py hz 0 free npmts_dt1
python generator.py hz 0 free npmts_dt1 penalty=Bi210
python generator.py hz 0 free npmts_dt1 random=Bi210
```

## Parameters

On top of the file generator.py you can define several parameters
```
# total number of fits
NFITS_min = 486 # including
NFITS_max = 1000 # not including
# number of fits per one submission file
NBATCH = 100
# path to the input root files
INPUT = '/p/project/cjikp20/jikp2001/BxFitterData/senst'
```
## Inputs and outputs to the code

```
generator.py
|
 - creator.py
|   |
|    - templates/
|
 -> fitoptions/*.cfg (if needed) [common fitoptions files]
|	(e.g. fitoptions/fitoptions_hz_0_npmts_dt1.cfg)
|
 -> species_list/*.icc (if needed) [common species lists]
|	(e.g. species_list/species_free.icc)
|
 -> fit_*/ [specific inputs and outputs for our combination]
   |	(e.g. fit_hz_0_cno_free_npmts_dt1/)
   |
	-> logs_*/ [folder with outputs from the fitter]
   |	(e.g. logs_hz_0_cno_free_npmts_dt1/, future log file created by the fit*.sh: logs_hz_0_cno_free_npmts_dt1/sen_X_hz_0_cno_free_npmts_dt1.log where X is from 0 to 10000)
   |
    -> fits_*/*.sh [folder with *.sh fitter files]
   |	(e.g. fits_hz_0_cno_free_npmts_dt1/fit_hz_0_cno_free_npmts_dt1_X.sh where X is from 0 to 20)
   |
    -> sbatch_*/*.sh [folder with *.sh batch submission files corr. to the fit files]
		(e.g. sbatch_hz_0_cno_free_npmts_dt1/sbatch_hz_0_cno_free_npmts_dt1_X.sh where X is from 0 to 20)
```


The sbatch*.sh submission files should be launched from the spectralfitter folder.
The sbatch*.sh files call the fit via a relative path (outfolder/fitfolder/fits_*.sh), and the fit*.sh files call fitoptions*.cfg and species_*.icc via relative paths too and have a relative path to the log files as well (../logs_*/)
