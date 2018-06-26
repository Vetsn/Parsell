
# trims parameters into JSON for handling in python
offset=`sed -n '/\/\/embedded_reaction/ {=}' Sim_cond.cnd `
sed "$offset q" Sim_cond.cnd | cat - dump > x; mv x Sim_cond.cnd

