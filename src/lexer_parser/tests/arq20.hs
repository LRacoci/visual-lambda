isZero a = a == 0
fact n = if isZero(n) then 1 else fact(n - 1)
main = fact(3)