# The cutest cat — make.fun bounty entry

Entry for the [make.fun](https://make.fun) bounty
**"Draw the cutest cat"** (`cutest-cat-01`, $100 prize pool, top 3).

## What it does

`main.py` draws a cat and writes it to `/output/entry.png` (or
`$MAKEFUN_OUTPUT_DIR/entry.png`): a big-eyed ginger kitten sitting
front-on with a slight head tilt, pink inner ears and nose, whiskers,
blush, a curled tail with a cream tip, and a little ball of yarn by its
paw. No image file is shipped — every pixel is rasterized by the program
itself (circles, ellipses, triangles and bezier curves), and the PNG
bytes are built by hand with `zlib` + `struct`.

## Run it locally

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Standard library only; Python 3.13 in the grading sandbox. No network.
The output is deterministic: two runs write byte-identical files
(1024x1024 PNG, ~18 KB, well under the 1 MiB limit).

## License

MIT — see [LICENSE](LICENSE).
