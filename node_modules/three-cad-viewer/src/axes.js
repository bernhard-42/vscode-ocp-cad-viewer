import { LineSegments2 } from "three/examples/jsm/lines/LineSegments2.js";
import { LineSegmentsGeometry } from "./patches.js";
import { LineMaterial } from "three/examples/jsm/lines/LineMaterial.js";

class AxesHelper extends LineSegments2 {
  constructor(center, size, lineWidth, width, height, axes0, visible, theme) {
    // prettier-ignore
    const vertices = new Float32Array([
            0, 0, 0, size, 0, 0,
            0, 0, 0, 0, size, 0,
            0, 0, 0, 0, 0, size
        ]);
    // prettier-ignore
    const colors = (theme === "dark") ?
            [
                1,          0x45 / 255, 0,          1,          0x45 / 255, 0,           // x
                0x32 / 255, 0xcd / 255, 0x32 / 255, 0x32 / 255, 0xcd / 255, 0x32 / 255,  // y
                0x3b / 255, 0x9e / 255, 1,          0x3b / 255, 0x9e / 255, 1            // z
            ] :
            [
                1, 0,   0, 1, 0,   0,  // x
                0, 0.7, 0, 0, 0.7, 0,  // y
                0, 0,   1, 0, 0,   1   // z
            ];

    const geometry = new LineSegmentsGeometry();
    geometry.setPositions(vertices);
    geometry.setColors(new Float32Array(colors));

    const material = new LineMaterial({
      vertexColors: true,
      toneMapped: false,
      linewidth: lineWidth,
      transparent: true,
    });
    material.resolution.set(width, height);

    super(geometry, material);

    this.center = center;

    this.type = "AxesHelper";
    this.visible = visible;
    this.setCenter(axes0);
  }

  dispose() {
    this.geometry.dispose();
    this.material.dispose();
  }

  setCenter(axes0) {
    if (axes0) {
      this.position.set(0, 0, 0);
    } else {
      this.position.set(...this.center);
    }
  }

  setVisible(visible) {
    this.visible = visible;
  }
}

export { AxesHelper };
