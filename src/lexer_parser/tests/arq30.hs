a x = 2*x
b x = 3*x
c x = 5 * x
f x = {
  'ac' + "bc" : a(x),
  "ba" + 'ca' : b(x),
  'cb' + "ab" : c(x)
}
main = f(f(7)["acbc"])[x + y]
  where z = 'a'
  where x = 'b' + z
  where y = "c" + z