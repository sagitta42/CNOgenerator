printf "\nTotal number of logs ready: "
ls $1/*.log | wc -l
printf "\nSuccessful fits: "
grep "FIT PARAMETERS" $1/*.log | wc -l
printf "\n"
