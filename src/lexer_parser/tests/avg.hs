avg l = aux(l)(0)(0)
aux [] s t = s / t
aux l s t = aux(xs)(s+x)(t+1)
where x = first(l)
where xs = rest(l)

main = avg([10.0,8.0,3.0,4.0,5.0])