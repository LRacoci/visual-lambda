f1 n = f2(n)
f2 n = f3(n)
f3 n = f4(n)
f4 n = f5(n)
f5 n = f1(n)

main = f1(1)