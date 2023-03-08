import { getIconBackground } from "./icons.js";

// Some helpers

function tag(name, classList, options) {
  var el = document.createElement(name);
  if (typeof classList != "undefined") {
    for (var i in classList) {
      el.classList.add(classList[i]);
    }
  }
  if (typeof options != "undefined") {
    for (var t in options) {
      el[t] = options[t];
    }
  }
  return el;
}

const States = {
  unselected: 0,
  selected: 1,
  mixed: 2,
  empty: 3,
};

class TreeView {
  constructor(states, tree, objectHandler, pickHandler, theme) {
    this.states = states;
    this.tree = tree;
    this.objectHandler = objectHandler;
    this.pickHandler = pickHandler;
    this.theme = theme;
    this.lastSelection = null;

    this.setupIcons(theme);
    this.treeModel = this.toModel(tree);
  }

  setupIcons(theme) {
    var shapes = {};
    shapes[States.unselected] = getIconBackground(theme, "shape_no");
    shapes[States.selected] = getIconBackground(theme, "shape");
    shapes[States.mixed] = getIconBackground(theme, "shape_mix");
    shapes[States.empty] = getIconBackground(theme, "shape_empty");

    var meshes = {};
    meshes[States.unselected] = getIconBackground(theme, "mesh_no");
    meshes[States.selected] = getIconBackground(theme, "mesh");
    meshes[States.mixed] = getIconBackground(theme, "mesh_mix");
    meshes[States.empty] = getIconBackground(theme, "mesh_empty");

    this.icons = [shapes, meshes];
  }

  toModel(tree) {
    var model = {
      id: tree.id,
      type: tree.type,
      name: tree.name,
      color: tree.color,
      imgs: [],
      states: [],
    };
    var i = 0;

    if (tree.type === "node") {
      for (i in this.icons) {
        model.states.push(States.selected);
      }
      model.children = [];
      for (i in tree.children) {
        model.children.push(this.toModel(tree.children[i]));
      }
    } else if (tree.type === "leaf") {
      var state = this.states[tree.id];
      for (i in this.icons) {
        model.states.push(state[i]);
      }
    } else {
      console.error(`Error, unknown type '${tree.type}'`);
    }
    return model;
  }

  toHtml(model) {
    var icon_id = 0;
    var img_button;

    var li = tag("li", [`node${model.id.replaceAll(" ", "_")}`]);
    var lbl = tag("span", ["tcv_tree_label"]);
    lbl.innerHTML = model.name;
    lbl.id = model.id;
    
    lbl.addEventListener("mousedown", (e) => {
      e.preventDefault();
      e.stopPropagation();
      const id = e.target.id;
      const parts = id.split("/");
      const path = parts.slice(0, -1).join("/");
      const name = parts[parts.length - 1];

      this.pickHandler(path, name, e.metaKey, e.shiftKey, model.type, true);
    }, false);

    var entry = tag("span", ["tcv_node_entry"], { id: model.id });
    if (model.type === "node") {
      var span = tag("span", ["tcv_node_entry_wrap"]);
      span.appendChild(tag("span", ["tcv_t-caret", "tcv_t-caret-down"]));
      for (icon_id in this.icons) {
        img_button = tag("input", ["tcv_icon"], {
          type: "button",
          style: `background-image: ${this.getIcon(icon_id, 1)}`,
        });
        img_button.setAttribute("icon_id", icon_id);
        img_button.addEventListener("click", (e) => {
          // jshint ignore:line
          this.handleClick(
            model.type,
            model.id,
            e.srcElement.getAttribute("icon_id"),
          );
        });
        entry.appendChild(img_button);
        model.imgs.push(img_button);
      }
      entry.appendChild(lbl);
      span.appendChild(entry);
      li.append(span);
      var lu = tag("ul", ["tcv_nested", "tcv_active"]);
      for (var i in model.children) {
        lu.appendChild(this.toHtml(model.children[i]));
      }
      li.appendChild(lu);
    } else {
      for (icon_id in this.icons) {
        img_button = tag("input", ["tcv_icon"], {
          type: "button",
          style: `background-image: ${this.getIcon(
            icon_id,
            model.states[icon_id],
          )}`,
        });
        img_button.setAttribute("icon_id", icon_id);
        if (icon_id == 0) {
          img_button.classList.add("tcv_indent");
        }
        if (model.states[icon_id] != States.empty) {
          // no events on empty icon
          img_button.addEventListener("click", (e) => {
            // jshint ignore:line
            this.handleClick(
              model.type,
              model.id,
              e.srcElement.getAttribute("icon_id"),
            );
          });
        }
        entry.appendChild(img_button);
        model.imgs.push(img_button);
      }
      entry.appendChild(lbl);
      li.appendChild(entry);
    }
    return li;
  }

  _labelVisible(label) {
    const scrollContainer = this.container.parentElement.parentElement;
    const height = scrollContainer.getBoundingClientRect().height;
    const scrollTop = scrollContainer.scrollTop;
    const offsetTop = label.offsetTop - 134;
    return offsetTop - scrollTop < height - 12 && offsetTop > scrollTop;
  }

  _openToTop(label) {
    var li = label.parentElement.parentElement.parentElement.parentElement;
    while (li.tagName == "LI") {
      this.toggleTreeNode(li, false);
      li = li.parentElement.parentElement;
    }
  }

  removeLabelHighlight() {
    this.lastSelection?.classList.remove("tcv_node_selected");
    this.lastSelection = null;
  }

  highlightLabel(label) {
    const change = label != this.lastSelection;
    this.removeLabelHighlight();
    if (change) {
      // open collapsed entries
      if (label.offsetTop == 0) {
        this._openToTop(label);
      }

      label.classList.add("tcv_node_selected");
      this.lastSelection = label;

      if (!this._labelVisible(label)) {
        if (label.scrollIntoViewIfNeeded == null) {
          label.scrollIntoView({ block: "nearest" });
        } else {
          label.scrollIntoViewIfNeeded();
        }
      }
    }
  }

  selectNode(id) {
    const el = this.container.getElementsByClassName(
      `node${id.replaceAll(" ", "_")}`,
    )[0];
    if (el != null) {
      const label = el.getElementsByClassName("tcv_tree_label")[0];
      this.highlightLabel(label);
    }
  }

  toggleTreeNode(el, collapse) {
    if (collapse == null) {
      el.querySelector(".tcv_nested").classList.toggle("tcv_active");
      el.getElementsByClassName("tcv_t-caret")[0].classList.toggle(
        "tcv_t-caret-down",
      );
    } else if (collapse) {
      el.querySelector(".tcv_nested").classList.remove("tcv_active");
      el.getElementsByClassName("tcv_t-caret")[0].classList.remove(
        "tcv_t-caret-down",
      );
    } else {
      el.querySelector(".tcv_nested").classList.add("tcv_active");
      el.getElementsByClassName("tcv_t-caret")[0].classList.add(
        "tcv_t-caret-down",
      );
    }
  }

  render(collapse) {
    // before the nodes can be collapsed, the DOM element needs to be rendered and added to the container
    this.container = tag("ul", ["tcv_toplevel"]);

    // eslint-disable-next-line no-unused-vars
    var observer = new MutationObserver((_mutuations) => {
      if (this.container.contains(tree)) {
        if (collapse > 0 && collapse < 3) {
          this.collapseNodes(collapse);
        }
        observer.disconnect();
      }
    });

    observer.observe(this.container, {
      attributes: false,
      childList: true,
      characterData: false,
      subtree: false,
    });

    const tree = this.toHtml(this.treeModel);
    this.container.appendChild(tree);

    for (var icon_id in this.icons) {
      this.updateNodes(this.treeModel, icon_id);
    }

    var toggler = this.container.getElementsByClassName("tcv_t-caret");
    for (var i = 0; i < toggler.length; i++) {
      toggler[i].addEventListener("click", (e) => {
        this.toggleTreeNode(e.target.parentElement.parentElement, null);
      });
    }

    return this.container;
  }

  getNode(node, id) {
    if (node.id == id) return node;
    for (var i in node.children) {
      var result = this.getNode(node.children[i], id);
      if (result != null) return result;
    }
    return null;
  }

  updateState(node, icon_id, state) {
    if (node.states[icon_id] != States.empty) {
      // ignore empty
      this.states[node.id][icon_id] = state;
      node.states[icon_id] = state;
      this.setIcon(node.imgs[icon_id], icon_id, state);
    }
  }

  propagateChange(node, icon_id, state) {
    for (var i in node.children) {
      var subNode = node.children[i];
      if (subNode.type == "leaf") {
        this.updateState(subNode, icon_id, state);
      } else {
        this.propagateChange(subNode, icon_id, state);
      }
    }
  }

  updateNodes(model, icon_id) {
    var state = 0;
    if (model.type === "node") {
      var states = [];
      for (var i in model.children) {
        states.push(this.updateNodes(model.children[i], icon_id));
      }
      var filtered_states = states.filter((e) => e != 3);
      if (filtered_states.length == 0) {
        state = 3;
      } else {
        state = filtered_states.reduce(
          (s1, s2) => (s1 == s2 ? s1 : States.mixed),
          filtered_states[0],
        );
      }
      model.states[icon_id] = state;
      this.setIcon(model.imgs[icon_id], icon_id, state);
    } else {
      state = model.states[icon_id];
    }
    return state;
  }

  _toggleNodes(mode, collapse) {
    var walk = (obj) => {
      if (obj.type == "node") {
        if (
          (mode == 1 &&
            obj.children.length === 1 &&
            obj.children[0].type === "leaf") ||
          mode == 2
        ) {
          var el = this.container.getElementsByClassName(
            `node${obj.id.replaceAll(" ", "_")}`,
          )[0];
          if (el != null) {
            this.toggleTreeNode(el, collapse);
          }
        }
        for (var o of obj.children) {
          walk(o);
        }
      }
    };
    walk(this.tree);
  }

  collapseNodes(mode) {
    this._toggleNodes(mode, true);
  }

  expandNodes() {
    this._toggleNodes(2, false);
  }

  getIcon(icon_id, state) {
    return this.icons[icon_id][state];
  }

  setIcon(img, icon_id, state) {
    img.setAttribute(
      "style",
      `background-image: ${this.getIcon(icon_id, state)}`,
    );
  }

  hideAll() {
    [0, 1].forEach((i) => this.setState("node", this.treeModel.id, i, 0));
  }

  showAll() {
    [0, 1].forEach((i) => this.setState("node", this.treeModel.id, i, 1));
  }

  setState(type, id, icon_id, state) {
    this.handleStateChange(type, id, icon_id, state);
  }

  handleClick(type, id, icon_id) {
    this.handleStateChange(type, id, icon_id, null);
  }

  handleStateChange(type, id, icon_id, state) {
    var node = this.getNode(this.treeModel, id);
    var newState;
    if (state == null) {
      newState =
        node.states[icon_id] == States.selected
          ? States.unselected
          : States.selected;
    } else {
      newState = state ? States.selected : States.unselected;
    }
    if (type == "leaf") {
      this.updateState(node, icon_id, newState);
      this.updateNodes(this.treeModel, icon_id);
      this.objectHandler(this.states);
    } else if (type == "node") {
      this.propagateChange(node, icon_id, newState);
      this.updateNodes(this.treeModel, icon_id);
      this.objectHandler(this.states);
    } else {
      console.error(`Error, unknown type '${type}'`);
    }
  }
}

export { TreeView };
