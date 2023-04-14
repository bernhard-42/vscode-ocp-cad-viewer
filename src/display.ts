/*
   Copyright 2023 Bernhard Walter
  
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at
  
      http://www.apache.org/licenses/LICENSE-2.0
  
   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
*/

import * as vscode from "vscode";

export function template() {
    let options = vscode.workspace.getConfiguration("OcpCadViewer");
    let theme = options.get("dark") ? "dark" : "light";
    let treeWidth = options.get("treeWidth");
    let control = options.get("orbitControl") ? "orbit" : "trackball";
    let up = options.get("up");
    let glass = options.get("glass");
    let tools = options.get("tools");
    let rotateSpeed = options.get("rotateSpeed");
    let zoomSpeed = options.get("zoomSpeed");
    let panSpeed = options.get("panSpeed");

    let html = `
<!DOCTYPE html>
<html>

<head>
    <meta charset="utf-8" />
    <title>OCP CAD Viewer</title>
    <link rel="stylesheet" href="https://unpkg.com/three-cad-viewer@1.7.5/dist/three-cad-viewer.css" /> <!-- 1.7.5 -->

    <script type="module">
        import { Viewer, Timer } from "https://unpkg.com/three-cad-viewer@1.7.5/dist/three-cad-viewer.esm.js";
        var viewer = null;
        var _shapes = null;
        var _states = null;
        var _config = null;
        var _zoom = null;
        var _position = null;
        var _quaternion = null;
        var _target = null;
        
        const MAP_HEX = {
            0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6,
            7: 7, 8: 8, 9: 9, a: 10, b: 11, c: 12, d: 13,
            e: 14, f: 15, A: 10, B: 11, C: 12, D: 13,
            E: 14, F: 15
        };

        function fromHex(hexString) {
            const bytes = new Uint8Array(Math.floor((hexString || "").length / 2));
            let i;
            for (i = 0; i < bytes.length; i++) {
              const a = MAP_HEX[hexString[i * 2]];
              const b = MAP_HEX[hexString[i * 2 + 1]];
              if (a === undefined || b === undefined) {
                break;
              }
              bytes[i] = (a << 4) | b;
            }
            return i === bytes.length ? bytes : bytes.slice(0, i);
        }

        function decode(data) {
            function convert(obj) {
                let buffer = fromHex(obj.buffer);
                return new Float32Array(buffer.buffer);
            }
        
            function walk(obj) {
                var type = null;
                for (var attr in obj) {
                    if (attr === "parts") {
                        for (var i in obj.parts) {
                            walk(obj.parts[i]);
                        }
        
                    } else if (attr === "type") {
                        type = obj.type;
        
                    } else if (attr === "shape") {
                        if (type === "shapes") {
                            if (obj.shape.ref === undefined) {
                                obj.shape.vertices = convert(obj.shape.vertices);
                                obj.shape.normals = convert(obj.shape.normals);
                                obj.shape.edges = convert(obj.shape.edges);
                            } else {
                                const ind = obj.shape.ref;
                                if (ind !== undefined) {
                                    obj.shape = instances[ind];
                                }
                            }
                        } else {
                            obj.shape = convert(obj.shape);
                        }
                    }
                }
            }

            const instances = data.data.instances;
            
            data.data.instances.forEach((instance) => {
                instance.vertices = convert(instance.vertices);
                instance.normals = convert(instance.normals);
                instance.edges = convert(instance.edges);
                instance.triangles = Uint32Array.from(instance.triangles);
            });

            walk(data.data.shapes);
            
            data.data.instances = []
        }

        function nc(change) {
            console.debug("Viewer:", JSON.stringify(change, null, 2));
            if (change.zoom !== undefined) {
                _zoom = change.zoom.new;
            }
            if (change.position !== undefined) {
                _position = change.position.new;
            }
            if (change.quaternion !== undefined) {
                _quaternion = change.quaternion.new;
            }
            if (change.target !== undefined) {
                _target = change.target.new;
            }
        }

        function getSize() {
            return {
                width: window.innerWidth || document.body.clientWidth,
                height: window.innerHeight || document.body.clientHeight
            }
        }
        
        function preset(config, val) {
            return (config === undefined) ? val : config;
        }

        function showViewer() {
            const size = getSize()
            const treeWidth = ${glass} ? 0: ${treeWidth};
            const minWidth = ${glass} ? 665 : 665 - ${treeWidth};
            
            const displayOptions = {
                cadWidth: Math.max(minWidth, size.width - treeWidth - 42),
                height: size.height - 65,
                treeWidth: treeWidth,
                theme: '${theme}',
                pinning: false,
            };    

            const container = document.getElementById("cad_viewer");
            container.innerHTML = ""
            viewer = new Viewer(container, displayOptions, nc);
            
            if (_states != null) {
                render(_shapes, _states, _config);
            }     
            
            // viewer.trimUI(["axes", "axes0", "grid", "ortho", "more", "help"])           
        }    

        function render(shapes, states, config) {
            _states = states;
            _shapes = shapes;
            _config = config;
            
            const tessellationOptions = {
                ambientIntensity: preset(config.ambient_intensity, 0.75),
                directIntensity: preset(config.direct_intensity, 0.15),
                edgeColor: preset(config.default_edgecolor, 0x707070),
                defaultOpacity: preset(config.default_opacity, 0.5),
                normalLen: preset(config.normal_len, 0),
            };


            const renderOptions = {
                axes: preset(config.axes, false),
                axes0: preset(config.axes0, false),
                blackEdges: preset(config.black_edges, false),
                grid: preset(config.grid, [false, false, false]),
                collapse: preset(config.collapse, 1),
                ortho: preset(config.ortho, true),
                ticks: preset(config.ticks, 10),
                timeit: preset(config.timeit, false),
                tools: preset(config.tools, ${tools}),
                glass: preset(config.glass, ${glass}),
                up: preset(config.up, '${up}'),
                transparent: preset(config.transparent, false),
                zoom: preset(config.zoom, 1.0),
                position: preset(config.position, null),
                quaternion: preset(config.quaternion, null),
                target: preset(config.target, null),
                control: preset(config.control, '${control}'),
                panSpeed: preset(config.panSpeed, ${panSpeed}),
                zoomSpeed: preset(config.zoomSpeed, ${zoomSpeed}),
                rotateSpeed: preset(config.rotateSpeed, ${rotateSpeed}),
            };

            viewer?.clear();

            var shapesStates = viewer.renderTessellatedShapes(shapes, states, tessellationOptions)
            
            if (config.reset_camera) {
                _zoom = null;
                _position = null;
                _quaternion = null;
                _target = null;                
            } else {
                if (_zoom !== null) {
                    renderOptions["zoom"] = _zoom;
                }
                if (_position !== null) {
                    renderOptions["position"] = _position;
                }
                if (_quaternion !== null) {
                    renderOptions["quaternion"] = _quaternion;
                }
                if (_target !== null) {
                    renderOptions["target"] = _target;
                }
            }
            
            viewer.render(
                ...shapesStates,
                states,
                renderOptions,
            );
        }

        window.addEventListener('resize', function(event) {         
            const displayOptions = getDisplayOptions();
            viewer.resizeCadView(displayOptions.cadWidth, displayOptions.treeWidth, displayOptions.height, displayOptions.glass);
        }, true);

        console.log("resize listener registered");

        window.addEventListener('message', event => {
            var data = JSON.parse(event.data);

            if (data.type === "data") {
                decode(data);

                let meshData = data.data;
                let config = data.config;
                showViewer(meshData.shapes, meshData.states, config);

            } else if (data.type === "animation") {
                const tracks = data.data;
                for (var track of tracks) {
                    viewer.addAnimationTrack(...track);
                }
                const duration = Math.max(
                    ...tracks.map((track) => Math.max(...track[2]))
                );
                if (data.config.speed > 0) {
                      viewer.initAnimation(duration, data.config.speed);
                }
            }
        });
        console.log("message listener registered");
        
    </script>
</head>

<body>
    <div id="cad_viewer"></div>
</body>

</html>
`;
    return html;
}
