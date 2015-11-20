set -x

for type in number pos1 pos2 pos3
do
    python2 Run.py \
	    --type $type \
	    --process JZ4 \
	    --submit-dir JZ4 \
	    --driver grid \
	    --grid-input group.perf-idtracking:group.perf-idtracking.361024.Pythia8EvtGen_A14NNPDF23LO_jetjet_JZ4W.AOD_TIDE.e3668_s2576_s2132_r6765_v5_wSiHits_EXT0 
    rm -rf JZ4
	 		
done
