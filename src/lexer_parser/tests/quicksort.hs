main = qs([4,2,3,1])
qs [] = []
qs l = qs(small) + [x] + qs(large)
where x = first(l)
where xs = rest(l)
where small = filter(\ y -> y <= x)(xs)
where large = filter(\ y -> y > x)(xs)