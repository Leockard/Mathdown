# Mathdown
## Rmarkdown for Mathematica.


### Overview
The **mathdown** script imitates the basic functionality of RMarkdown but for Mathematica (Wolfram Language).


### Installation
Clone this repo and execute mathdown.py.


### Usage
$> python mathdown.py your_file.Mmd

Where *your_file.Mmd* is a Markdown file containing Mathematica code chunks. Each chunk
must start with three backquotes (`) followed by the "{Mathematica}" tag on the first
line, and end with a line containing only three backquotes.


### Example
This README.md file was generated from README.Mmd, also available in the repo.
```{Mathematica}
Print["This is a chunk."]
var = 2;
Range[10]
```

```
"This is a chunk."
{1, 2, 3, 4, 5, 6, 7, 8, 9, 10}
```

Mathdown retains variables across chunks:

```{Mathematica}
Print["This is a second chunk."]
var
Do[var = var^var, {2}];
var
```

```
"This is a second chunk."
2
256
```


### License
This **Mathdown** repo is licensed under the UNLICENSE.
