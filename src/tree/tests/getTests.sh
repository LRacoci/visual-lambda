#Need to run with bash
path_src="../../../src/lexer_parser/tests"

regex="$path_src/arq([0-9]+).json"

for f in $path_src/*
do
    if [[ $f =~ $regex ]]
    then
        name="${BASH_REMATCH[1]}"
        cp $f "forest${name}.json"    # concatenate strings
    fi
done
