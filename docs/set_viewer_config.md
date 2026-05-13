## set_viewer_config

Change configuration of the OCP CAD Viewer from Python. The changes will be applied immediately.

### Command

```python
set_viewer_config(<keyword arguments>)
```

### Arguments

```text

Keywords

- UI
    glass:                   (boolean) Use glass mode where tree is an overlay over the cad object
    tools:                   (boolean) Show tools
    tree_width:              (int) Width of the object tree

- Viewer
    axes:                    (boolean) Show axes
    axes0:                   (boolean) Show axes at (0,0,0)
    grid:                    (boolean) Show grid
    ortho:                   (boolean) Use orthographic projections
    transparent:             (boolean) Show objects transparent
    black_edges:             (boolean) Show edges in black color
    collapse:                (enum) Collapse.LEAVES: collapse all single leaf nodes,
                                    Collapse.ROOT: expand root only,
                                    Collapse.ALL: collapse all nodes,
                                    Collapse.NONE: expand all nodes
    explode:                 (boolean) Turn on explode mode
    analysis_tool:           (AnalysisTool or string) Activate an analysis tool
                                     (mutually exclusive with explode=True):
                                     AnalysisTool.PROPERTIES, AnalysisTool.DISTANCE,
                                     AnalysisTool.SELECT, AnalysisTool.OFF
                                     (or "properties", "distance", "select", "off")

    zoom:                    (int) Zoom factor of view
    position:                (float 3-tuple) Camera position
    quaternion:              (float 4-tuple) Camera orientation as quaternion
    target:                  (float 3-tuple) Camera look at target

    pan_speed:               (float) Speed of mouse panning
    rotate_speed:            (float) Speed of mouse rotate
    zoom_speed:              (float) Speed of mouse zoom

    states:                  (dict) Set the visibility state of cad objects. Format: `{'path': [1, 1]}`
                                `[1,1], [0,1]` (first element of the tuple) toggles faces
                                `[1,1], [1,0]` (second element of the tuple) toggles edges
    tab:                     (string/UiTab) Select a tab in the viewer:
                                     "tree" | "clip" | "zebra" | "material" | "studio"
                                     (or use UiTab.TREE, UiTab.CLIP, UiTab.ZEBRA,
                                     UiTab.MATERIAL, UiTab.STUDIO)

    clip_slider_0:           (float) Set clipping slider 0 to a value
    clip_slider_1:           (float) Set clipping slider 1 to a value
    clip_slider_2:           (float) Set clipping slider 2 to a value
    clip_normal_0:           (float 3-tuple) Set clipping normal 0 to a 3 dim tuple
    clip_normal_1:           (float 3-tuple) Set clipping normal 1 to a 3 dim tuple
    clip_normal_2:           (float 3-tuple) Set clipping normal 2 to a 3 dim tuple
    clip_intersection:       (boolean) Turn on/off intersection clipping
    clip_planes:             (boolean) Show/hide clipping helper planes
    clip_object_colors:      (boolean) Toggle RGB and object color clipping caps

- Studio
    studio_environment:      (StudioEnvironment or string) Environment HDR map; use
                                     the StudioEnvironment enum or a custom HDR URL
    studio_env_intensity:    (float) Intensity of environment lighting, 0-3.0
    studio_env_rotation:     (float) Rotation of environment map in degrees, 0-360
    studio_background:       (StudioBackground) ENVIRONMENT, TRANSPARENT, GRADIENT,
                                     GRADIENT_DARK, WHITE, GREY, DARKGREY
    studio_tone_mapping:     (StudioToneMapping) NEUTRAL, ACES, NONE
    studio_exposure:         (float) Tone mapping exposure, 0-3.0
    studio_shadow_intensity: (float) Shadow intensity, 0-1.0
    studio_shadow_softness:  (float) Shadow softness, 0-1.0
    studio_ao_intensity:     (float) Ambient occlusion intensity, 0-3.0
    studio_texture_mapping:  (StudioTextureMapping) TRIPLANAR or PARAMETRIC
    studio_4k_env_maps:      (boolean) Use 4K resolution environment maps

- Renderer:
    default_edgecolor:       Default color of the edges of a mesh
    default_opacity:         Opacity value for transparent objects

    ambient_intensity:       Intensity of ambient light
    direct_intensity:        Intensity of direct light
    metalness:               Metalness property of the default material
    roughness:               Roughness property of the default material

    port:                    Port of OCP CAD Viewer
```
