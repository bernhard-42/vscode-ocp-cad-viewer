import * as THREE from "three";

class PlaneHelper extends THREE.Line {
  constructor(index, plane, center, size = 1, hex = 0xffff00) {
    const color = hex;

    const positions = [-1, -1, 1, -1, 1, 1, 1, 1, 1, 1, -1, 1, -1, -1, 1];

    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute(
      "position",
      new THREE.Float32BufferAttribute(positions, 3),
    );
    geometry.computeBoundingSphere();

    super(
      geometry,
      new THREE.LineBasicMaterial({ color: color, toneMapped: false }),
    );

    this.type = "PlaneHelper";
    this.index = index;

    this.plane = plane;
    this.size = size;
    this.center = center;

    const positions2 = [
      1, 1, 1, -1, 1, 1, -1, -1, 1, 1, 1, 1, -1, -1, 1, 1, -1, 1,
    ];
    const geometry2 = new THREE.BufferGeometry();
    geometry2.setAttribute(
      "position",
      new THREE.Float32BufferAttribute(positions2, 3),
    );
    geometry2.computeBoundingSphere();

    this.planeMesh = new THREE.Mesh(
      geometry2,
      new THREE.MeshBasicMaterial({
        color: color,
        opacity: 0.05,
        transparent: true,
        depthWrite: false,
        toneMapped: false,
      }),
    );
    this.add(this.planeMesh);
  }

  updateMatrixWorld(force) {
    let scale = -this.plane.constant;

    if (Math.abs(scale) < 1e-8) scale = 1e-8; // sign does not matter

    this.scale.set(0.5 * this.size, 0.5 * this.size, scale);

    // this.children[0].material.side = (scale < 0) ? THREE.BackSide : THREE.FrontSide; // renderer flips side when determinant < 0; flipping not wanted here
    this.children[0].material.side = THREE.DoubleSide;
    this.lookAt(this.plane.normal);

    super.updateMatrixWorld(force);
  }
}

class Clipping {
  constructor(center, size, distance, uiCallback, theme) {
    this.distance = distance;
    this.uiCallback = uiCallback;

    const normals = [
      new THREE.Vector3(-1, 0, 0),
      new THREE.Vector3(0, -1, 0),
      new THREE.Vector3(0, 0, -1),
    ];

    this.clipPlanes = [];

    for (var i = 0; i < 3; i++) {
      this.clipPlanes.push(new THREE.Plane(normals[i], distance));
      this.uiCallback(i, normals[i].toArray());
    }

    this.planeHelpers = new THREE.Group();
    this.planeHelpers.add(
      new PlaneHelper(
        0,
        this.clipPlanes[0],
        center,
        size,
        theme === "light" ? 0xff0000 : 0xff4500,
      ),
    );
    this.planeHelpers.add(
      new PlaneHelper(
        1,
        this.clipPlanes[1],
        center,
        size,
        theme === "light" ? 0x00ff00 : 0x32cd32,
      ),
    );
    this.planeHelpers.add(
      new PlaneHelper(
        2,
        this.clipPlanes[2],
        center,
        size,
        theme === "light" ? 0x0000ff : 0x3b9eff,
      ),
    );
    this.planeHelpers.visible = false;
  }

  setConstant(index, value) {
    this.clipPlanes[index].constant = value;
  }

  setNormal = (index, normal) => {
    this.clipPlanes[index].normal = normal;
    this.uiCallback(index, normal.toArray());
  };
}

export { Clipping };
