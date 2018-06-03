-- Header
map f list =
  if list == []
    then list
    else [f(list[0])] + map(f)(rest(list))

filter f list =
  if list == []
    then []
    else (
      if f(list[0])
        then [list[0]]
        else []
      ) + filter(f)(rest(list))

fold func list initial =
  if list == []
    then initial
    else func(list[0])(
      fold
        (func)
        (rest(list))
        (initial)
    )

rest list = if list == [] then [] else restAux(list)(1)
restAux list x = if list[x] == None then [] else [list[x]] + restAux(list)(x+1)

first list = if list == [] then [] else list[0]
