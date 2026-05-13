"""Tests for the standalone CLI — verify that command-line flags propagate
into the running viewer's workspace config.

Each test spawns its own `python -m ocp_vscode` subprocess on a non-default
port, queries it via `workspace_config()`, asserts the expected keys, then
terminates the subprocess.
"""

import os
import subprocess
import sys
import time

import pytest

from ocp_vscode import set_port, workspace_config
from ocp_vscode.comms import port_check
from ocp_vscode.state import del_port


# Use a port that is unlikely to clash with a running dev viewer.
STANDALONE_PORT = 39777
STARTUP_TIMEOUT = 20.0  # seconds


@pytest.fixture(autouse=True)
def disable_pytest_stub():
    """`OCP_VSCODE_PYTEST=1` short-circuits `workspace_config`; turn it off."""
    old = os.environ.pop("OCP_VSCODE_PYTEST", None)
    yield
    if old is not None:
        os.environ["OCP_VSCODE_PYTEST"] = old


@pytest.fixture(autouse=True)
def isolate_comms_port_state():
    """`set_port()` mutates module-level globals in `ocp_vscode.comms`
    (`CMD_PORT`, `CMD_URL`, `INIT_DONE`). Save and restore them around each
    test so our standalone port (39777) doesn't leak into sibling test
    modules — e.g. `tests/test_viewer_config.py` expects `OCP_PORT=3939`
    discovery, which only fires when `INIT_DONE` is False."""
    import ocp_vscode.comms as comms

    saved = (comms.INIT_DONE, comms.CMD_PORT, comms.CMD_URL)
    yield
    comms.INIT_DONE, comms.CMD_PORT, comms.CMD_URL = saved


def _wait_for_config(port, proc, timeout=STARTUP_TIMEOUT):
    """Poll `workspace_config` until it returns (handles WS-startup race).

    If the subprocess exits early or the timeout fires, surface its captured
    stdout/stderr in the assertion message — otherwise CLI errors are silent.
    """
    deadline = time.time() + timeout
    last_err = None
    while time.time() < deadline:
        if proc.poll() is not None:
            out = proc.stdout.read() if proc.stdout else ""
            raise AssertionError(
                f"standalone on port {port} exited with code {proc.returncode} "
                f"before answering; output:\n{out}"
            )
        if port_check(port):
            try:
                return workspace_config(port=port)
            except Exception as ex:  # pylint: disable=broad-except
                last_err = ex
        time.sleep(0.2)
    raise AssertionError(
        f"standalone on port {port} did not answer workspace_config in "
        f"{timeout}s (last error: {last_err!r})"
    )


@pytest.fixture
def standalone():
    """Spawn `python -m ocp_vscode` with caller-supplied CLI args.

    Yield function `start(*cli_args)` → port (after the WS is ready).
    """
    procs = []

    def start(*cli_args):
        cmd = [
            sys.executable, "-m", "ocp_vscode",
            "--port", str(STANDALONE_PORT),
            *cli_args,
        ]
        env = dict(os.environ)
        env.pop("OCP_PORT", None)
        p = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        procs.append(p)
        set_port(STANDALONE_PORT)
        return p

    yield start

    for p in procs:
        p.terminate()
        try:
            p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            p.kill()
        del_port(STANDALONE_PORT)


def test_passthrough_flags(standalone):
    """Plain-value flags should land in workspace_config 1:1."""
    proc = standalone(
        "--axes",
        "--axes0",
        "--grid_xy",
        "--theme", "dark",
        "--tree_width", "300",
        "--ticks", "12",
        "--rotate_speed", "2.0",
        "--zoom_speed", "0.25",
        "--pan_speed", "0.75",
        "--up", "Y",
    )
    cfg = _wait_for_config(STANDALONE_PORT, proc)

    assert cfg["axes"] is True
    assert cfg["axes0"] is True
    assert cfg["grid"] == [True, False, False]  # XY only
    assert cfg["theme"] == "dark"
    assert cfg["tree_width"] == 300
    assert cfg["ticks"] == 12
    assert cfg["rotate_speed"] == 2.0
    assert cfg["zoom_speed"] == 0.25
    assert cfg["pan_speed"] == 0.75
    assert cfg["up"] == "Y"


def test_zoom_speed_value_matching_old_default(standalone):
    """`--zoom_speed 1.0` (previously the Click default) must still take effect.

    Regression: with the old `default=1` on the Click option, `track_param`
    silently dropped the user value because it matched the Click default,
    and the in-process default of 0.5 in standalone.DEFAULTS won instead.
    """
    proc = standalone("--zoom_speed", "1.0")
    cfg = _wait_for_config(STANDALONE_PORT, proc)
    assert cfg["zoom_speed"] == 1.0


def test_inverted_flags(standalone):
    """`--no_glass`, `--no_tools`, `--perspective` flip internal booleans."""
    proc = standalone("--no_glass", "--no_tools", "--perspective")
    cfg = _wait_for_config(STANDALONE_PORT, proc)

    assert cfg["glass"] is False    # --no_glass
    assert cfg["tools"] is False    # --no_tools
    assert cfg["ortho"] is False    # --perspective


def test_defaults_when_no_flags(standalone):
    """Spawn with no flags; key defaults should match the built-in values."""
    proc = standalone()
    cfg = _wait_for_config(STANDALONE_PORT, proc)

    assert cfg["axes"] is False
    assert cfg["theme"] == "browser"
    assert cfg["tree_width"] == 240
    assert cfg["glass"] is True
    assert cfg["tools"] is True
    assert cfg["ortho"] is True
    assert cfg["grid"] == [False, False, False]


def test_three_grid_planes(standalone):
    """All three grid flags compose into `grid=[xy, xz, yz]`."""
    proc = standalone("--grid_xy", "--grid_xz", "--grid_yz")
    cfg = _wait_for_config(STANDALONE_PORT, proc)
    assert cfg["grid"] == [True, True, True]


# ---------------------------------------------------------------------------
# Regression tests for the audit fixes
# ---------------------------------------------------------------------------


def test_reset_camera_string_value_propagates(standalone):
    """`--reset_camera reset` was silently dropped before the audit fix
    because it matched the (broken) Click default of "reset" while
    standalone.DEFAULTS used "KEEP"."""
    from ocp_vscode import Camera

    proc = standalone("--reset_camera", "reset")
    cfg = _wait_for_config(STANDALONE_PORT, proc)
    assert cfg["reset_camera"] == Camera.RESET


def test_ambient_intensity_accepts_fractional(standalone):
    """`--ambient_intensity 0.7` was rejected before the fix because Click
    inferred type=INTEGER from default=1."""
    proc = standalone("--ambient_intensity", "0.7")
    cfg = _wait_for_config(STANDALONE_PORT, proc)
    assert cfg["ambient_intensity"] == 0.7


def test_collapse_accepts_string_value(standalone):
    """`--collapse leaves` was rejected before the fix because Click
    inferred type=INTEGER from default=1, even though the help text
    described string modes ('leaves', 'all', 'none', 'root')."""
    from ocp_vscode import Collapse

    proc = standalone("--collapse", "leaves")
    cfg = _wait_for_config(STANDALONE_PORT, proc)
    assert cfg["collapse"] == Collapse.LEAVES


def test_default_edgecolor_matches_canonical():
    """DEFAULTS used '#808080' while the Click option, the README, and
    package.json all used '#707070'. After the fix, DEFAULTS is the
    single source of truth and must match the canonical value."""
    from ocp_vscode.standalone_defaults import DEFAULTS

    assert DEFAULTS["default_edgecolor"] == "#707070"


# ---------------------------------------------------------------------------
# Fundamental runtime smoke tests
#
# These guard against whole classes of "the standalone is broken" regressions
# that earlier escaped the per-flag tests above — hangs, missing acks, fallback
# dicts that poison downstream callers, and silent drift between standalone
# defaults and the VS Code workspace settings.
# ---------------------------------------------------------------------------


def _run_with_timeout(fn, timeout):
    """Run `fn` in a daemon thread; return (ok, result_or_exc).

    `ok=False, result=None` means the call did not finish within `timeout`.
    The thread is left running (daemon) — the parent process exit cleans it
    up. Cross-platform alternative to `signal.alarm` (which is Unix-only).
    """
    import threading

    box = {"result": None, "exc": None, "done": False}

    def runner():
        try:
            box["result"] = fn()
        except BaseException as ex:  # pylint: disable=broad-except
            box["exc"] = ex
        finally:
            box["done"] = True

    t = threading.Thread(target=runner, daemon=True)
    t.start()
    t.join(timeout=timeout)
    if not box["done"]:
        return False, None
    if box["exc"] is not None:
        raise box["exc"]
    return True, box["result"]


def test_show_against_fresh_standalone_does_not_hang(standalone):
    """A bare `show(box)` against a freshly spawned standalone must complete
    in seconds. This is the regression test for the missing `B:` ack bug
    (`standalone.py` not sending `{"ok": True}` to `comms.py:_send` waiting
    on `ws.recv()`), which presents as `show()` hanging forever."""
    import cadquery as cq
    from ocp_vscode import show

    proc = standalone()
    _wait_for_config(STANDALONE_PORT, proc)  # ensure WS is alive

    box = cq.Workplane().box(10, 20, 30)
    ok, _ = _run_with_timeout(lambda: show(box), timeout=15.0)
    assert ok, (
        "show() did not return within 15 s against a fresh standalone — "
        "almost certainly a missing-ack regression on the Python↔standalone "
        "protocol (see commit c393150 for the original asymmetry)."
    )


def test_status_after_show_returns_safe_collapse(standalone):
    """After `show()`, `status()` must return either a `Collapse` enum or
    `None` for the collapse key — never a string. A string here means
    `comms.py:_send`'s fallback dict was hit (connection error path) and is
    leaking its bogus `"collapse": "none"` placeholder into downstream
    callers that try `.value` on it."""
    import cadquery as cq
    from ocp_vscode import Collapse, show, status

    proc = standalone()
    _wait_for_config(STANDALONE_PORT, proc)

    show(cq.Workplane().box(10, 20, 30))
    s = status()
    cval = s.get("collapse")
    assert cval is None or isinstance(cval, Collapse), (
        f"status()['collapse'] should be a Collapse enum or None; got "
        f"{cval!r} ({type(cval).__name__}). If it's a string, the fallback "
        f"dict in comms._send is leaking through."
    )


def test_send_fallback_does_not_poison_collapse():
    """Pointing at a dead port forces `_send` into its connection-error
    fallback. The returned dict must use a `Collapse` enum (or omit the
    key), never the string `"none"` — otherwise downstream `.value` calls
    in `show.py` crash with `AttributeError`."""
    from ocp_vscode import Collapse
    from ocp_vscode.comms import send_command

    DEAD_PORT = 39555  # nothing should be listening here
    result = send_command("config", port=DEAD_PORT)
    cval = result.get("collapse")
    # If the key is absent that's fine; if present it must be an enum.
    assert cval is None or isinstance(cval, Collapse), (
        f"send_command fallback returned collapse={cval!r} "
        f"({type(cval).__name__}); must be Collapse enum or absent."
    )


def test_standalone_defaults_match_package_json():
    """Drift guard: every key declared in both `package.json`'s view/render
    workspace settings and `ocp_vscode/standalone_defaults.py:DEFAULTS` must
    agree on the default value. Catches the class of bug where one side
    moves and the other doesn't (e.g. default_edgecolor `#707070` vs
    `#808080`, axes0 `True` vs `False`)."""
    import json
    import pathlib

    from ocp_vscode.standalone_defaults import DEFAULTS

    pkg_path = pathlib.Path(__file__).parent.parent / "package.json"
    pkg = json.loads(pkg_path.read_text())
    props = pkg["contributes"]["configuration"]["properties"]

    mismatches = []
    for full_key, spec in props.items():
        # Only OcpCadViewer.view.* and OcpCadViewer.render.* map to DEFAULTS.
        if not (
            full_key.startswith("OcpCadViewer.view.")
            or full_key.startswith("OcpCadViewer.render.")
        ):
            continue
        short = full_key.split(".", 2)[2]
        # Lowercase grid_XY/YZ/XZ in package.json vs grid_xy/yz/xz in DEFAULTS.
        short_norm = short.lower() if short.startswith("grid_") else short
        if short_norm not in DEFAULTS:
            continue  # standalone-side only; no drift possible
        if DEFAULTS[short_norm] != spec.get("default"):
            mismatches.append(
                f"  {short_norm}: standalone={DEFAULTS[short_norm]!r}, "
                f"package.json={spec.get('default')!r}"
            )
    assert not mismatches, (
        "DEFAULTS drift between standalone_defaults.py and package.json:\n"
        + "\n".join(mismatches)
    )
