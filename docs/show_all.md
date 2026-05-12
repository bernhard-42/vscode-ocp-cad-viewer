## show_all

Show every CAD object in the current scope (`locals()`) of the Python interpreter.

### Command

```python
show_all(variables=None, exclude=None, classes=None, include=None, <keyword arguments>)
```

### Arguments

```text
    Show all variables in the current scope

    Parameters:
        variables:     Only show objects with names in this list of variable names,
                       i.e. do not use all from locals()
        exclude:       List of variable names to exclude from "show_all"
        classes:       Only show objects which are instances of the classes in this list
        include:       List of variable names that should be shown even though they
                       would be filtered out by `classes`. Only takes effect when
                       `classes` is set.

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
