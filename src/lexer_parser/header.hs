-- Header
map f [] = []
map f list = [f(list[0])] + map(f)(rest(list))

filter f [] = []
filter f list = (
      if f(list[0])
        then [list[0]]
        else []
      ) + filter(f)(rest(list))

fold func [] initial = initial
fold func list initial = func(list[0])(
      fold
        (func)
        (rest(list))
        (initial)
    )

rest [] = []
rest list = end(list)(1)

end list x = if list[x] == None
  then []
  else [list[x]] + end(list)(x+1)

first [] = []
first list = list[0]

init list n = if list[n] == None
  then []
  else init(list)(n-1) + [list[n]]

len [] = 0
len ls = 1 + len(rest(ls))

last ls = ls[len(ls)-1]