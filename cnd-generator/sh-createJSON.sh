
# trims parameters into JSON for handling in python
offsetFrom=`sed -n '/<SymbolList>/      {=}' Sim_cond.cnd | awk '{print $1+1}'`
offsetTo=`  sed -n 'N;/<CalcCondition>/ {=}' Sim_cond.cnd | awk '{print $1-1}'`
sed "1, $offsetFrom d; $offsetTo q" Sim_cond.cnd | awk '\
BEGIN{print"["}
{
	if(NR!=1) printf(",\n")
	printf("[\"%s\",\t{\"default\":%s} ]", $1,$7)
}
END{print "\n]"}
' > concentration.json

sed 's/<[^>]\+>//g' s-g.html | awk -F "\t" '\
BEGIN{print"["}
{
	if(NR!=1){ print "," }
	if($1 != ""){
		symbol = ($1-1) ",\t\"" $2 "\""
	}
	printf("[%s,\t\"%s\"]", symbol,$3)
}
END{print"\n]"}
' > symbol-group.json

sed 's/<[^>]\+>//g' s-g.html | awk -F "\t" '{print $3}' | sort | uniq | awk '
BEGIN{print"["}
{
	if(NR!=1) printf(",\n")
	printf ("[\"%s\", \"\"]", $1)
}
END{print"\n]"}
'> editthisgrouplist.txt



