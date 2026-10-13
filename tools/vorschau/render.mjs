// Rendert scene.json + atlas.png (aus quads.py) mit three.js in headless Chromium.
// node render.mjs <scene-dir> <out.png> [ansicht: se|sw|ne|nw|top|s|n] [breite] [höhe] [zoom]
import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';
import url from 'url';

const here = path.dirname(url.fileURLToPath(import.meta.url));
const [sceneDir, out, view = 'se', W = '1600', H = '1000', zoom = '1'] = process.argv.slice(2);

const html = `<!doctype html><html><body style="margin:0;background:#9cc7f0">
<canvas id="c" width="${W}" height="${H}"></canvas>
<script type="module">
import * as THREE from 'http://r.local/three.module.js';
const scene = await (await fetch('http://r.local/scene/scene.json')).json();
const tex = await new THREE.TextureLoader().loadAsync('http://r.local/scene/atlas.png');
tex.magFilter = THREE.NearestFilter; tex.minFilter = THREE.NearestFilter; tex.colorSpace = THREE.SRGBColorSpace;
tex.generateMipmaps = false;
const g = new THREE.BufferGeometry();
g.setAttribute('position', new THREE.Float32BufferAttribute(scene.pos, 3));
g.setAttribute('uv', new THREE.Float32BufferAttribute(scene.uv, 2));
g.setAttribute('color', new THREE.Float32BufferAttribute(scene.col, 3));
const mat = new THREE.MeshBasicMaterial({map: tex, vertexColors: true, alphaTest: 0.1, side: THREE.DoubleSide, transparent: false});
const mesh = new THREE.Mesh(g, mat);
const s = new THREE.Scene();
s.background = new THREE.Color('#a9cdee');
s.add(mesh);
g.computeBoundingBox();
const bb = g.boundingBox;
const c = new THREE.Vector3(); bb.getCenter(c);
const size = new THREE.Vector3(); bb.getSize(size);
const r = size.length() / 2;
const renderer = new THREE.WebGLRenderer({canvas: document.getElementById('c'), antialias: true, preserveDrawingBuffer: true});
renderer.outputColorSpace = THREE.SRGBColorSpace;
const aspect = ${W} / ${H};
const z = ${zoom};
const cam = new THREE.OrthographicCamera(-r * aspect / z, r * aspect / z, r / z, -r / z, -1000, 1000);
const dirs = {se: [1, 0.85, 1.25], sw: [-1, 0.85, 1.25], ne: [1, 0.85, -1.25], nw: [-1, 0.85, -1.25], top: [0.001, 1, 0.3], s: [0.0, 0.5, 1], n: [0, 0.5, -1]};
const d = new THREE.Vector3(...dirs['${view}']).normalize();
cam.position.copy(c).addScaledVector(d, 200);
cam.lookAt(c);
renderer.render(s, cam);
window.done = true;
</script></body></html>`;

const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await browser.newPage({ viewport: { width: +W, height: +H } });
page.on('console', (m) => console.log('browser:', m.text()));
page.on('pageerror', (e) => console.log('pageerror:', e.message));
await page.route('http://r.local/**', async (route) => {
  const u = new URL(route.request().url());
  let file;
  if (u.pathname === '/index.html') return route.fulfill({ body: html, contentType: 'text/html' });
  if (u.pathname === '/three.module.js') file = path.join(here, 'node_modules/three/build/three.module.js');
  else if (u.pathname === '/three.core.js') file = path.join(here, 'node_modules/three/build/three.core.js');
  else if (u.pathname.startsWith('/scene/')) file = path.join(sceneDir, u.pathname.slice(7));
  if (!file || !fs.existsSync(file)) return route.fulfill({ status: 404, body: 'nf' });
  const type = file.endsWith('.js') ? 'text/javascript' : file.endsWith('.png') ? 'image/png' : 'application/json';
  route.fulfill({ body: fs.readFileSync(file), contentType: type });
});
await page.goto('http://r.local/index.html');
await page.waitForFunction('window.done === true', null, { timeout: 120000 });
await page.locator('#c').screenshot({ path: out });
await browser.close();
console.log('ok', out);
