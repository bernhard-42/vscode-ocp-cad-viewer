## push_object and show_objects

Incrementally show CAD objects in Visual Studio Code. The commands support the CQ-Editor parameters `obj`, `name` and `options` plus additional viewer-specific args. Compared to `show_object`, this pair is the lazy variant: `push_object` collects objects without rendering, and `show_objects` then renders them in a single batch — much faster than calling `show_object` repeatedly.

### Command

```python
push_object(obj, name=None, color=None, alpha=None, material=None, mode=None, clear=False, update=False)
```

### Arguments

    Parameters:
        obj: The object to be added or updated. Must have 'name', 'label', 'color', or 'alpha'
            attributes if corresponding arguments are not provided.
        name (str, optional): The name to associate with the object. If not provided,
            attempts to use 'name' or 'label' attribute of obj.
        color (any, optional): The color to associate with the object. If not provided,
            attempts to use 'color' attribute of obj.
        alpha (float, optional): The alpha (transparency) value for the object. If not provided,
            attempts to use 'alpha' attribute of obj, defaults to 1.0.
        material (PbrProperties or str, optional): Material object or material name string for the object.
        mode (Render, optional): A Render value for this object (Render.ALL, Render.EDGES, Render.FACES, Render.NONE).
        clear (bool, optional): If True, clears the OBJECTS registry before adding the new object.
        update (bool, optional): If True, updates an existing object with the same name;
            otherwise, appends as a new object.

    Raises:
        ValueError: If no name is provided and the object does not have a 'name' or 'label' attribute.

### Command

```python
show_objects(<keyword arguments>)
```

### Arguments

```text
    Keywords for show_objects:
        progress:                Show progress of tessellation with None is no progress indicator. (default="-+*c")
                                 for object: "-": is reference,
                                             "+": gets tessellated with Python code,
                                             "*": gets tessellated with native code,
                                             "c": from cache


    Valid keywords to configure the viewer (**kwargs):
    - UI
        glass:                   Use glass mode where tree is an overlay over the cad object (default=False)
        tools:                   Show tools (default=True)
        tree_width:              Width of the object tree (default=240)

    - Viewer
        axes:                    Show axes (default=False)
        axes0:                   Show axes at (0,0,0) (default=False)
        grid:                    Show grid (default=False)
        ortho:                   Use orthographic projections (default=True)
        transparent:             Show objects transparent (default=False)
        default_opacity:         Opacity value for transparent objects (default=0.5)
        black_edges:             Show edges in black color (default=False)
        orbit_control:           Mouse control use "orbit" control instead of "trackball" control (default=False)
        collapse:                Collapse.LEAVES: collapse all single leaf nodes,
                                 Collapse.ROOT: expand root only,
                                 Collapse.ALL: collapse all nodes,
                                 Collapse.NONE: expand all nodes
                                 (default=Collapse.ROOT)
        analysis_tool:           Activate an analysis tool: AnalysisTool.PROPERTIES,
                                 AnalysisTool.DISTANCE, AnalysisTool.SELECT (default=AnalysisTool.OFF)
        tab:                     Select a UI tab: UiTab.TREE, UiTab.CLIP, UiTab.ZEBRA,
                                 UiTab.MATERIAL, UiTab.STUDIO (default=UiTab.TREE)
        ticks:                   Hint for the number of ticks in both directions (default=5)
        center_grid:             Center the grid at the origin or center of mass (default=False)
        grid_font_size:          Size for the font used for grid axis labels (default=12)
        up:                      Use z-axis ('Z') or y-axis ('Y') as up direction for the camera (default="Z")

        zoom:                    Zoom factor of view (default=1.0)
        position:                Camera position
        quaternion:              Camera orientation as quaternion
        target:                  Camera look at target
        reset_camera:            Camera.RESET: Reset camera position, rotation, zoom and target
                                 Camera.CENTER: Keep camera position, rotation, zoom, but look at center
                                 Camera.KEEP: Keep camera position, rotation, zoom, and target
                                 (default=Camera.RESET)

        clip_slider_0:           Setting of clipping slider 0 (default=None)
        clip_slider_1:           Setting of clipping slider 1 (default=None)
        clip_slider_2:           Setting of clipping slider 2 (default=None)
        clip_normal_0:           Setting of clipping normal 0 (default=None)
        clip_normal_1:           Setting of clipping normal 1 (default=None)
        clip_normal_2:           Setting of clipping normal 2 (default=None)
        clip_intersection:       Use clipping intersection mode (default=None)
        clip_planes:             Show clipping plane helpers (default=False)
        clip_object_colors:      Use object color for clipping caps (default=False)

        zebra_count:             Setting of zebra stripe count (default=9, range: 2-50)
        zebra_opacity:           Setting of zebra opacity (default=1, range: 0-1)
        zebra_direction:         Setting of zebra direction angle (default=0, range: 0-90)
        zebra_color_scheme:      Zebra color scheme: "blackwhite", "grayscale", or "colorful" (default="blackwhite")
        zebra_mapping_mode:      Zebra mapping mode: "reflection" or "normal" (default="reflection")

        studio_environment:      Environment HDR map, use StudioEnvironment enum or a custom HDR URL
                                 (default=StudioEnvironment.PROCEDURAL_STUDIO)
        studio_env_intensity:    Intensity of environment lighting, 0-3.0 (default=1.0)
        studio_env_rotation:     Rotation of environment map in degrees, 0-360 (default=0)
        studio_background:       StudioBackground.ENVIRONMENT, .TRANSPARENT, .GRADIENT, .GRADIENT_DARK,
                                 .WHITE, .GREY, .DARKGREY (default=StudioBackground.ENVIRONMENT)
        studio_tone_mapping:     StudioToneMapping.NEUTRAL, .ACES, .NONE (default=StudioToneMapping.NEUTRAL)
        studio_exposure:         Tone mapping exposure, 0-3.0 (default=1.0)
        studio_shadow_intensity: Shadow intensity, 0-1.0 (default=0.5)
        studio_shadow_softness:  Shadow softness, 0-1.0 (default=0.2)
        studio_ao_intensity:     Ambient occlusion intensity, 0-3.0 (default=0.5)
        studio_texture_mapping:  StudioTextureMapping.TRIPLANAR or .PARAMETRIC
                                 (default=StudioTextureMapping.TRIPLANAR)
        studio_4k_env_maps:      Use 4K resolution environment maps (default=False)

        pan_speed:               Speed of mouse panning (default=1)
        rotate_speed:            Speed of mouse rotate (default=1)
        zoom_speed:              Speed of mouse zoom (default=1)

    - Renderer
        deviation:               Shapes: Deviation from linear deflection value (default=0.1)
        angular_tolerance:       Shapes: Angular deflection in radians for tessellation (default=0.2)
        edge_accuracy:           Edges: Precision of edge discretization (default: mesh quality / 100)

        default_color:           Default mesh color (default=(232, 176, 36))
        default_edgecolor:       Default color of the edges of a mesh (default=(128, 128, 128))
        default_facecolor:       Default color of the edges of a mesh (default=#ee82ee / Violet)
        default_thickedgecolor:  Default color of the edges of a mesh (default=#ba55d3 / MediumOrchid)
        default_vertexcolor:     Default color of the edges of a mesh (default=#ba55d3 / MediumOrchid)
        ambient_intensity:       Intensity of ambient light (default=1.00)
        direct_intensity:        Intensity of direct light (default=1.10)
        metalness:               Metalness property of the default material (default=0.30)
        roughness:               Roughness property of the default material (default=0.65)


        render_edges:            Render edges  (default=True)
        render_normals:          Render normals (default=False)
        render_mates:            Render mates for MAssemblies (default=False)
        render_joints:           Render build123d joints (default=False)
        show_parent:             Render parent of faces, edges or vertices as wireframe (default=False)
        show_sketch_local:       In build123d show local sketch in addition to relocate sketch (default=True)
        helper_scale:            Scale of rendered helpers (locations, axis, mates for MAssemblies) (default=1)

    - Debug
        debug:                   Show debug statements to the VS Code browser console (default=False)
        timeit:                  Show timing information from level 0-3 (default=False)
```

### Example

```python
import cadquery as cq
from ocp_vscode import show_object, reset_show, set_defaults

reset_show()  # use for repeated shift-enter execution to clean object buffer

set_defaults(axes=True, transparent=False, collapse=1, grid=(True, True, True))

box = cq.Workplane().box(1, 2, 1).edges().chamfer(0.4)
push_object(box, name="box", alpha=0.5)

sphere = cq.Workplane().sphere(0.6)
push_object(sphere, name="sphere", alpha=0.5)

show_objects(
    collapse="1",
    ortho=False
)
```
