import { InstancedBufferGeometry } from "three";
import { LineSegmentsGeometry as _LineSegmentsGeometry } from "three/examples/jsm/lines/LineSegmentsGeometry.js";

class LineSegmentsGeometry extends _LineSegmentsGeometry {
  toJSON() {
    // skip the broken toJSON method of _LineSegmentsGeometry
    const data = InstancedBufferGeometry.prototype.toJSON.call(this);
    return data;
  }
}

export { LineSegmentsGeometry };

// minimum implementation

// const data = {
//     uuid: this.uuid,
//     type: "BufferGeometry",
//     data: {
//         "attributes": {
//             "positions": this.attributes.position.toJSON(),
//             "uv": this.attributes.uv.toJSON()
//         },
//         "boundingSphere": {
//             "center": this.boundingSphere.center.toArray(),
//             "radius": this.boundingSphere.radius
//         },
//         "index": {
//             type: this.index.array.constructor.name,
//             array: Array.prototype.slice.call(this.index.array)
//         }
//     }
// }
