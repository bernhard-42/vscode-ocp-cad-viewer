## show_all

Incrementally show CAD objects in Visual Studio Code. The command support the CQ-Editor parameters `obj`, `name` and `options` plus additional viewer specific args.

### Command

```python
show_all(name=None, options=None, port=None, <keyword arguments>)
```

### Arguments

```text
    Show all variables in the current scope

    Parameters:
        variables:     Only show objects with names in this list of variable names, 
                       i.e. do not use all from locals()
        exclude:       List of variable names to exclude from "show_all"
        classes:       Only show objects which are instances of the classes in this list
        _visual_debug: private variable, do not use!

    Keywords for show_all:
        Valid keywords for "show_all" are the same as for "show"
```

For more detail, see [show](show.md)

### Example

```python
from build123d import *
from ocp_vscode import *

set_defaults(axes=True, transparent=False, collapse=1, grid=(True, True, True))

box = Box(1, 2, 1)
chamfer(box.edges(), 0.4)
sphere = Sphere(0.8)

show_all(
    collapse="1",
    ortho=False
)
```
