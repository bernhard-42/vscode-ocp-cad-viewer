import * as THREE from "three";

class Grid {
  constructor(display, bbox, ticks, axes0, grid, flipY) {
    if (ticks === undefined) {
      ticks = 10;
    }
    this.display = display;
    this.bbox = bbox;

    this.grid = grid;
    this.allGrid = grid[0] | grid[1] | grid[2];

    this.gridHelper = [];
    // in case the bbox has the same siez as the nice grid there should be
    // a margin bewteen grid and object. Hence factor 1.1
    var [axisStart, axisEnd, niceTick] = this.niceBounds(
      -bbox.max_dist_from_center() * 1.1,
      bbox.max_dist_from_center() * 1.1,
      2 * ticks,
    );
    this.size = axisEnd - axisStart;

    this.ticks = niceTick;

    for (var i = 0; i < 3; i++) {
      this.gridHelper.push(
        new THREE.GridHelper(
          this.size,
          this.size / this.ticks,
          0x888888,
          0xcccccc,
        ),
      );
    }

    this.gridHelper[0].rotateX(Math.PI / 2);
    this.gridHelper[1].rotateY(Math.PI / 2);
    this.gridHelper[2].rotateZ(Math.PI / 2);

    this.setCenter(axes0, flipY);

    this.setVisible();
  }

  // https://stackoverflow.com/questions/4947682/intelligently-calculating-chart-tick-positions
  niceNumber(value, round) {
    var exponent = Math.floor(Math.log10(value));
    var fraction = value / 10 ** exponent;

    var niceFraction;

    if (round) {
      if (fraction < 1.5) {
        niceFraction = 1.0;
      } else if (fraction < 3.0) {
        niceFraction = 2.0;
      } else if (fraction < 7.0) {
        niceFraction = 5.0;
      } else {
        niceFraction = 10.0;
      }
    } else {
      if (fraction <= 1) {
        niceFraction = 1.0;
      } else if (fraction <= 2) {
        niceFraction = 2.0;
      } else if (fraction <= 5) {
        niceFraction = 5.0;
      } else {
        niceFraction = 10.0;
      }
    }
    return niceFraction * 10 ** exponent;
  }

  niceBounds(axisStart, axisEnd, numTicks) {
    var niceTick;
    var niceRange;

    if (!numTicks) {
      numTicks = 10;
    }

    var axisWidth = axisEnd - axisStart;

    if (axisWidth == 0) {
      niceTick = 0;
    } else {
      niceRange = this.niceNumber(axisWidth);
      niceTick = this.niceNumber(niceRange / (numTicks - 1), true);
      axisStart = Math.floor(axisStart / niceTick) * niceTick;
      axisEnd = Math.ceil(axisEnd / niceTick) * niceTick;
    }
    return [axisStart, axisEnd, niceTick];
  }

  computeGrid() {
    this.allGrid = this.grid[0] | this.grid[1] | this.grid[2];

    this.display.checkElement("tcv_grid", this.allGrid);
    this.display.checkElement("tcv_grid-xy", this.grid[0]);
    this.display.checkElement("tcv_grid-xz", this.grid[1]);
    this.display.checkElement("tcv_grid-yz", this.grid[2]);

    this.setVisible();
  }

  setGrid(action) {
    switch (action) {
      case "grid":
        this.allGrid = !this.allGrid;
        this.grid[0] = this.allGrid;
        this.grid[1] = this.allGrid;
        this.grid[2] = this.allGrid;
        break;
      case "grid-xy":
        this.grid[0] = !this.grid[0];
        break;
      case "grid-xz":
        this.grid[1] = !this.grid[1];
        break;
      case "grid-yz":
        this.grid[2] = !this.grid[2];
        break;
    }
    this.computeGrid();
  }

  setGrids(xy, xz, yz) {
    this.grid[0] = xy;
    this.grid[1] = xz;
    this.grid[2] = yz;
    this.computeGrid();
  }

  setCenter(axes0, flipY) {
    if (axes0) {
      for (var i = 0; i < 3; i++) {
        this.gridHelper[i].position.set(0, 0, 0);
      }
      this.gridHelper[0].position.z = -this.size / 2;
      this.gridHelper[1].position.y = ((flipY ? 1 : -1) * this.size) / 2;
      this.gridHelper[2].position.x = -this.size / 2;
    } else {
      const c = this.bbox.center();
      for (i = 0; i < 3; i++) {
        this.gridHelper[i].position.set(...c);
      }
      this.gridHelper[0].position.z = -this.size / 2 + c[2];
      this.gridHelper[1].position.y = ((flipY ? 1 : -1) * this.size) / 2 + c[1];
      this.gridHelper[2].position.x = -this.size / 2 + c[0];
    }
  }

  setVisible() {
    for (var i = 0; i < 3; i++) {
      this.gridHelper[i].visible = this.grid[i];
    }
  }
}

export { Grid };
