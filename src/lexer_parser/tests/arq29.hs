a x = 2*x
b x = 3*x
c x = 5 * x
f x = {
  '\"' : a(x),
  "\'" + "\"" : b(x),
  '\"\"': c(x)
}
main = f(f(7)[y])[x + y]
  where x = '\''
  where y = "\""