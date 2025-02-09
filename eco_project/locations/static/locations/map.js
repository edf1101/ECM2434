import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';

function getLocation() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(showPosition);
  } else {
    console.log("Geolocation is not supported by this browser.");
  }
}

function showPosition(position) {
   console.log("Latitude: " + position.coords.latitude +
  "<br>Longitude: " + position.coords.longitude);
}

getLocation();

// Fetch nearby tiles
async function fetchNearbyTiles(lat, lon, distance = 100) {
    const response = await fetch(`/locations/api/nearby-tiles/?lat=${lat}&lon=${lon}&distance=${distance}`);
    const data = await response.json();
    return data;
}

async function getMapData() {
    const response = await fetch(`/locations/api/map_data`);
    const data = await response.json();
    return data;
}

// get and save the map data to variables max_lat, min_lat, max_lon, min_lon
let max_lat = 0.0;
let min_lat = 0.0;
let max_lon = 0.0;
let min_lon = 0;

let maxX = 0;
let minX = 0;
let maxY = 0;
let minY = 0;
getMapData().then(data => {
    // Access the first element in the array
    const mapData = data[0];

    // Now, extract the properties
    max_lat = parseFloat(mapData['max_lat']);
    min_lat = parseFloat(mapData['min_lat']);
    max_lon = mapData['max_lon'];
    min_lon = mapData['min_lon'];

    maxX = mapData['max_x'];
    minX = mapData['min_x'];
    maxY = mapData['max_y'];
    minY = mapData['min_y'];

});



// write a function to convert lat, lon to x, y
function latLonToXY(lat, lon) {
    let x = (lon - min_lon) / (max_lon - min_lon) * (maxX - minX) + minX;
    let y = (lat - min_lat) / (max_lat - min_lat) * (maxY - minY) + minY;
    return [x, y];
}


// Renderer setup
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setClearColor(0x5ac598);
renderer.setPixelRatio(window.devicePixelRatio);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

// Scene & Camera setup
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(
  45, window.innerWidth / window.innerHeight, 1, 1000
);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.enablePan = false;
controls.minDistance = 5;
controls.maxDistance = 5;
controls.minPolarAngle = 0.3;
controls.maxPolarAngle = 1.5;
controls.autoRotate = false;
controls.target = new THREE.Vector3(-77, 184, 24);
controls.update();

THREE.ShaderChunk.fog_vertex = `#ifdef USE_FOG\n\tvFogDepth = length( mvPosition );\n#endif`;
scene.fog = new THREE.Fog( 0x5ac598, 150, 200 );

// --- Draco Loader Setup ---
const dracoLoader = new DRACOLoader();
// Set the path to the Draco decoder files (using Google's hosted decoders)
dracoLoader.setDecoderPath('https://www.gstatic.com/draco/versioned/decoders/1.4.3/');

// --- GLTF Loader Setup ---
const loader = new GLTFLoader();
loader.setDRACOLoader(dracoLoader);

let lat = 50.7351111;
let lng = -3.5343202;

// Fetch and load models based on nearby tiles
fetchNearbyTiles(lat, lng, 250).then(data => {
    let meshSources = [];

    // Add the mesh sources (GLB file paths)
    data.forEach(tile => {
        meshSources.push(tile.file);
    });


    // Now load each GLB model
    meshSources.forEach((source, index) => {
        loader.load(
            source,
            (gltf) => {
                const mesh = gltf.scene;

                // Enable shadows on each mesh
                mesh.traverse((child) => {
                    if (child.isMesh) {
                        child.castShadow = true;
                        child.receiveShadow = true;
                    }
                });

                // Position each mesh. Adjust the offset as needed.
                mesh.position.set(0, 0, 0);
                scene.add(mesh);
            },
            (xhr) => {
                // console.log(`Loading ${source}: ${(xhr.loaded / xhr.total * 100).toFixed(2)}%`);
            },
            (error) => {
                // console.error('An error occurred loading', source, error);
            }
        );
    });
});

// Handle window resizing
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// Animation loop
function animate() {
  requestAnimationFrame(animate);

  let xy = latLonToXY(lat, lng);
  // console.log(xy);

  // Log the individual values to check
  const x = xy[0];
  const y = 200;
  const z = -xy[1];
  // console.log(x, y, z); // Log individual values

  // Check for NaN before setting the target
  if (isNaN(x) || isNaN(y) || isNaN(z)) {
    console.error("Invalid values detected:", x, y, z);
  } else {
    controls.target = new THREE.Vector3(x, y, z);
  }
    // console.log(controls.target);
  controls.update();
  renderer.render(scene, camera);
}

animate();


animate();
