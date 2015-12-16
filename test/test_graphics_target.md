# Test some plots and Graphics[] expressions

Here we test Plot[] types of functions and their outputs.

## Plots per chunk
We begin with one plot per chunk.

```{Mathematica}
Plot[x^2, {x, 0, 10}]
```
![]("test_graphics-figures/chunk-0-1.jpg")


Two plots per chunk.

```{Mathematica}
Plot[Sin[x], {x, 0, 10}]
Plot[Cos[x], {x, 0, 10}]
```
![]("test_graphics-figures/chunk-1-1.jpg")
![]("test_graphics-figures/chunk-1-2.jpg")


## Expressions with Graphics[] within
Test when Graphics[] is not the sole expression in the output.

```{Mathematica}
Plot[Sin[x^#], {x, 0, 10}] & /@ {1,2,3}
```

```
{![]("test_graphics-figures/chunk-2-1.jpg"), ![]("test_graphics-figures/chunk-2-2.jpg"), ![]("test_graphics-figures/chunk-2-3.jpg")}
```

## Other types of plots

Here be any other type of plot that outputs a Graphics[].

```{Mathematica}
ParametricPlot[{Cosh[t] + 2 Sinh[t], 2 Cosh[t] + Sinh[t]}, {t, -1, 1}]
```
![]("test_graphics-figures/chunk-3-1.jpg")


```{Mathematica}
(* Plot3D[{Cosh[x]/Sinh[y], 2 Cosh[x] Sinh[y]}, {x, -1, 1}, {y, -1, 1}] *)
```


