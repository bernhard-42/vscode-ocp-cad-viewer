# Color maps

A color map automatically assigns colors to the objects passed to `show()` / `show_all()`. Useful for collections (lists/tuples) where you don't want to spell out a color for each entry.

```python
from ocp_vscode import show, set_colormap, ColorMap
```

## Activation

```python
set_colormap(ColorMap.tab20())           # use one of the named maps
set_colormap(ColorMap.golden_ratio())    # generator-style endless palette
set_colormap(None)                       # or use unset_colormap()
```

`get_colormap()` returns the currently active map (resetting its iterator). `unset_colormap()` clears it.

The map is consumed each time `show` would otherwise default a color, so order matters — the n-th unnamed object gets the n-th color.

## Available factories

`ColorMap` exposes the following static factory methods:

### Listed palettes (cycling)

| Factory                                                  | Source                                                                              |
| -------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| `ColorMap.accent(alpha=1.0, reverse=False)`              | matplotlib's _Accent_ (8 colors)                                                    |
| `ColorMap.dark2(alpha=1.0, reverse=False)`               | _Dark2_ (8)                                                                         |
| `ColorMap.paired(alpha=1.0, reverse=False)`              | _Paired_ (12)                                                                       |
| `ColorMap.pastel1(alpha=1.0, reverse=False)`             | _Pastel1_ (9)                                                                       |
| `ColorMap.pastel2(alpha=1.0, reverse=False)`             | _Pastel2_ (8)                                                                       |
| `ColorMap.set1(alpha=1.0, reverse=False)`                | _Set1_ (9)                                                                          |
| `ColorMap.set2(alpha=1.0, reverse=False)`                | _Set2_ (8)                                                                          |
| `ColorMap.set3(alpha=1.0, reverse=False)`                | _Set3_ (12)                                                                         |
| `ColorMap.tab10(alpha=1.0, reverse=False)`               | _tab10_ (10)                                                                        |
| `ColorMap.tab20(alpha=1.0, reverse=False)`               | _tab20_ (20)                                                                        |
| `ColorMap.tab20b(alpha=1.0, reverse=False)`              | _tab20b_ (20)                                                                       |
| `ColorMap.tab20c(alpha=1.0, reverse=False)`              | _tab20c_ (20)                                                                       |

### Procedural palettes

| Factory                                                                                   | Description                                                                                              |
| ----------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `ColorMap.golden_ratio(colormap="hsv", alpha=1.0, reverse=False)`                          | Walks the colormap by the inverse golden ratio so successive colors are maximally distinct              |
| `ColorMap.seeded(seed_value=42, colormap="hsv", alpha=1.0, **params)`                      | Deterministic random walk through the colormap (use `colormap="rgb"` to draw RGB directly)              |
| `ColorMap.segmented(length=10, colormap="hsv", alpha=1.0, reverse=False)`                  | Equally spaced samples across a continuous colormap                                                      |
| `ColorMap.listed(length=10, colormap="mpl:plasma", colors=None, alpha=1.0, reverse=False)` | Subsample a matplotlib listed colormap, or pass `colors=[...]` to use your own list                     |

For matplotlib-based variants pass `colormap="mpl:<name>"` (e.g. `"mpl:plasma"`). The `mpl:` form requires matplotlib to be installed.

## Custom maps

Subclass `BaseColorMap` and implement `__next__` returning an `(r, g, b, alpha)` tuple. Use `set_colormap(YourMap())` to activate it.

For a working end-to-end example see [`examples/colormaps.py`](../examples/colormaps.py).
