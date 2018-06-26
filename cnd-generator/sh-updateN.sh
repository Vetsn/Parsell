
# counted compartments in your model?
# good, these commands'll apply that number.

count=`python compartmentN.py`
echo "compartment count: $count"
echo ""

# no argument values?
if [ $# -eq 0 ]; then
	echo "usage: sh-updateN.sh [options]"
	echo "[options]:"
	echo "  (default)   print number of compartments in model described in 'blueprint.txt'."
	echo "              does not overwrite anything."
	echo "  -update     update the number of compartments accordingly in 'Sim_cond.cnd' and 'Sim_prog.cpp'."
	echo ""
	exit
fi

if [ $1 != "-update" ]; then
	# just print, no update
	exit
else
	# update parameter
	sed -e "/^<CellStructure>/ {N;p;N;s/^.\+\n\([^\n]\+\)$/\1/g;s/^[0-9]\+/$count/g}" Sim_cond.cnd > x ; mv x Sim_cond.cnd
	sed -e "s/#define N_COMPARTMENT.*/#define N_COMPARTMENT\t$count/"                 Sim_prog.cpp > x ; mv x Sim_prog.cpp
	echo "updated."
fi
