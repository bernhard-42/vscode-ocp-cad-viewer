import * as THREE from "three";
import { LineSegments2 } from "three/examples/jsm/lines/LineSegments2.js";
import { LineSegmentsGeometry } from "./patches.js";
import { LineMaterial } from "three/examples/jsm/lines/LineMaterial.js";
import { VertexNormalsHelper } from "three/examples/jsm/helpers/VertexNormalsHelper.js";
import { BoundingBox } from "./bbox.js";

class ObjectGroup extends THREE.Group {
  constructor(opacity, alpha, edge_color, renderback) {
    super();
    this.opacity = opacity;
    this.alpha = (alpha == null) ? 1.0 : alpha;
    this.edge_color = edge_color;
    this.renderback = renderback;
    this.types = { front: null, back: null, edges: null, vertrices: null };
  }

  addType(mesh, type) {
    this.add(mesh);
    this.types[type] = mesh;
  }

  setTransparent(flag) {
    if (this.types.back) {
      this.types.back.material.opacity = flag ? this.opacity * this.alpha : this.alpha;
      this.types.front.material.opacity = flag ? this.opacity * this.alpha : this.alpha;
    }
    for (var child of this.children) {
      // turn depth write off for transparent objects
      child.material.depthWrite = (this.alpha < 1.0) ? false : !flag;
      // but keep depth test
      child.material.depthTest = true;
      child.material.needsUpdate = true;
    }
  }

  setBlackEdges(flag) {
    if (this.types.edges) {
      const color = flag ? 0x000000 : this.edge_color;
      this.types.edges.material.color = new THREE.Color(color);
      this.types.edges.material.needsUpdate = true;
    }
  }

  setEdgeColor(color) {
    if (this.types.edges) {
      this.edge_color = color;
      this.types.edges.material.color = new THREE.Color(color);
      this.types.edges.material.needsUpdate = true;
    }
  }

  setOpacity(opacity) {
    if (this.types.front || this.types.back) {
      this.opacity = opacity;
      this.types.back.material.opacity = this.opacity;
      this.types.front.material.opacity = this.opacity;
      this.types.back.material.needsUpdate = true;
      this.types.front.material.needsUpdate = true;
    }
  }

  setShapeVisible(flag) {
    this.types.front.material.visible = flag;
    if (this.types.back && this.renderback) {
      this.types.back.material.visible = flag;
    }
  }

  setEdgesVisible(flag) {
    if (this.types.edges) {
      this.types.edges.material.visible = flag;
    }
    if (this.types.vertices) {
      this.types.vertices.material.visible = flag;
    }
  }

  setBackVisible(flag) {
    if (this.types.back && this.types.front.material.visible) {
      this.types.back.material.visible = this.renderback || flag;
    }
  }

  setClipIntersection(flag) {
    for (var child of this.children) {
      child.material.clipIntersection = flag;
      child.material.clipIntersection = flag;
      child.material.clipIntersection = flag;
    }
  }

  setClipPlanes(planes) {
    if (this.types.back) {
      this.types.back.material.clippingPlanes = planes;
    }
    if (this.types.front) {
      this.types.front.material.clippingPlanes = planes;
    }
    if (this.types.edges) {
      this.types.edges.material.clippingPlanes = planes;
    }
    if (this.types.vertices) {
      this.types.vertices.material.clippingPlanes = planes;
    }
    this.updateMaterials(true);
  }

  setPolygonOffset(offset) {
    if (this.types.back) {
      this.types.back.material.polygonOffsetUnits = offset;
    }
  }

  updateMaterials(flag) {
    if (this.types.back) {
      this.types.back.material.needsUpdate = flag;
    }
    if (this.types.front) {
      this.types.front.material.needsUpdate = flag;
    }
    if (this.types.edges) {
      this.types.edges.material.needsUpdate = flag;
    }
    if (this.types.vertices) {
      this.types.vertices.material.needsUpdate = flag;
    }
  }
}

class NestedGroup {
  constructor(
    shapes,
    width,
    height,
    edgeColor,
    transparent,
    opacity,
    normalLen,
    bb_max,
  ) {
    this.shapes = shapes;
    this.width = width;
    this.height = height;
    this.edgeColor = edgeColor;
    this.transparent = transparent;
    this.defaultOpacity = opacity;
    this.normalLen = normalLen;
    this.blackEdges = false;
    this.backVisible = false;
    this.bb_max = bb_max;
    this.delim = "|";
    this.rootGroup = null;
    this.bbox = null;
    this.bsphere = null;
    this.groups = {};

    this.clipPlanes = null;
  }

  _dump(ind) {
    if (ind == undefined) {
      ind = "";
    }
    if (this.parts) {
      for (var part of this.parts) {
        this._dump(part, ind + "  ");
      }
    }
  }

  _renderEdges(edgeList, lineWidth, color, state) {
    var positions =
      edgeList instanceof Float32Array
        ? edgeList
        : new Float32Array(edgeList.flat(2));

    const lineGeometry = new LineSegmentsGeometry();
    lineGeometry.setPositions(positions);

    const lineMaterial = new LineMaterial({
      linewidth: lineWidth,
      transparent: true,
      depthWrite: !this.transparent,
      depthTest: !this.transparent,
      clipIntersection: false,
    });

    if (Array.isArray(color)) {
      var colors = color
        .map((c) => [
          new THREE.Color(c).toArray(),
          new THREE.Color(c).toArray(),
        ])
        .flat(2);
      lineGeometry.setColors(colors);
      lineMaterial.vertexColors = "VertexColors";
    } else {
      lineMaterial.color = new THREE.Color(
        color == null ? this.edgeColor : color,
      );
    }
    lineMaterial.visible = state == 1;
    lineMaterial.resolution.set(this.width, this.height);

    var edges = new LineSegments2(lineGeometry, lineMaterial);
    edges.renderOrder = 999;

    return edges;
  }

  renderEdges(edgeList, lineWidth, color, name, state) {
    var group = new ObjectGroup(
      this.defaultOpacity,
      1.0,
      color == null ? this.edgeColor : color,
    );

    var edges = this._renderEdges(edgeList, lineWidth, color, state);
    if (name) {
      edges.name = name;
    }
    group.addType(edges, "edges");

    return group;
  }

  renderVertices(vertexList, size, color, name, state) {
    var group = new ObjectGroup(
      this.defaultOpacity,
      1.0,
      color == null ? this.edgeColor : color,
    );

    const vertex_color = color == null ? this.edgeColor : color;

    const positions =
      vertexList instanceof Float32Array
        ? vertexList
        : new Float32Array(vertexList.flat());

    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute(
      "position",
      new THREE.Float32BufferAttribute(positions, 3),
    );

    const material = new THREE.PointsMaterial({
      color: vertex_color,
      sizeAttenuation: false,
      size: size,
      transparent: true,
      clipIntersection: false,
      visible: state == 1,
    });

    var points = new THREE.Points(geometry, material);
    if (name) {
      points.name = name;
    }
    group.addType(points, "vertices");

    return group;
  }

  renderShape(shape, color, alpha, renderback, name, states) {
    const positions =
      shape.vertices instanceof Float32Array
        ? shape.vertices
        : new Float32Array(shape.vertices.flat());
    const normals =
      shape.normals instanceof Float32Array
        ? shape.normals
        : new Float32Array(shape.normals.flat());
    const triangles =
      shape.triangles instanceof Uint32Array
        ? shape.triangles
        : new Uint32Array(shape.triangles.flat());

    var group = new ObjectGroup(
      this.defaultOpacity,
      alpha,
      this.edgeColor,
      renderback,
    );
    
    if (alpha == null) {
      alpha = 1.0;
    } else if (alpha < 1.0) {
      this.transparent = true;
    }
    var shapeGeometry = new THREE.BufferGeometry();
    shapeGeometry.setAttribute(
      "position",
      new THREE.BufferAttribute(positions, 3),
    );
    shapeGeometry.setAttribute("normal", new THREE.BufferAttribute(normals, 3));
    shapeGeometry.setIndex(new THREE.BufferAttribute(triangles, 1));

    // see https://stackoverflow.com/a/37651610
    // "A common draw configuration you see is to draw all the opaque object with depth testing on, 
    //  turn depth write off, then draw the transparent objects in a back to front order."

    const frontMaterial = new THREE.MeshStandardMaterial({
      color: color,
      polygonOffset: true,
      polygonOffsetFactor: 1.0,
      polygonOffsetUnits: 1.0,
      transparent: true,
      opacity: this.transparent ? this.defaultOpacity * alpha : alpha,
      // turn depth write off for transparent objects
      depthWrite: !this.transparent,
      // but keep depth test
      depthTest: true,
      clipIntersection: false,
      side: THREE.FrontSide,
      visible: states[0] == 1,
    });
    
    const backMaterial = new THREE.MeshBasicMaterial({
      color: new THREE.Color(this.edgeColor),
      side: THREE.BackSide,
      polygonOffset: true,
      polygonOffsetFactor: 1.0,
      polygonOffsetUnits: 1.0,
      transparent: true,
      opacity: this.transparent ? this.defaultOpacity * alpha : alpha,
      // turn depth write off for transparent objects
      depthWrite: !this.transparent,
      // but keep depth test
      depthTest: true,
      clipIntersection: false,
      visible: states[0] == 1 && (renderback || this.backVisible),
    });

    const front = new THREE.Mesh(shapeGeometry, frontMaterial);
    front.name = name;

    const back = new THREE.Mesh(shapeGeometry, backMaterial);
    back.name = name;
    
    // ensure, transparent objects will be rendered at the end
    if (alpha < 1.0) {
      back.renderOrder = 999;
      front.renderOrder = 999;
    }

    group.addType(back, "back");
    group.addType(front, "front");

    if (this.normalLen > 0) {
      const normalsHelper = new VertexNormalsHelper(
        front,
        this.normalLen,
        0xff00ff,
      );
      group.add(normalsHelper);
    }

    // group.add(new THREE.BoxHelper(front, 0x888888))

    const edgeList = shape.edges;
    if (edgeList.length > 0) {
      var edges = this._renderEdges(edgeList, 1, null, states[1]);
      edges.name = name;
      group.addType(edges, "edges");
    }

    return group;
  }

  renderLoop(shapes, path, states) {
    const _render = (shape) => {
      var mesh;
      switch (shape.type) {
        case "edges":
          mesh = this.renderEdges(
            shape.shape,
            shape.width,
            shape.color,
            shape.name,
            states[shape.id][1],
          );
          break;
        case "vertices":
          mesh = this.renderVertices(
            shape.shape,
            shape.size,
            shape.color,
            shape.name,
            states[shape.id][1],
          );
          break;
        default:
          mesh = this.renderShape(
            shape.shape,
            shape.color,
            shape.alpha,
            shape.renderback == null ? false : shape.renderback,
            shape.name,
            states[shape.id],
          );
      }
      return mesh;
    };

    var group = new THREE.Group();
    if (shapes.loc == null) {
      shapes.loc = [
        [0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
      ];
    }
    group.position.set(...shapes.loc[0]);
    group.quaternion.set(...shapes.loc[1]);

    path = path + this.delim + shapes.name;
    this.groups[path.replaceAll(this.delim, "/")] = group;
    group.name = path;

    for (var shape of shapes.parts) {
      if (shape.parts) {
        group.add(this.renderLoop(shape, path, states));
      } else {
        const objectGroup = _render(shape);
        this.groups[shape.id] = objectGroup;
        group.add(objectGroup);
      }
    }
    return group;
  }

  render(states) {
    this.rootGroup = this.renderLoop(this.shapes, "", states);
    return this.rootGroup;
  }

  boundingBox() {
    if (this.bbox == null) {
      this.bbox = new BoundingBox();
      this.bbox.setFromObject(this.rootGroup, true);
    }
    return this.bbox;
  }

  _traverse(func, flag) {
    for (var path in this.groups) {
      for (var obj of this.groups[path].children) {
        if (obj instanceof ObjectGroup) {
          obj[func](flag);
        }
      }
    }
  }

  setTransparent(flag) {
    this.transparent = flag;
    this._traverse("setTransparent", flag);
  }

  setBlackEdges(flag) {
    this.blackEdges = flag;
    this._traverse("setBlackEdges", flag);
  }

  setBackVisible(flag) {
    this.backVisible = flag;
    this._traverse("setBackVisible", flag);
  }

  setEdgeColor(color) {
    this.edge_color = color;
    this._traverse("setEdgeColor", color);
  }

  setOpacity(opacity) {
    this.opacity = opacity;
    this._traverse("setOpacity", opacity);
  }

  setClipIntersection(flag) {
    this._traverse("setClipIntersection", flag);
  }

  setClipPlanes(planes) {
    this.clipPlanes = planes;
    this._traverse("setClipPlanes", planes);
  }

  setPolygonOffset(offset) {
    this._traverse("setPolygonOffset", offset);
  }

  updateMaterials() {
    this._traverse("updateMaterials", true);
  }
}

export { NestedGroup, ObjectGroup };
