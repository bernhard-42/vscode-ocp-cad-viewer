function clone(obj) {
  if (Array.isArray(obj)) {
    return obj.map((el) => clone(el));
  } else if (typeof obj === "object") {
    var result = {};
    for (var [k, v] of Object.entries(obj)) {
      result[k] = clone(v);
    }
    return result;
  } else {
    return obj;
  }
}

function isEqual(obj1, obj2, tol = 1e-9) {
  if (Array.isArray(obj1) && Array.isArray(obj2)) {
    return (
      obj1.length === obj2.length && obj1.every((v, i) => isEqual(v, obj2[i]))
    );
  } else if (typeof obj1 === "object" && typeof obj2 === "object") {
    var keys1 = Object.keys(obj1);
    var keys2 = Object.keys(obj2);

    if (
      keys1.length == keys2.length &&
      keys1.every((key) => Object.prototype.hasOwnProperty.call(obj2, key))
    ) {
      return keys1.every((key) => isEqual(obj1[key], obj2[key]));
    } else {
      return false;
    }
  } else {
    if (Number(obj1) === obj1 && Number(obj2) === obj2) {
      return Math.abs(obj1 - obj2) < tol;
    }
    return obj1 === obj2;
  }
}

function sceneTraverse(obj, fn) {
  if (!obj) return;

  fn(obj);

  if (obj.children && obj.children.length > 0) {
    obj.children.forEach((o) => {
      sceneTraverse(o, fn);
    });
  }
}

function format(v, b = 2, a = 2) {
  const s = Math.abs(v).toFixed(a);
  var padding = "";
  var int = s.split(".")[0];
  for (var i = int.length; i < b; i++) padding += " ";
  padding += v < 0 ? "-" : " ";
  return padding + s;
}

function prettyPrintVector(v, a, b) {
  return `${format(v[0], a, b)}, ${format(v[2], a, b)}, ${format(v[2], a, b)}`;
}

export { clone, isEqual, sceneTraverse, prettyPrintVector };
