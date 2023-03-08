import * as THREE from "three";
import { AxesHelper } from "./axes.js";
import { sceneTraverse } from "./utils.js";

class OrientationMarker {
  constructor(width, height, camera, theme) {
    this.width = width;
    this.height = height;
    this.cad_camera = camera;
    this.theme = theme;
    this.camera = null;
    this.scene = null;
    this.renderer = null;
  }

  create() {
    const size = 2.7;
    const length = 60;

    // scene
    this.scene = new THREE.Scene();

    // camera
    this.camera = new THREE.OrthographicCamera(
      -this.width,
      this.width,
      this.height,
      -this.height,
      1,
      1000,
    );
    this.camera.up = this.cad_camera.up; // important!
    this.camera.lookAt(new THREE.Vector3(0, 0, 0));

    // axes
    const axes = new AxesHelper(
      [0, 0, 0],
      length,
      size,
      this.width,
      this.height,
      true,
      true,
      this.theme,
    );
    this.scene.add(axes);

    const colors =
      this.theme === "dark"
        ? [
            [1, 0x45 / 255, 0],
            [0x32 / 255, 0xcd / 255, 0x32 / 255],
            [0x3b / 255, 0x9e / 255, 1],
          ]
        : [
            [1, 0, 0],
            [0, 0.7, 0],
            [0, 0, 1],
          ];
    this.cones = [];
    for (var i = 0; i < 3; i++) {
      var coneGeometry = new THREE.CylinderGeometry(
        0,
        3 * size,
        6 * size,
        20,
        1,
      );
      const coneMaterial = new THREE.MeshBasicMaterial({
        color: new THREE.Color(...colors[i]),
        toneMapped: false,
      });
      const cone = new THREE.Mesh(coneGeometry, coneMaterial);
      cone.matrixAutoUpdate = false;
      this.cones.push(cone);
    }

    this.cones[0].geometry.rotateZ(-Math.PI / 2);
    this.cones[0].geometry.translate(length, 0, 0);
    this.cones[1].geometry.translate(0, length, 0);
    this.cones[2].geometry.rotateX(Math.PI / 2);
    this.cones[2].geometry.translate(0, 0, length);

    this.scene.add(...this.cones);

    const geometry = new THREE.SphereGeometry(3 * size, 20, 20);
    const material = new THREE.MeshBasicMaterial({ color: 0xa0a0a0 });
    const sphere = new THREE.Mesh(geometry, material);
    this.scene.add(sphere);

    this.scene.background = null;
  }

  dispose() {
    sceneTraverse(this.scene, (o) => {
      o.geometry?.dispose();
      o.material?.dispose();
    });
    this.scene = null;
    this.camera = null;
  }

  render(renderer) {
    renderer.setViewport(0, 0, this.width, this.height);

    renderer.render(this.scene, this.camera);
  }

  // handler (bound to OrientationMarker instance)

  update(position, rotation) {
    this.camera.position.copy(position);
    this.camera.position.setLength(300);
    this.camera.rotation.copy(rotation);
  }
}

export { OrientationMarker };
