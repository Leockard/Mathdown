# Test variable permanency across chunks

Define some variable and test its permanency within one chunk.

```{Mathematica}
var = 2
var + 2
var
```

```
2
4
2
```

And now test if it remains through another chunk.

```{Mathematica}
var
var = var^var
```

```
2
4
```

Even if the variable isn't even used.

```{Mathematica}
Range[10]
```

```
{1, 2, 3, 4, 5, 6, 7, 8, 9, 10}
```

Is it still there?

```{Mathematica}
var
```

```
4
```
