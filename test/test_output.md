# Test some basic outputs

This chunk tests some basic Markdown features as well as Mathematica numeric outputs.
Implicitly, we're also testing for correct whitespace.

Such as integers and lists,

```{Mathematica}
Range[10]
```

```
{1, 2, 3, 4, 5, 6, 7, 8, 9, 10}
```

big integers, decimals, scientific notation,

```{Mathematica}
16^4^4
N[Pi, 30]
Pi/10000000000 // N
```

```
179769313486231590772930519078902473361797697894230657273430081157732675805500963132708477322407536021120113879871393357658789768814416622492847430639474124377767893424865485276302219601246094119453082952085005768838150682342462881473913110540827237163350510684586298239947245938479716304835356329624224137216
3.1415926535897932384626433832795028841971693993751058151208`30.
3.1415926535897934*^-10
```

fractions, exponents,

```{Mathematica}
(Sqrt[5] + 1)/2
Integrate[x^2, x]
```

```
(1 + Sqrt[5])/2
x^3/3
```

and more complicated expressions

```{Mathematica}
\[Integral]x Sqrt[x^3 - 1] \[DifferentialD] x
```

```
(2*(x^2*(-1 + x^3) + (-1)^(2/3)*3^(3/4)*Sqrt[(-1)^(5/6)*(-1 + x)]*Sqrt[1 + x + x^2]*(Sqrt[3]*EllipticE[ArcSin[Sqrt[-(-1)^(5/6) - I*x]/3^(1/4)], (-1)^(1/3)] + (-1)^(5/6)*EllipticF[ArcSin[Sqrt[-(-1)^(5/6) - I*x]/3^(1/4)], (-1)^(1/3)])))/(7*Sqrt[-1 + x^3])
```

Also, we test inline output: two plus two equals 4.
