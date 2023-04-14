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
    let options = vscode.workspace.getConfiguration("OcpCadViewer.view");
    let theme = options.get("dark") ? "dark" : "light";
    let treeWidth = options.get("tree_width");
    let control = options.get("orbit_control") ? "orbit" : "trackball";
    let up = options.get("up");
    let glass = options.get("glass");
    let tools = options.get("tools");
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
        var viewerOptions = {};
        const minWidth = 665;
        const vscode = acquireVsCodeApi();
        var message = {};

        const displayDefaultOptions = {
            cadWidth: 730,
            height: 525,
            treeWidth: ${treeWidth},
            glass: ${glass},
            theme: '${theme}',
            pinning: false,
        };   

        const viewerDefaultOptions = {
            timeit: false,
            tools: ${tools},
            glass: ${glass},
            up: '${up}',
            zoom: 1.0,
            position: null,
            quaternion: null,
            target: null,
            control: '${control}',
        };
        
        const renderDefaultOptions = {
            ambientIntensity:  0.75,
            directIntensity:  0.15,
            edgeColor:  0x707070,
            defaultOpacity:  0.5,
            normalLen:  0,
            angularTolerance: 0.2,
            deviation: 0.1,
            defaultColor: "#e8b024"
        };
        
        // console.log("displayDefaultOptions", displayDefaultOptions);
        // console.log("viewerDefaultOptions", viewerDefaultOptions);
        // console.log("renderDefaultOptions", renderDefaultOptions);

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

            var changed = false;
            Object.keys(change).forEach((k) => {
                if(change[k].new !== undefined) {
                    message[k] = change[k].new;
                    changed = true;
                }
            });
            if (changed) {
                vscode.postMessage(JSON.stringify({
                    command: 'status',
                    text: message
                }))    
            }       
        }

        function normalizeWidth(width, glass) {
            const treeWidth = glass ? 0: preset(_config.treeWidth, displayDefaultOptions.treeWidth);
            return Math.max(minWidth, width - treeWidth - 42);
        }

        function normalizeHeight(height) {
            return height - 65;
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

        function getDisplayOptions() {
            const size = getSize()
            const glass = preset(_config.glass, displayDefaultOptions.glass)
            const treeWidth = glass ? 0: preset(_config.treeWidth, displayDefaultOptions.treeWidth);
            return {
                glass: glass,
                treeWidth: treeWidth,
                cadWidth: normalizeWidth(size.width, glass),
                height: normalizeHeight(size.height) 
            }            
        }

        function showViewer(shapes, states, config) {
            _shapes = shapes;
            _states = states;
            _config = config;

            const displayOptions = getDisplayOptions();

            const container = document.getElementById("cad_viewer");
            container.innerHTML = ""
            viewer = new Viewer(container, displayOptions, nc);
            
            render();
            // viewer.trimUI(["axes", "axes0", "grid", "ortho", "more", "help"])           
        }    

        function render() {
            const renderOptions = {
                ambientIntensity: preset(_config.ambient_intensity, renderDefaultOptions.ambientIntensity),
                directIntensity: preset(_config.direct_intensity, renderDefaultOptions.directIntensity),
                edgeColor: preset(_config.default_edgecolor, renderDefaultOptions.defaultEdgecolor),
                defaultOpacity: preset(_config.default_opacity, renderDefaultOptions.defaultOpacity),
                normalLen: preset(_config.normal_len, renderDefaultOptions.normalLen),
            };
            // console.log("renderOptions", renderOptions)
            
            viewerOptions = {
                axes: preset(_config.axes, viewerDefaultOptions.axes),
                axes0: preset(_config.axes0, viewerDefaultOptions.axes0),
                blackEdges: preset(_config.black_edges, viewerDefaultOptions.black_edges),
                grid: preset(_config.grid, viewerDefaultOptions.grid),
                collapse: preset(_config.collapse, viewerDefaultOptions.collapse),
                ortho: preset(_config.ortho, viewerDefaultOptions.ortho),
                ticks: preset(_config.ticks, viewerDefaultOptions.ticks),
                timeit: preset(_config.timeit, viewerDefaultOptions.timeit),
                tools: preset(_config.tools, viewerDefaultOptions.tools),
                glass: preset(_config.glass, viewerDefaultOptions.glass),
                up: preset(_config.up, viewerDefaultOptions.up),
                transparent: preset(_config.transparent, viewerDefaultOptions.transparent),
                control: preset(_config.control, viewerDefaultOptions.control),
                panSpeed: preset(_config.pan_speed, viewerDefaultOptions.panSpeed),
                zoomSpeed: preset(_config.zoom_speed, viewerDefaultOptions.zoomSpeed),
                rotateSpeed: preset(_config.rotate_speed, viewerDefaultOptions.rotateSpeed),
            };
            // console.log("viewerOptions", viewerOptions)
            if (_config.zoom !== undefined) {
                viewerOptions.zoom = _config.zoom;
            }
            if (_config.position !== undefined) {
                viewerOptions.position = _config.position;
            }
            if (viewerOptions.quaternion !== undefined) {
                viewerOptions.quaternion = _config.quaternion;
            }
            if (viewerOptions.target !== undefined) {
                viewerOptions.target = _config.target;
            }
            
            var shapesAndTree = viewer.renderTessellatedShapes(_shapes, _states, renderOptions)
            
            if (preset(_config.reset_camera, true)) {
                _zoom = null;
                _position = null;
                _quaternion = null;
                _target = null;                
            } else {
                if (_zoom !== null) {
                    viewerOptions["zoom"] = _zoom;
                }
                if (_position !== null) {
                    viewerOptions["position"] = _position;
                }
                if (_quaternion !== null) {
                    viewerOptions["quaternion"] = _quaternion;
                }
                if (_target !== null) {
                    viewerOptions["target"] = _target;
                }
            }
            
            viewer.render(
                ...shapesAndTree,
                _states,
                viewerOptions,
            );
            console.log(viewer)
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
