import { getIconBackground } from "./icons.js";

function TEMPLATE(id) {

  var html = `
<div class="tcv_cad_viewer">
    <div class="tcv_cad_toolbar tcv_round">
        <span class="tcv_tooltip" data-tooltip="Show coordinate axis">
            <input class='tcv_axes tcv_check' id='tcv_axes_${id}' type="checkbox" />
            <label for='tcv_axes_${id}' class="tcv_label">Axes</label>
        </span>
        <div class="tcv_grid-dropdown">
            <input class='tcv_grid tcv_check' id='tcv_grid_${id}' type="checkbox" />
            <label for='tcv_grid_${id}' class="tcv_label">Grid</label>
            <div class="tcv_grid-content tcv_dropdown-content">
                <div class="tcv_tooltip" data-tooltip="Show xy grid">
                    <input class='tcv_grid-xy tcv_check tcv_dropdown-entry' id='tcv_grid-xy_${id}' type="checkbox">
                    <label for='tcv_grid-xy_${id}' class="tcv_label tcv_dropdown-entry">xy</label>
                </div>
                <div class="tcv_tooltip" data-tooltip="Show xz grid">
                    <input class='tcv_grid-xz tcv_check tcv_dropdown-entry' id='tcv_grid-xz_${id}' type="checkbox">
                    <label for='tcv_grid-xz_${id}' class="tcv_label tcv_dropdown-entry">xz</label>
                </div>
                <div class="tcv_tooltip" data-tooltip="Show yz grid">
                    <input class='tcv_grid-yz tcv_check tcv_dropdown-entry' id='tcv_grid-yz_${id}' type="checkbox">
                    <label for='tcv_grid-yz_${id}' class="tcv_label tcv_dropdown-entry">yz</label>
                </div>
            </div>
        </div>
        <span class="tcv_tooltip" data-tooltip="Move center of axis and grid to (0,0,0)">
            <input class='tcv_axes0 tcv_check' id='tcv_axes0_${id}' type="checkbox" /><label for='tcv_axes0_${id}'
                class="tcv_label">@0</label>
        </span>
        <span class="tcv_tooltip" data-tooltip="Toggle camera between orthographic and perspective view">
            <input class='tcv_ortho tcv_check' id='tcv_ortho_${id}' type="checkbox" /><label for='tcv_ortho_${id}'
                class="tcv_label">Ortho</label>
        </span>
        <span class="tcv_tooltip" data-tooltip="Reset view">
            <input class='tcv_reset tcv_btn' type="button" />
        </span>
        <span class="tcv_tooltip" data-tooltip="Fit view">
            <input class='tcv_resize tcv_btn' type="button" />
        </span>
        <span class="tcv_tooltip" data-tooltip="Switch to iso view">
            <input class='tcv_iso tcv_btn' type="button" />
        </span>
        <span class="tcv_tooltip" data-tooltip="Switch to front view">
            <input class='tcv_front tcv_btn' type="button" />
        </span>
        <span class="tcv_tooltip" data-tooltip="Switch to back view">
            <input class='tcv_rear tcv_btn' type="button" />
        </span>
        <span class="tcv_tooltip" data-tooltip="Switch to top view">
            <input class='tcv_top tcv_btn' type="button" />
        </span>
        <span class="tcv_tooltip" data-tooltip="Switch to bottom view">
            <input class='tcv_bottom tcv_btn' type="button" />
        </span>
        <span class="tcv_tooltip" data-tooltip="Switch to left view">
            <input class='tcv_left tcv_btn' type="button" />
        </span>
        <span class="tcv_tooltip" data-tooltip="Switch to right view">
            <input class='tcv_right tcv_btn' type="button" />
        </span>
        <div class="tcv_more-dropdown">
            <button class="tcv_more-btn">More<span class="tcv_more_icon">\u25BC</span></button>
            <span class="tcv_more-wrapper tcv_more-content tcv_dropdown-content">
               <span class="tcv_more_check" class="tcv_tooltip" data-tooltip="Toggle transparent objects">
                    <input class='tcv_transparent tcv_check tcv_dropdown-entry' id='tcv_transparent_${id}' type="checkbox" />
                    <label for='tcv_transparent_${id}' class="tcv_label tcv_dropdown-entry">Transparent</label>
                </span class="tcv_more_check">
                <span class="tcv_more_check" class="tcv_tooltip" data-tooltip="Toggle black edges">
                    <input class='tcv_black_edges tcv_check tcv_dropdown-entry' id='tcv_black_edges_${id}' type="checkbox" />
                    <label for='tcv_black_edges_${id}' class="tcv_label tcv_dropdown-entry">Black edges</label>
                </span class="tcv_more_check">
                <span class="tcv_more_check" class="tcv_explode_widget tcv_tooltip"
                    data-tooltip="Explode assembly (@0 determines explosion center)">
                    <input class='tcv_explode tcv_check tcv_dropdown-entry' id='tcv_explode_${id}' type="checkbox" />
                    <label for='tcv_explode_${id}' class="tcv_label tcv_dropdown-entry">Explode</label>
                </span class="tcv_more_check">
            </span>
        </div>

        <span class="tcv_align_right">
            <span class="tcv_tooltip" data-tooltip="Toggle help">
                <input class='tcv_help tcv_btn' type="button" />
            </span>
            <span class="tcv_tooltip" data-tooltip="Pin view as PNG image">
                <input class='tcv_pin tcv_btn' type="button" />
            </span>
        </span>
    </div>

    <div class="tcv_cad_body">
        <div class="tcv_cad_navigation">
            <div class="tcv_cad_tree tcv_round">
                <div class="tcv_tabnav">
                    <input class='tcv_tab_tree tcv_tab tcv_tab-left tcv_tab-selected' value="Tree" type="button" />
                    <input class='tcv_tab_clip tcv_tab tcv_tab-right tcv_tab-unselected' value="Clipping"
                        type="button" />
                </div>
                <div class="tcv_cad_tree_toggles">
                    <input class='tcv_collapse_singles tcv_btn tcv_small_btn' value="1" type="button" />
                    <input class='tcv_collapse_all tcv_btn tcv_small_btn' value="C" type="button" />
                    <input class='tcv_expand tcv_btn tcv_small_btn' value="E" type="button" />
                </div>
                <div class="tcv_box_content tcv_mac-scrollbar tcv_scroller">
                    <div class="tcv_cad_tree_container"></div>
                    <div class="tcv_cad_clip_container">
                        <div class="tcv_slider_group">
                            <div>
                                <span class="tcv_tooltip" data-tooltip="Set red clipping plane to view direction">
                                    <input class='tcv_btn_norm_plane1 tcv_btn tcv_plane' type="button" />
                                </span>
                                <span class="tcv_lbl_norm_plane1 tcv_label">N1 = (n/a, n/a, n/a)</span>
                            </div>
                            <div>
                                <input type="range" min="1" max="100" value="50"
                                    class="tcv_sld_value_plane1 tcv_clip_slider">
                                <input value=50 class="tcv_inp_value_plane1 tcv_clip_input"></input>
                            </div>
                        </div>
                        <div class="tcv_slider_group">
                            <div>
                                <span class="tooltip" data-tooltip="Set green clipping plane to view direction">
                                    <input class='tcv_btn_norm_plane2 tcv_btn tcv_plane' type="button" />
                                </span>
                                <span class="tcv_lbl_norm_plane2 tcv_label">N2 = (n/a, n/a, n/a)</span>
                            </div>
                            <div>
                                <input type="range" min="1" max="100" value="50"
                                    class="tcv_sld_value_plane2 tcv_clip_slider">
                                <input value=50 class="tcv_inp_value_plane2 tcv_clip_input"></input>
                            </div>
                        </div>
                        <div class="tcv_slider_group">
                            <div>
                                <span class="tooltip" data-tooltip="Set blue clipping plane to view direction">
                                    <input class='tcv_btn_norm_plane3 tcv_btn tcv_plane' type="button" />
                                </span>
                                <span class="tcv_lbl_norm_plane3 tcv_label">N3 = (n/a, n/a, n/a)</span>
                            </div>
                            <div>
                                <input type="range" min="1" max="100" value="50"
                                    class="tcv_sld_value_plane3 tcv_clip_slider">
                                <input value=50 class="tcv_inp_value_plane3 tcv_clip_input"></input>
                            </div>
                        </div>
                        <div class="tcv_clip_checks">
                            <span class="tcv_tooltip" data-tooltip="Use intersection clipping">
                                <span class="tcv_label">Intersection</span><input
                                    class='tcv_clip_intersection tcv_check' type="checkbox" />
                            </span>
                            <span class="tcv_tooltip" data-tooltip="Show clipping planes">
                                <span class="tcv_label">Planes</span><input
                                    class='tcv_clip_plane_helpers tcv_axes0 tcv_check' type="checkbox" />
                            </span>
                        </div>
                    </div>
                </div>
            </div>
            <div class="tcv_cad_info_wrapper">
                <div class="tcv_toggle_info_wrapper">
                    <span class="tooltip" data-tooltip="Open/close info box">
                        <input class='tcv_toggle_info tcv_btn tcv_small_info_btn' value="<" type="button" />
                    </span>
                </div>
                <div class="tcv_cad_info tcv_round">
                    <div class="tcv_box_content tcv_mac-scrollbar tcv_scroller">
                        <div class="tcv_cad_info_container"></div>
                    </div>
                </div>
            </div>
        </div>

        <div class="tcv_cad_view">
            <div class="tcv_cad_animation tcv_round">
                <span class="tcv_animation_label">E</span>
                <span><input type="range" min="0" max="1000" value="0"
                        class="tcv_animation_slider tcv_clip_slider"></span>
                <span class="tcv_tooltip" data-tooltip="Play animation"><input class='tcv_play tcv_btn'
                        type="button" /></span>
                <span class="tcv_tooltip" data-tooltip="Pause animation"><input class='tcv_pause tcv_btn'
                        type="button" /></span>
                <span class="tcv_tooltip" data-tooltip="Stop and reset animation"><input class='tcv_stop tcv_btn'
                        type="button" /></span>
            </div>

            <div class="tcv_cad_help tcv_round">
                <table class="tcv_cad_help_layout">
                    <tr>
                        <td></td>
                        <td><b>Mouse Navigation</b></td>
                    </tr>
                    <tr>
                        <td>Rotate</td>
                        <td>&lt;left mouse button&gt;</td>
                    </tr>
                    <tr>
                        <td>Rotate up / down</td>
                        <td>&lt;Ctrl&gt; + &lt;left mouse button&gt;</td>
                    </tr>
                    <tr>
                        <td>Rotate left / right</td>
                        <td>&lt;Meta&gt; + &lt;left mouse button&gt;</td>
                    </tr>
                    <tr>
                        <td>Pan</td>
                        <td>&lt;Shift&gt; + &lt;left mouse button&gt; or &lt;right mouse button&gt;</td>
                    </tr>
                    <tr>
                        <td>Zoom</td>
                        <td>&lt;mouse wheel&gt; or &lt;middle mouse button&gt;</td>
                    </tr>

                    <tr>
                        <td></td>
                        <td><b>Mouse Selection</b></td>
                    </tr>
                    <tr>
                        <td>Pick element</td>
                        <td>&lt;left mouse button&gt; double click</td>
                    </tr>
                    <tr>
                        <td></td>
                        <td>Click on navigation tree label</td>
                    </tr>
                    <tr>
                        <td></td>
                        <td>(Shows axis-aligned bounding box, AABB)</td>
                    </tr>
                    <tr>
                        <td>Hide element</td>
                        <td>&lt;Meta&gt; + &lt;left mouse button&gt; double click</td>
                    </tr>
                    <tr>
                        <td></td>
                        <td>&lt;Meta&gt; + click on navigation tree label</td>
                    </tr>                    <tr>
                        <td>Isolate element</td>
                        <td>&lt;Shift&gt; + &lt;left mouse button&gt; double click</td>
                    </tr>
                    <tr>
                        <td></td>
                        <td>&lt;Shift&gt; + click on navigation tree label</td>
                    </tr>
                    <tr>
                        <td></td>
                        <td><b>CAD Object Tree</b></td>
                    </tr>
                    <tr>
                        <td>Collapse single leafs</td>
                        <td>Button '1' (all nodes with one leaf only)</td>
                    </tr>
                    <tr>
                        <td>Collapse all nodes</td>
                        <td>Button 'C'</td>
                    </tr>
                    <tr>
                        <td>Expand all nodes</td>
                        <td>Button 'E'</td>
                    </tr>
                </table>
            </div>
        </div>
    </div>
</div>
`;
  return html;
}

function px(val) {
  return `${val}px`;
}

const buttons = [
  "reset",
  "resize",
  "help",
  "iso",
  "front",
  "rear",
  "top",
  "bottom",
  "left",
  "right",
  "pin",
  "plane",
  "play",
  "pause",
  "stop",
];
class Slider {
  constructor(index, min, max, display) {
    this.index = index;
    this.display = display;

    this.slider = display.container.getElementsByClassName(
      `tcv_sld_value_plane${index}`,
    )[0];
    this.slider.min = min;
    this.slider.max = max;
    this.input = display.container.getElementsByClassName(
      `tcv_inp_value_plane${index}`,
    )[0];
    this.input.value = max;
    this.slider.oninput = this.sliderChange;
    this.input.addEventListener("change", this.inputChange);
  }

  _notify = (value, notify = true) => {
    const change = {};
    change[`clip_slider_${this.index - 1}`] = parseFloat(value);
    this.display.viewer.checkChanges(change, notify);
  };

  sliderChange = (e) => {
    const value = e.target.value;
    this.input.value = Math.round(1000 * value) / 1000;
    this.display.refreshPlane(this.index, this.input.value);
    this._notify(value);
  };

  inputChange = (e) => {
    const value = Math.max(
      Math.min(e.target.value, this.slider.max),
      this.slider.min,
    );
    // if (value != e.target.value) {
    //     this.input.value = Math.round(1000 * value) / 1000;
    // }
    this.slider.value = value;
    this.display.refreshPlane(this.index, this.input.value);
    this._notify(value);
  };

  setSlider(limit) {
    const exp = Math.abs(Math.round(Math.log10(2 * limit)));
    this.slider.min = -limit;
    this.slider.max = limit;
    this.slider.step = Math.pow(10, -(3 - exp));
    this.slider.value = limit;
    this.input.value = Math.round(1000 * this.slider.max) / 1000;
    this.display.refreshPlane(this.index, this.input.value);
  }

  getValue() {
    return parseFloat(this.input.value);
  }

  setValue(value, notify = true) {
    const trimmed_value = Math.max(
      Math.min(value, this.slider.max),
      this.slider.min,
    );
    this.input.value = trimmed_value;
    this.slider.value = value;
    this.display.refreshPlane(this.index, this.input.value);
    this._notify(value, notify);
  }
}

class Display {
  /**
   * Create Display
   * @param {DOMElement} container - the DOM element, e.g. div, that should contain the Display
   * @param {} options - display options
   */
  constructor(container, options) {
    this.container = container;

    this.container.innerHTML = TEMPLATE(this.container.id);
    const fullWidth = options.cadWidth + (options.glass ? 0 : options.treeWidth);
    this.handleMoreButton(fullWidth);
    this.cadBody = this._getElement("tcv_cad_body");
    this.cadTool = this._getElement("tcv_cad_toolbar");
    this.cadView = this._getElement("tcv_cad_view");
    this.cadTree = this._getElement("tcv_cad_tree_container");
    this.cadTreeToggles = this._getElement("tcv_cad_tree_toggles");
    this.cadClip = this._getElement("tcv_cad_clip_container");
    this.tabTree = this._getElement("tcv_tab_tree");
    this.tabClip = this._getElement("tcv_tab_clip");
    this.cadInfo = this._getElement("tcv_cad_info_container");
    this.cadAnim = this._getElement("tcv_cad_animation");

    this.cadHelp = this._getElement("tcv_cad_help");

    this.planeLabels = [];
    for (var i = 1; i < 4; i++) {
      this.planeLabels.push(this._getElement(`tcv_lbl_norm_plane${i}`));
    }

    this.viewer = null;
    this.glass = options.glass;
    this.tools = options.tools;
    this.cadWidth = options.cadWidth;
    this.height = options.height;
    this.treeWidth = options.treeWidth;

    this._events = [];

    this.setSizes(options);

    this.activeTab = "tree";
    this.cadTree.style.display = "block";
    this.cadClip.style.display = "none";
    this.clipSliders = null;

    this.lastPlaneState = false;

    var theme;
    if (
      options.theme === "dark" ||
      (options.theme == "browser" &&
        window.matchMedia("(prefers-color-scheme: dark)").matches)
    ) {
      document.documentElement.setAttribute("data-theme", "dark");
      theme = "dark";
    } else {
      document.documentElement.setAttribute("data-theme", "light");
      theme = "light";
    }

    for (var btn of buttons) {
      var elements = this.container.getElementsByClassName(`tcv_${btn}`);
      for (i = 0; i < elements.length; i++) {
        var el = elements[i];
        el.setAttribute(
          "style",
          `background-image: ${getIconBackground(theme, btn)}`,
        );
      }
    }

    this.showPinning(options.pinning);
  }

  _setupCheckEvent(name, fn, flag) {
    const el = this._getElement(name);
    el.addEventListener("change", fn);
    if (flag != undefined) {
      el.checked = flag;
    }
    this._events.push(["change", name, fn]);
  }

  // eslint-disable-next-line no-unused-vars
  _setupClickEvent(name, fn, flag) {
    const el = this._getElement(name);
    el.addEventListener("click", fn);
    this._events.push(["click", name, fn]);
  }

  _getElement(name) {
    return this.container.getElementsByClassName(name)[0];
  }

  dispose() {
    var type, el_name, fn;
    for (var ui_event of this._events) {
      [type, el_name, fn] = ui_event;
      const el = this._getElement(el_name);
      el.removeEventListener(type, fn);
    }
    // remove cadTree
    this.cadTree.innerHTML = "";
    // remove canvas
    this.cadView.removeChild(this.cadView.children[2]);
    // delete view
    this.container.innerHTML = "";
  }

  /**
   * Use More fropdown if overall width < 970px else just check boxes
   * @param {number} fullWidth - overall width of tree and cad view (taking glass mode into account)
   */
  handleMoreButton(fullWidth) {
    const moreButton = this._getElement("tcv_more-btn");
    const moreContent = this._getElement("tcv_more-wrapper");
    if (fullWidth  < 970) {
      moreButton.classList.remove("tcv_none");
      moreContent.classList.add("tcv_dropdown-content");
      moreContent.classList.add("tcv_more-content");  
    } else {
      moreButton.classList.add("tcv_none");
      moreContent.classList.remove("tcv_dropdown-content");
      moreContent.classList.remove("tcv_more-content");  
    }
  }

  /**
   * Set the width and height of the different UI elements (tree, canvas and info box)
   * @param {DisplayOptions} options
   */
  setSizes(options, ratio = 2 / 3) {
    if (options.cadWidth) {
      this.cadWidth = options.cadWidth;
      this.cadView.style.width = px(options.cadWidth);
    }
    if (options.height) {
      this.height = options.height;
      this.cadView.style.height = px(options.height);
    }
    if (options.treeWidth) {
      this.treeWidth = options.treeWidth;
      this.cadTree.parentElement.parentElement.style.width = px(
        options.treeWidth,
      );
      this.cadInfo.parentElement.parentElement.style.width = px(
        options.treeWidth,
      );
    }
    if (!options.glass) {
      const treeHeight = Math.round(options.height * ratio);
      this.cadTree.parentElement.parentElement.style.height = px(treeHeight);
      this.cadInfo.parentElement.parentElement.style.height = px(
        options.height - treeHeight - 4,
      );
    }

    if (options.tools && !options.glass) {
      this.cadTool.style.width = px(options.treeWidth + options.cadWidth + 4);
      this.cadBody.style.width = px(options.treeWidth + options.cadWidth + 4);
    } else {
      this.cadTool.style.width = px(options.cadWidth + 2);
      this.cadBody.style.width = px(options.cadWidth + 2);
    }

    this.cadBody.style.height = px(options.height + 4);
  }

  /**
   * Set up the UI
   * @param {Viewer} viewer - the viewer for this UI
   */
  setupUI(viewer) {
    this.viewer = viewer;

    this._setupCheckEvent("tcv_axes", this.setAxes, viewer.axes);
    this._setupCheckEvent("tcv_grid", this.setGrid, viewer.grid);
    this._setupCheckEvent("tcv_grid-xy", this.setGrid, viewer.grid);
    this._setupCheckEvent("tcv_grid-xz", this.setGrid, viewer.grid);
    this._setupCheckEvent("tcv_grid-yz", this.setGrid, viewer.grid);
    this._setupCheckEvent("tcv_axes0", this.setAxes0, viewer.axes0);
    this._setupCheckEvent("tcv_ortho", this.setOrtho, viewer.ortho);
    this._setupCheckEvent(
      "tcv_transparent",
      this.setTransparent,
      viewer.transparent,
    );
    this._setupCheckEvent(
      "tcv_black_edges",
      this.setBlackEdges,
      viewer.blackEdges,
    );

    this._setupCheckEvent("tcv_explode", this.setExplode);

    this._setupClickEvent("tcv_reset", this.reset);
    this._setupClickEvent("tcv_resize", this.resize);

    const buttons = [
      "tcv_front",
      "tcv_rear",
      "tcv_top",
      "tcv_bottom",
      "tcv_left",
      "tcv_right",
      "tcv_iso",
    ];
    buttons.forEach((name) => {
      this._setupClickEvent(name, this.setView);
    });

    this._setupClickEvent("tcv_collapse_singles", this.handleCollapseNodes);
    this._setupClickEvent("tcv_collapse_all", this.handleCollapseNodes);
    this._setupClickEvent("tcv_expand", this.handleCollapseNodes);

    this._setupClickEvent("tcv_toggle_info", this.toggleInfo);

    this._setupClickEvent("tcv_pin", this.pinAsPng);
    this._setupClickEvent("tcv_help", this.toggleHelp);
    this.help_shown = true;
    this.info_shown = !this.glass;

    const tabs = ["tcv_tab_tree", "tcv_tab_clip"];
    tabs.forEach((name) => {
      this._setupClickEvent(name, this.selectTab);
    });

    this.clipSliders = [];
    for (var i = 1; i < 4; i++) {
      this.clipSliders.push(new Slider(i, 0, 100, this));
    }

    this._setupCheckEvent(
      "tcv_clip_plane_helpers",
      this.setClipPlaneHelpers,
      false,
    );
    this._setupCheckEvent(
      "tcv_clip_intersection",
      this.setClipIntersection,
      false,
    );

    for (i = 1; i < 4; i++) {
      this._setupClickEvent(
        `tcv_btn_norm_plane${i}`,
        this.setClipNormalFromPosition,
        false,
      );
    }

    this._setupClickEvent("tcv_play", this.controlAnimation, false);
    this._setupClickEvent("tcv_pause", this.controlAnimation, false);
    this._setupClickEvent("tcv_stop", this.controlAnimation, false);
    this.animationSlider = this.container.getElementsByClassName(
      "tcv_animation_slider",
    )[0];
    this.animationSlider.value = 0;
    this.animationSlider.addEventListener("input", this.animationChange);
    this.showAnimationControl(false);

    this.showHelp(false);
  }

  /**
   * Check or uncheck a checkbox
   * @property {boolean} [axes = false] - show X-, Y-, Z-axes.
   * @property {boolean} [axes0 = false] - show axes at [0,0,0] ot at object center (target).
   * @property {boolean} [ortho = true] - use an orthographic (true) or perspective camera (false)
   * @property {boolean} [transparent = false] - show CAD object transparent.
   * @property {boolean} [blackEdges = false] - show edges in black and not in edgeColor.
   * @property {boolean} [tools = true] - show CAD tools.
   * @property {boolean} [glass = false] - use glass mode, i.e. CAD navigation as overlay.
   */
  updateUI(axes, axes0, ortho, transparent, blackEdges, tools, glass) {
    this.checkElement("tcv_axes", axes);
    this.checkElement("tcv_axes0", axes0);
    this.checkElement("tcv_ortho", ortho);
    this.checkElement("tcv_transparent", transparent);
    this.checkElement("tcv_black_edges", blackEdges);

    this.showTools(tools);
    this.glassMode(glass);
  }
  // setup functions

  /**
   * Check or uncheck a checkbox
   * @param {string} name - name of the check box, see getElement
   * @param {boolean} flag - whether to check or uncheck
   */
  checkElement(name, flag) {
    this._getElement(name).checked = flag;
  }

  /**
   * Add the Cad View (the canvas for threejs)
   * @param {DOMElement} cadView - the DOM element that contains the cadView
   */
  addCadView(cadView) {
    this.cadView.appendChild(cadView);
  }

  /**
   * Clear the Cad tree
   */
  clearCadTree() {
    this.cadTree.innerHTML = "";
  }

  /**
   * Add the Cad tree and other UI elements like Clipping
   * @param {DOMElement} cadTree - the DOM element that contains the cadTree
   */
  addCadTree(cadTree) {
    this.cadTree.appendChild(cadTree);
  }

  // handler (bound to Display instance)

  /**
   *
   * @function
   * @param {*} e
   */
  setAxes = (e) => {
    const flag = !!e.target.checked;
    this.viewer.setAxes(flag);
  };

  /**
   * Check/uncheck the axes checkbox
   * @function
   * @param {boolean} flag - whether to check or uncheck the axes checkbox
   */
  setAxesCheck = (flag) => {
    this.checkElement("tcv_axes", flag);
  };

  /**
   * Checkbox Handler for setting the grid parameter
   * @function
   * @param {Event} e - a DOM click event
   */
  setGrid = (e) => {
    const action = e.target.className.split(" ")[0].slice(4);
    this.viewer.setGrid(action);
  };

  /**
   * Check/uncheck the main grid UI element
   * @function
   * @param {boolean} flag - whether to check or uncheck the main grid checkbox
   */
  setGridCheck = (flag) => {
    this.checkElement("tcv_grid", flag);
  };

  /**
   * Checkbox Handler for setting the axes0 parameter
   * @function
   * @param {Event} e - a DOM click event
   */
  setAxes0 = (e) => {
    const flag = !!e.target.checked;
    this.viewer.setAxes0(flag);
  };

  /**
   * Check/uncheck the Axes0 checkbox
   * @function
   * @param {boolean} flag - whether to check or uncheck the Axes0 checkbox
   */
  setAxes0Check = (flag) => {
    this.checkElement("tcv_axes0", flag);
  };

  /**
   * Checkbox Handler for setting the ortho parameter
   * @function
   * @param {Event} e - a DOM click event
   */
  setOrtho = (e) => {
    const flag = !!e.target.checked;
    this.viewer.switchCamera(flag);
  };

  /**
   * Check or uncheck the Ortho checkbox
   * @function
   * @param {boolean} flag - whether to check or uncheck the ortho checkbox
   */
  setOrthoCheck = (flag) => {
    this.checkElement("tcv_ortho", flag);
  };

  /**
   * Checkbox Handler for setting the transparent parameter
   * @function
   * @param {Event} e - a DOM click event
   */
  setTransparent = (e) => {
    const flag = !!e.target.checked;
    this.viewer.setTransparent(flag);
  };

  /**
   * Check or uncheck the Transparent checkbox
   * @function
   * @param {boolean} flag - whether to check or uncheck the Transparent checkbox
   */
  setTransparentCheck = (flag) => {
    this.checkElement("tcv_transparent", flag);
  };

  /**
   * Checkbox Handler for setting the black edges parameter
   * @function
   * @param {Event} e - a DOM click event
   */
  setBlackEdges = (e) => {
    const flag = !!e.target.checked;
    this.viewer.setBlackEdges(flag);
  };

  /**
   * Check or uncheck the Black Edges checkbox
   * @function
   * @param {boolean} flag - whether to check or uncheck the Black Edges checkbox
   */
  setBlackEdgesCheck = (flag) => {
    this.checkElement("tcv_black_edges", flag);
  };

  /**
   * Checkbox Handler for setting the black edges parameter
   * @function
   * @param {Event} e - a DOM click event
   */
  setExplode = (e) => {
    const flag = !!e.target.checked;
    if (flag) {
      this.viewer.backupAnimation();
      this.viewer.explode();
    } else {
      this.controlAnimationByName("stop");
      this.viewer.clearAnimation();
      this.viewer.restoreAnimation();
    }
  };

  /**
   * Check or uncheck the Explode checkbox
   * @function
   * @param {boolean} flag - whether to check or uncheck the Black Edges checkbox
   */
  setExplodeCheck = (flag) => {
    this.checkElement("tcv_explode", flag);
  };

  /**
   * Show or hide the Explode checkbox
   * @function
   * @param {boolean} flag - whether to check or uncheck the Black Edges checkbox
   */
  showExplode = (flag) => {
    const el = this._getElement("tcv_explode_widget");
    el.style.display = flag ? "inline-block" : "none";
  };

  /**
   * Checkbox Handler for setting the clip planes parameter
   * @function
   * @param {Event} e - a DOM click event
   */
  setClipPlaneHelpers = (e) => {
    const flag = !!e.target.checked;
    this.setClipPlaneHelpersCheck(flag);
    this.viewer.setClipPlaneHelpers(flag);
  };

  /**
   * Check or uncheck the Plane Helpers checkbox
   * @function
   * @param {boolean} flag - whether to check or uncheck the Plane Helpers checkbox
   */
  setClipPlaneHelpersCheck = (flag) => {
    this.checkElement("tcv_clip_plane_helpers", flag);
    this.lastPlaneState = flag;
  };

  /**
   * Show or hide the CAD tools
   * @function
   * @param {boolean} flag - whether to show or hide the CAD tools
   */
  showTools = (flag) => {
    this.tools = flag;
    if (this.viewer) {
      // not available at first call
      this.viewer.tools = flag;
    }
    var tb = this._getElement("tcv_cad_toolbar");
    var cn = this._getElement("tcv_cad_navigation");
    for (var el of [cn, tb]) {
      if (flag) {
        el.style.height = "36px";
        el.style.display = "block";
      } else {
        el.style.height = "0px";
        el.style.display = "none";
      }
    }
  };

  /**
   * Checkbox Handler for setting the clip intersection parameter
   * @function
   * @param {*} e
   */
  setClipIntersection = (e) => {
    const flag = !!e.target.checked;
    this.viewer.setClipIntersection(flag);
  };

  /**
   * Check or uncheck the Intersection checkbox
   * @function
   * @param {boolean} flag - whether to check or uncheck the Intersection checkbox
   */
  setClipIntersectionCheck = (flag) => {
    const el = this._getElement("tcv_clip_intersection");
    el.checked = flag;
  };

  /**
   * Handler to reset position, zoom and up of the camera
   * @function
   */
  reset = () => {
    this.viewer.reset();
    this.clearHighlights();
  };

  /**
   * Handler to reset zoom of the camera
   * @function
   */
  resize = () => {
    this.viewer.resize();
  };

  /**
   * Clear all highlights of navigation tree entries
   */
   clearHighlights() {
    const buttons = [
      "tcv_front",
      "tcv_rear",
      "tcv_top",
      "tcv_bottom",
      "tcv_left",
      "tcv_right",
      "tcv_iso",
    ];
    buttons.forEach((btn) => {
      var el = this._getElement(btn);
      el.classList.remove("tcv_btn_highlight");
    });
  }

  /**
   * Highlight the selected navigation tree entry
   * @param {string} name - A CAD object id (path)
   */
  highlightButton(name) {
    this.clearHighlights();
    var el = this._getElement(`tcv_${name}`);
    el.classList.add("tcv_btn_highlight");
    this.viewer.keepHighlight = true;
  }

  /**
   * Handler to set camera to a predefined position
   * @function
   * @param {Event} e - a DOM click event
   */
  setView = (e) => {
    const btn = e.target.className.split(" ")[0].slice(4);
    this.viewer.presetCamera(btn);
    this.highlightButton(btn);
  };

  /**
   * Show/hide pinning button
   * @function
   * @param {boolean} flag - Whether to show/hide the pinning button
   */
  showPinning(flag) {
    const el = this._getElement("tcv_pin");
    el.style.display = flag ? "inline-block" : "none";
  }

  /**
   * Pin screenshot of canvas as PNG
   * @function
   * @param {Event} e - a DOM click event
   */
  // eslint-disable-next-line no-unused-vars
  pinAsPng = (e) => {
    this.viewer.pinAsPng();
  };

  /**
   * Handler to set the label of a clipping normal widget
   * @function
   * @param {number} index - index of the normal widget
   * @param {Vector3} normal - the normal
   */
  setNormalLabel = (index, normal) => {
    this.planeLabels[index].innerHTML = `N=(${normal[0].toFixed(
      2,
    )}, ${normal[1].toFixed(2)}, ${normal[2].toFixed(2)})`;
  };

  /**
   * Set the normal at index to the current viewing direction
   * @function
   * @param {Event} e - a DOM click event
   */
  setClipNormalFromPosition = (e) => {
    const index = parseInt(e.target.classList[0].slice(-1));
    this.viewer.setClipNormalFromPosition(index - 1);
  };

  /**
   * Handler to activate a UI tab (tree / clipping)
   * @function
   * @param {Event} e - a DOM click event
   */
  selectTab = (e) => {
    const tab = e.target.className.split(" ")[0];
    this.selectTabByName(tab.slice(8));
  };

  /**
   * Activate the UI tab given the name of the tab
   * @param {string} tab - name of the tab "tree" or "clip"
   */
  selectTabByName(tab) {
    if (!["clip", "tree"].includes(tab)) {
      return;
    }

    if (tab === "tree" && this.activeTab !== "tree") {
      this.cadTree.style.display = "block";
      this.cadTreeToggles.style.display = "block";
      this.cadClip.style.display = "none";
      this.viewer.nestedGroup.setBackVisible(false);
      this.viewer.setLocalClipping(false);
      // copy state since setClipHelpers(false) will set to false
      var lastPlaneState = this.viewer.getClipPlaneHelpers();
      this.viewer.setClipPlaneHelpers(false);
      this.lastPlaneState = lastPlaneState;
    } else if (tab === "clip" && this.activeTab !== "clip") {
      this.cadTree.style.display = "none";
      this.cadTreeToggles.style.display = "none";
      this.cadClip.style.display = "block";
      this.viewer.nestedGroup.setBackVisible(true);
      this.viewer.setLocalClipping(true);
      this.viewer.setClipPlaneHelpers(this.lastPlaneState);
    }
    this.activeTab = tab;
    this.viewer.checkChanges({ tab: tab });
    if (tab == "tree") {
      this.tabTree.classList.add("tcv_tab-selected");
      this.tabTree.classList.remove("tcv_tab-unselected");
      this.tabClip.classList.remove("tcv_tab-selected");
      this.tabClip.classList.add("tcv_tab-unselected");
    } else {
      this.tabTree.classList.remove("tcv_tab-selected");
      this.tabTree.classList.add("tcv_tab-unselected");
      this.tabClip.classList.add("tcv_tab-selected");
      this.tabClip.classList.remove("tcv_tab-unselected");
    }
  }

  /**
   * Collapse nodes handler
   * @function
   * @param {Event} e - a DOM click event
   */
  handleCollapseNodes = (e) => {
    this.collapseNodes(e.target.value);
  };

  /**
   * Collapse nodes handler
   * @param {string} value - 1: collapse all leaf nodes, 2: collapse all nodes, "E": expand all nodes
   */
  collapseNodes(value) {
    if (value === "1") {
      this.viewer.treeview.expandNodes();
      this.viewer.treeview.collapseNodes(1);
    } else if (value === "C") {
      this.viewer.treeview.collapseNodes(2);
    } else if (value === "E") {
      this.viewer.treeview.expandNodes();
    }
  }

  /**
   * Set minimum and maximum of the sliders
   * @param {number} index - index of the plane: 0,1,2
   * @param {number} limit - the value for both minimum and maximum value of the slider
   */
  setSliderLimits(limit) {
    for (var i = 0; i < 3; i++) {
      this.clipSliders[i].setSlider(limit);
    }
  }

  /**
   * Refresh clipping plane
   * @function
   * @param {number} index - index of the plane: 0,1,2
   * @param {number} value - distance on the clipping normal from the center
   */
  refreshPlane(index, value) {
    this.viewer.refreshPlane(index - 1, parseFloat(value));
  }

  /**
   * Show or hide the Animation control widget
   * @function
   * @param {boolean} flag - whether to show or hide the Animation control widget
   */
  showAnimationControl = (flag) => {
    this.cadAnim.style.display = flag ? "block" : "none";
  };

  /**
   * Handle animation control
   * @function
   * @param {string} btn - animation control button name
   */
  controlAnimationByName(btn) {
    this.viewer.controlAnimation(btn);

    var currentTime = this.viewer.animation.getRelativeTime();
    this.animationSlider.value = 1000 * currentTime;
    if (btn == "play") {
      this.viewer.bboxNeedsUpdate = true;
    } else if (btn == "stop") {
      this.viewer.bboxNeedsUpdate = false;
      if(this.viewer.lastBbox != null){
        this.viewer.lastBbox.needsUpdate = true;
      }
    } else {
      this.viewer.bboxNeedsUpdate = !this.viewer.bboxNeedsUpdate;
    }
  }

  /**
   * Handler for the animation control
   * @function
   * @param {Event} e - a DOM click event
   */
  controlAnimation = (e) => {
    const btn = e.target.className.split(" ")[0].slice(4);
    this.controlAnimationByName(btn);
  };

  /**
   * Handler for the animation slider
   * @function
   * @param {Event} e - a DOM click event
   */
  animationChange = (e) => {
    this.viewer.animation.setRelativeTime(e.target.valueAsNumber / 1000);
    if(this.viewer.lastBbox != null){
      this.viewer.lastBbox.needsUpdate = true;
    }
  };

  /**
   * Set label text of animation control
   * @param {string} label - "A" for animation and "E" for Explode control
   */
  setAnimationLabel(label) {
    var el = this._getElement("tcv_animation_label");
    el.innerHTML = label;
  }

  /**
   * Reset animation slider to 0
   */
  resetAnimationSlider() {
    this.animationSlider.value = 0;
  }

  /**
   * Show or hide help dialog
   * @function
   * @param {boolean} flag - whether to show or hide help dialog
   */
  showHelp = (flag) => {
    this.cadHelp.style.display = flag ? "block" : "none";
    this.help_shown = flag;
  };

  /**
   * Show help dialog
   * @function
   */
  toggleHelp = () => {
    this.showHelp(!this.help_shown);
  };

  /**
   * Show or hide info dialog
   * @function
   * @param {boolean} flag - whether to show or hide info dialog
   */
  showInfo = (flag) => {
    this.cadInfo.parentNode.parentNode.style.display = flag ? "block" : "none";
    this._getElement("tcv_toggle_info").value = flag ? "\u25B2 i" : "\u25BC i";
    this.info_shown = flag;
  };

  /**
   * Show info dialog
   * @function
   */
  toggleInfo = () => {
    this.showInfo(!this.info_shown);
  };

  /**
   * Auto collapse tree nodes, when cad width < 600
   * @function
   * @param {boolean} flag - whether to enable/disable glass mode
   */
  autoCollapse() {
    if (this.cadWidth < 600 && this.glass) {
      console.info("Small view, collapsing tree");
      this.collapseNodes("C");
    }
  }

  /**
   * Enable/disable glass mode
   * @function
   * @param {boolean} flag - whether to enable/disable glass mode
   */
  glassMode(flag) {
    if (flag) {
      this._getElement("tcv_cad_tree").classList.add("tcv_cad_tree_glass");
      this._getElement("tcv_cad_tree").style["height"] = null;
      this._getElement("tcv_cad_tree").style["max-height"] = px(
        Math.round((this.height * 2) / 3) - 18,
      );

      this._getElement("tcv_cad_info").classList.add("tcv_cad_info_glass");
      this._getElement("tcv_cad_view").classList.add("tcv_cad_view_glass");

      this._getElement("tcv_toggle_info_wrapper").style.display = "block";

      this.showInfo(false);
      this.glass = true;
      this.autoCollapse();
    } else {
      this._getElement("tcv_cad_tree").classList.remove("tcv_cad_tree_glass");
      this._getElement("tcv_cad_tree").style["max-height"] = null;
      this._getElement("tcv_cad_tree").style.height = px(
        Math.round((this.height * 2) / 3),
      );
      this._getElement("tcv_cad_info").classList.remove("tcv_cad_info_glass");
      this._getElement("tcv_cad_view").classList.remove("tcv_cad_view_glass");

      this._getElement("tcv_toggle_info_wrapper").style.display = "none";

      this.showInfo(true);
      this.glass = false;
    }
    if (this.viewer) {
      // not available at first call
      this.viewer.glass = false;
    }
    const options = {
      cadWidth: this.cadWidth,
      glass: this.glass,
      height: this.height,
      tools: this.tools,
      treeWidth: flag ? 0 : this.treeWidth,
    };
    this.setSizes(options);
    
    const fullWidth = this.cadWidth + (this.glass ? 0 : this.treeWidth);
    this.handleMoreButton(fullWidth);
  }
}

export { Display };
