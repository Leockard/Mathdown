# Mathdown
## Rmarkdown for Mathematica.


### Overview
The **mathdown** script imitates the basic functionality of RMarkdown but for Mathematica (Wolfram Language).


### Installation
Clone this repo and execute mathdown.py, with python3.


### Usage
$> python3 mathdown.py your_file.Mmd

Where *your_file.Mmd* is a Markdown file containing Mathematica code chunks. Each chunk
must start with three backquotes (`) followed by the "{Mathematica}" tag on the first
line, and end with a line containing only three backquotes.


### Example
This README.md file was generated from README.Mmd, also available in the repo.
```{Mathematica}
Print["This is a chunk."]
Range[10]
foo = 2;
```

```
"This is a chunk."
{1, 2, 3, 4, 5, 6, 7, 8, 9, 10}
```

Mathdown retains variables across chunks: it keeps the "foo" variable we defined previosly.

```{Mathematica}
foo
```

```
2
```

Inline chunks are also supported. For example, we can print the value of "foo" within a
paragraph: "foo" = 2.

Mathdown calls Export[] on Graphics[] output to convert them to .jpg and save them in a
separate folder. (Here we manually insert the image so that this README is
complete. Locally, the figures are stored in the your_file-graphics/ folder.)

```{Mathematica}
Plot[x^foo, {x, 0, 10}]
```
![]("README-graphics/chunk-7-1.jpg?raw=True")


### License
This **Mathdown** repo is licensed under the UNLICENSE.
