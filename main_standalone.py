# %%

from build123d import *

from ocp_vscode import *

set_port(3939)
# s = status()
# print(s)

b = Box(1, 2, 3)
b = fillet(b.edges(), 0.15)

show(b, debug=False)
