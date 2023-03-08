import * as THREE from "three";

import { CameraControls } from "./controls/CameraControls.js";

class Controls {
  /**
   * Create Camera Controls.
   * @param {string} type - Type of controls: "orbit", "trackball".
   * @param {THREE.Camera} camera - The camera object.
   * @param {THREE.Vector3} target - The lookAt target for the camera.
   * @param {canvas} domElement - The dom element of the rendering canvas.
   * @param {number} [rotateSpeed=1.0] - Speed for rotating.
   * @param {number} [zoomSpeed=1.0] - Speed for zooming.
   * @param {number} [panSpeed=1.0] - Speed for panning.
   */
  constructor(
    type,
    camera,
    target,
    domElement,
    rotateSpeed = 1.0,
    zoomSpeed = 1.0,
    panSpeed = 1.0,
  ) {
    this.type = type;
    this.camera = camera;
    this.target = target;
    this.target0 = target.slice();
    this.domElement = domElement;
    this.rotateSpeed = rotateSpeed;
    this.zoomSpeed = zoomSpeed;
    this.panSpeed = panSpeed;

    switch (type) {
      case "orbit":
        this.initOrbitControls();
        break;
      case "trackball":
        this.initTrackballControls();
        break;
    }

    this.controls.target = new THREE.Vector3(...this.target);
    this.controls.rotateSpeed = this.rotateSpeed;
    this.controls.zoomSpeed = this.zoomSpeed;
    this.controls.panSpeed = this.panSpeed;

    this.currentUpdateCallback = null;

    // save default view for reset
    this.saveState();
    this.update();
  }

  /**
   * Remove assets and event handlers.
   */
  dispose() {
    this.controls.dispose();
    this.controls = null;
  }

  /**
   * Save state for reset.
   */
  saveState() {
    this.controls.saveState();
  }

  /**
   * Initialize Trackball Controls.
   * @param {boolean} [holroyd=true] - enable holroyd (non tumbling) mode.
   **/
  initTrackballControls(holroyd = true) {
    this.controls = new CameraControls(this.camera, this.domElement);
    this.controls.trackball = true;
    this.setHolroydTrackball(holroyd);
  }

  /**
   * Initialize Orbit Controls.
   **/
  initOrbitControls() {
    this.controls = new CameraControls(this.camera, this.domElement);
  }

  /**
   * Add an event listener callback for the "change" event.
   * @param {callback} domEventCallback - the callback function.
   **/
  addChangeListener(callback) {
    if (this.currentUpdateCallback == null) {
      this.currentUpdateCallback = callback;
      this.controls.addEventListener("change", callback);
    }
  }

  /**
   * Remove the event listener callback for the "change" event.
   **/
  removeChangeListener() {
    if (this.currentUpdateCallback != null) {
      this.controls.removeEventListener("change", this.currentUpdateCallback);
      this.currentUpdateCallback = null;
    }
  }

  /**
   * Update controls after camera position, zoom or quaternion changes.
   **/
  update() {
    this.controls.update();
  }

  /**
   * Reset camera to initial (automatically saved) state of position, up, quaternion and zoom.
   **/
  reset() {
    this.controls.reset();
  }

  /**
   * Set the camera to be controlled.
   * @param {THREE.Camera} camera - a threejs Camera object.
   **/
  setCamera(camera) {
    this.controls.object = camera;
  }

  /**
   * Change the trackball holroyd (non tumbling) flag.
   * @param {boolean} flag - a threejs Camera object.
   **/
  setHolroydTrackball(flag) {
    this.controls.holroyd = flag;
  }

  /**
   * Get the lookAt target of the camera.
   * @returns {THREE.Vector3} The lookAt target
   **/
  getTarget() {
    return this.controls.target;
  }

  /**
   * Get the initial zoom value of the camera.
   **/
  getZoom0() {
    return this.controls.zoom0;
  }

  /**
   * Get the lookAt target of the camera.
   * @param {number[]} target - camera target as THREE.Vector3.
   **/
  setTarget(target) {
    this.controls.target.copy(target);
  }

  /**
   * Set the zoom speed.
   * @param {number} val - the speed value.
   **/
  setZoomSpeed(val) {
    this.controls.zoomSpeed = val;
  }

  /**
   * Set the pan speed.
   * @param {number} val - the speed value.
   **/
  setPanSpeed(val) {
    this.controls.panSpeed = val;
  }

  /**
   * Set the rotate speed.
   * @param {number} val - the speed value.
   **/
  setRotateSpeed(val) {
    this.controls.rotateSpeed = val;
  }

  /**
   * Get reset location value.
   * @function
   * @returns {object} - target, position, quaternion, zoom as object.
   */
  getResetLocation = () => {
    return {
      target0: this.controls.target0.clone(),
      position0: this.controls.position0.clone(),
      quaternion0: this.controls.quaternion0.clone(),
      zoom0: this.controls.zoom0,
    };
  };

  /**
   * Set reset location value.
   * @function
   * @param {number[]} target - camera target as THREE.Vector3.
   * @param {number[]} position - camera position as THREE.Vector3.
   * @returns {number[]} camera rotation as THREE.Quaternion.
   * @param {boolean} [notify=true] - whether to send notification or not.
   */
  setResetLocation = (target, position, quaternion, zoom) => {
    this.controls.target0.copy(target);
    this.controls.position0.copy(position);
    this.controls.quaternion0.copy(quaternion);
    this.controls.zoom0 = zoom;
  };

  // Rotations for OrbitControls

  /**
   * Rotate camera up (OrbitControls only)
   * @param {number} angle - the angle to rotate.
   **/
  rotateUp(angle) {
    this.controls.rotateUp((-angle / 180) * Math.PI);
    this.update();
  }

  /**
   * Rotate camera left (OrbitControls only)
   * @param {number} angle - the angle to rotate.
   **/
  rotateLeft(angle) {
    this.controls.rotateLeft((angle / 180) * Math.PI);
    this.update();
  }

  // Rotations for TrackballControls

  /**
   * Rotate camera around x-axis (TrackballControls only)
   * @param {number} angle - the angle to rotate.
   **/
  rotateX(angle) {
    this.controls.rotateX((angle / 180) * Math.PI);
    this.update();
  }

  /**
   * Rotate camera around y-axis (TrackballControls only)
   * @param {number} angle - the angle to rotate.
   **/
  rotateY(angle) {
    this.controls.rotateY((angle / 180) * Math.PI);
    this.update();
  }

  /**
   * Rotate camera around z-axis (TrackballControls only)
   * @param {number} angle - the angle to rotate.
   **/
  rotateZ(angle) {
    this.controls.rotateZ((angle / 180) * Math.PI);
    this.update();
  }
}

export { Controls };
