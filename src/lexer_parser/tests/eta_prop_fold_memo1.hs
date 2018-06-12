fib 0 = 0
fib 1 = 1
fib n = fib(n-1) + fib(n-2)
g x = x
f x = g(x)
main = fib(f(a + a)) where a = 2
