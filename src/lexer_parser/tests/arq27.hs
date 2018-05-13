g x = x/3
memo f x = m[x] where m = {x: f(x)}
f x = {g(x*2):g(x*3)}
id x = memo(f)(x)[x*2/3]
main = id(42)