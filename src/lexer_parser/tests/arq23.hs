main = y_combinator (factorial) (3)

apply y = y(y)
y_combinator f = apply(f(aply))

factorial f n = if n > 0 then f(n-1) else 1