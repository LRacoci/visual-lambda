soma1 l ch = if res[1] == True then res[0]
             else res[0] + [(ch,1)]
             where res = fold(\ x acc -> if x[0] == ch then ([(x[0],x[1]+1)]+acc[0],True) else ([(x[0],x[1])]+acc[0],acc[1]))(l)(([],False))

contapalavra l = if xs == [] then [(l[0],1)]
                           else soma1(contapalavra(xs))(l[0])
where xs = rest(l)

main = contapalavra(["a","abc","a","b","b"])