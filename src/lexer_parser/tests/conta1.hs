soma1 [] ch = [(ch,1)]
soma1 l ch = if x[0] == ch then [(x[0],x[1] + 1)]+xs
                      else [x]+soma1(xs)(ch)
where x = first(l)
where xs = rest(l)

contapalavra l = if xs == [] then [(l[0],1)]
                           else soma1(contapalavra(xs))(l[0])
where xs = rest(l)

main = contapalavra(["a","abc","a","b","b"])