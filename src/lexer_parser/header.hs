-- Header
map f list =
  if list == []
    then list
    else [f(list[0])] + map(f)(rest(list)(1))

filter f list =
  if list == []
    then []
    else (
      if f(list[0])
        then [list[0]]
        else []
      ) + filter(f)(rest(list)(1))

rest list x = if list[x] == None then [] else [list[x]] + rest(list)(x+1)

fold func list initial =
  if list == []
    then initial
    else func(list[0])(
      fold
        (func)
        (rest(list)(1))
        (initial)
    )

