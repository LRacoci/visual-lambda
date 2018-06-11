reverte [] = []
reverte l = reverte(xs)+[x]
where x = first(l)
where xs = rest(l)

main = reverte([1,2,3,4,5])