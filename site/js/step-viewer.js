/* ============================================================================
 *  STEP VIEWER  —  in-browser 3D viewer for .step / .stp CAD files
 * ----------------------------------------------------------------------------
 *  Parses STEP geometry with occt-import-js (WASM) and renders it with three.js.
 *  You should never need to edit this file. To put a model on a project page,
 *  just add a `model:` field to that project in js/data.js, e.g.
 *      model: "assets/files/my-board.step"
 *  The project page then shows a "Load 3D model" button that calls mountViewer().
 * ========================================================================== */

import * as THREE from "three";
import { OrbitControls } from "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/controls/OrbitControls.js";

const OCCT_JS  = "https://cdn.jsdelivr.net/npm/occt-import-js@0.0.23/dist/occt-import-js.js";
const OCCT_WASM = "https://cdn.jsdelivr.net/npm/occt-import-js@0.0.23/dist/occt-import-js.wasm";

let occtPromise = null;
// Load the WASM importer once and reuse it across viewers on the page.
function loadOcct() {
  if (occtPromise) return occtPromise;
  occtPromise = new Promise(function (resolve, reject) {
    var s = document.createElement("script");
    s.src = OCCT_JS;
    s.onload = function () {
      // occt-import-js exposes a global factory function `occtimportjs`.
      window.occtimportjs({ locateFile: function () { return OCCT_WASM; } })
        .then(resolve).catch(reject);
    };
    s.onerror = function () { reject(new Error("Failed to load the 3D engine (occt-import-js).")); };
    document.head.appendChild(s);
  });
  return occtPromise;
}

/**
 * Mount an interactive 3D viewer into `container` for the STEP file at `url`.
 * Reports progress through the optional `onStatus(text)` callback.
 */
export async function mountViewer(container, url, onStatus) {
  var status = onStatus || function () {};

  status("Loading 3D engine…");
  var occt = await loadOcct();

  status("Downloading model…");
  var res = await fetch(url);
  if (!res.ok) throw new Error("Could not download the model file (" + res.status + ").");
  var buf = new Uint8Array(await res.arrayBuffer());

  status("Reading CAD geometry…");
  var result = occt.ReadStepFile(buf, null);
  if (!result || !result.success || !result.meshes || !result.meshes.length) {
    throw new Error("This STEP file could not be read.");
  }

  status("Building scene…");
  container.innerHTML = "";

  // ---- three.js scene ----
  var width = container.clientWidth || 800;
  var height = container.clientHeight || 480;

  var scene = new THREE.Scene();
  scene.background = null; // transparent — page background shows through

  var camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100000);

  var renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setSize(width, height);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  container.appendChild(renderer.domElement);

  // Lighting
  scene.add(new THREE.AmbientLight(0xffffff, 0.65));
  var key = new THREE.DirectionalLight(0xffffff, 0.9); key.position.set(1, 1.5, 1); scene.add(key);
  var fill = new THREE.DirectionalLight(0xffffff, 0.45); fill.position.set(-1, -0.5, -1); scene.add(fill);

  // ---- build geometry from the parsed meshes ----
  var group = new THREE.Group();
  result.meshes.forEach(function (mesh) {
    var geom = new THREE.BufferGeometry();
    geom.setAttribute("position", new THREE.Float32BufferAttribute(mesh.attributes.position.array, 3));
    if (mesh.attributes.normal) {
      geom.setAttribute("normal", new THREE.Float32BufferAttribute(mesh.attributes.normal.array, 3));
    }
    if (mesh.index) {
      geom.setIndex(new THREE.Uint32BufferAttribute(mesh.index.array, 1));
    }
    if (!mesh.attributes.normal) geom.computeVertexNormals();

    var color = 0x9aa3b2;
    if (mesh.color) {
      color = new THREE.Color(mesh.color[0], mesh.color[1], mesh.color[2]).getHex();
    }
    var mat = new THREE.MeshStandardMaterial({ color: color, metalness: 0.25, roughness: 0.6 });
    group.add(new THREE.Mesh(geom, mat));
  });
  scene.add(group);

  // ---- center & frame the model ----
  var box = new THREE.Box3().setFromObject(group);
  var center = box.getCenter(new THREE.Vector3());
  var size = box.getSize(new THREE.Vector3());
  group.position.sub(center); // recenter on origin

  var maxDim = Math.max(size.x, size.y, size.z) || 1;
  var dist = (maxDim / 2) / Math.tan((camera.fov * Math.PI) / 360);
  dist *= 1.8;
  camera.position.set(dist * 0.8, dist * 0.6, dist);
  camera.near = maxDim / 100;
  camera.far = dist * 100;
  camera.updateProjectionMatrix();

  var controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.target.set(0, 0, 0);

  // ---- responsive ----
  function resize() {
    var w = container.clientWidth, h = container.clientHeight;
    if (!w || !h) return;
    camera.aspect = w / h; camera.updateProjectionMatrix();
    renderer.setSize(w, h);
  }
  window.addEventListener("resize", resize);

  // ---- render loop ----
  var running = true;
  (function loop() {
    if (!running) return;
    requestAnimationFrame(loop);
    controls.update();
    renderer.render(scene, camera);
  })();

  status("");

  // return a small handle so the caller can clean up if needed
  return {
    reset: function () {
      camera.position.set(dist * 0.8, dist * 0.6, dist);
      controls.target.set(0, 0, 0); controls.update();
    },
    dispose: function () {
      running = false;
      window.removeEventListener("resize", resize);
      renderer.dispose();
      container.innerHTML = "";
    }
  };
}
