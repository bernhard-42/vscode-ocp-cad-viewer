import light_bottom from "../icons/light/bottom.svg";
import light_front from "../icons/light/front.svg";
import light_help from "../icons/light/help.svg";
import light_iso from "../icons/light/iso.svg";
import light_left from "../icons/light/left.svg";
import light_mesh from "../icons/light/mesh.svg";
import light_mesh_empty from "../icons/light/mesh_empty.svg";
import light_mesh_mix from "../icons/light/mesh_mix.svg";
import light_mesh_no from "../icons/light/mesh_no.svg";
import light_pause from "../icons/light/pause.svg";
import light_pin from "../icons/light/pin.svg";
import light_plane from "../icons/light/plane.svg";
import light_play from "../icons/light/play.svg";
import light_rear from "../icons/light/rear.svg";
import light_reset from "../icons/light/reset.svg";
import light_resize from "../icons/light/resize.svg";
import light_right from "../icons/light/right.svg";
import light_shape from "../icons/light/shape.svg";
import light_shape_empty from "../icons/light/shape_empty.svg";
import light_shape_mix from "../icons/light/shape_mix.svg";
import light_shape_no from "../icons/light/shape_no.svg";
import light_stop from "../icons/light/stop.svg";
import light_top from "../icons/light/top.svg";
import dark_bottom from "../icons/dark/bottom.svg";
import dark_front from "../icons/dark/front.svg";
import dark_help from "../icons/dark/help.svg";
import dark_iso from "../icons/dark/iso.svg";
import dark_left from "../icons/dark/left.svg";
import dark_mesh from "../icons/dark/mesh.svg";
import dark_mesh_empty from "../icons/dark/mesh_empty.svg";
import dark_mesh_mix from "../icons/dark/mesh_mix.svg";
import dark_mesh_no from "../icons/dark/mesh_no.svg";
import dark_pause from "../icons/dark/pause.svg";
import dark_pin from "../icons/dark/pin.svg";
import dark_plane from "../icons/dark/plane.svg";
import dark_play from "../icons/dark/play.svg";
import dark_rear from "../icons/dark/rear.svg";
import dark_reset from "../icons/dark/reset.svg";
import dark_resize from "../icons/dark/resize.svg";
import dark_right from "../icons/dark/right.svg";
import dark_shape from "../icons/dark/shape.svg";
import dark_shape_empty from "../icons/dark/shape_empty.svg";
import dark_shape_mix from "../icons/dark/shape_mix.svg";
import dark_shape_no from "../icons/dark/shape_no.svg";
import dark_stop from "../icons/dark/stop.svg";
import dark_top from "../icons/dark/top.svg";

const icons = {
  bottom: { light: light_bottom, dark: dark_bottom },
  front: { light: light_front, dark: dark_front },
  help: { light: light_help, dark: dark_help },
  iso: { light: light_iso, dark: dark_iso },
  left: { light: light_left, dark: dark_left },
  mesh: { light: light_mesh, dark: dark_mesh },
  mesh_empty: { light: light_mesh_empty, dark: dark_mesh_empty },
  mesh_mix: { light: light_mesh_mix, dark: dark_mesh_mix },
  mesh_no: { light: light_mesh_no, dark: dark_mesh_no },
  pause: { light: light_pause, dark: dark_pause },
  pin: { light: light_pin, dark: dark_pin },
  plane: { light: light_plane, dark: dark_plane },
  play: { light: light_play, dark: dark_play },
  rear: { light: light_rear, dark: dark_rear },
  reset: { light: light_reset, dark: dark_reset },
  resize: { light: light_resize, dark: dark_resize },
  right: { light: light_right, dark: dark_right },
  shape: { light: light_shape, dark: dark_shape },
  shape_empty: { light: light_shape_empty, dark: dark_shape_empty },
  shape_mix: { light: light_shape_mix, dark: dark_shape_mix },
  shape_no: { light: light_shape_no, dark: dark_shape_no },
  stop: { light: light_stop, dark: dark_stop },
  top: { light: light_top, dark: dark_top },
};

function getIconBackground(theme, name) {
  return `url(data:image/svg+xml;utf8,${escape(icons[name][theme])});`;
}

export { getIconBackground };
