#!bin/bash

WORKDIR=/home/llr/cms/portales/HIGtrigger/higgs-trigger-nanoaod/CMSSW_10_6_18/src/higgs-trigger-nano/
DATA_DIR=${WORKDIR}/data/dataset_lists/

declare -A TRIGGERS_PER_ERA
#TRIGGERS_PER_ERA["24ABC"]="VBFincl"
TRIGGERS_PER_ERA["24B"]="VBFincl"
TRIGGERS_PER_ERA["24C"]="VBFincl"
TRIGGERS_PER_ERA["24D"]="VBFincl"
TRIGGERS_PER_ERA["24E"]="VBFincl"

for era in ${!TRIGGERS_PER_ERA[@]};
do
    echo $era ${!TRIGGERS_PER_ERA[${era}]}
    for trigger in ${TRIGGERS_PER_ERA[${era}]}
    do
	echo ${era} $trigger
	FILE_LIST=${DATA_DIR}/Run${era}_MUON.txt
	JOB_ID=0
	cat $FILE_LIST | while read line

	do
	    EXPECTED_OUT=ntuples_out/tmp/${era}/goodfiles/histos_Run${era}_${trigger}_${JOB_ID}.root
	    (( NTOT++ ))
	    if [ -f "$EXPECTED_OUT" ]; then
		let JOB_ID++
	    else
		/opt/exp_soft/cms/t3/t3submit -short -singleout condor_sub.sh ${WORKDIR} ${line} ${trigger} ${era} ${JOB_ID}
		#condor_submit condor_sub.sh ${WORKDIR} ${line} ${trigger} ${era} ${JOB_ID}
		let JOB_ID++
	    fi
	done
    done
done

