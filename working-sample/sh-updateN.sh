
# counted compartments in your model?
# good, these commands'll apply that number.

# validation
if [ -z $1 ]; then
	echo "(tell me how many compartments you have in your model, via argv.)"
	exit
fi

# apply parameter
sed -e "/^<CellStructure>/ {N;p;N;s/^.\+\n\([^\n]\+\)$/\1/g;s/^[0-9]\+/$1/g}" Sim_cond.cnd > x; mv x Sim_cond.cnd
sed -e "s/#define N_COMPARTMENT.*/#define N_COMPARTMENT\t$1/"                 Sim_prog.cpp > x; mv x Sim_prog.cpp





