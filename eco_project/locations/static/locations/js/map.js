import * as THREE from '../../three/build/three.module.js';
import {OrbitControls} from '../../three/jsm/controls/OrbitControls.js';
import {GeoHelper} from '/static/js/geolocation.js';
import {GltfLoader} from '/static/locations/js/gltfLoader.js';

/**
 * Main application class that sets up a Three.js scene with chunked map tiles,
 *  a camera that follows an API fetched user location, and custom feature markers.
 */
export class UniversityMap {
    /**
     * Initialises the UniversityMap application. By setting up the Three.js app,
     * getting basic map settings and starting API calls.
     */
    constructor(containerId = "map") {
        this.containerId = containerId;
        this._initLocationAndMapData(); // Initialize map data and location.
        this._initThreeJS();            // Set up the Three.js scene.
        window.addEventListener('resize', () => this._onWindowResize());
        this._animate();
        this.gltfLoader = new GltfLoader();
        setInterval(() => this._checkNeedUpdateLocation(), 5000);
    }

    /* Initialisation methods */
    /**
     * This function sets up all the important map settings data, ie the bounds for the scene,
     * height maps etc.
     * @return {Promise<void>} Promises that the async action has completed
     * @private
     */
    async _initLocationAndMapData() {
        this.activeMarkers = []; // stores the rotating markers

        // Default coordinates (to be updated by the API).
        this.render_dist = 250;
        this.heightOffset = 50;
        // Map bounds (latitude/longitude) details.
        this.mapBounds = {maxLat: 0, minLat: 0, maxLon: 0, minLon: 0};

        // Grid definitions for the map (x/y/z coordinates).
        this.mapGrid = {maxX: 0, minX: 0, maxY: 0, minY: 0};

        // Dictionary for keeping track of loaded tiles.
        this.loadedTiles = {};
        this.nameToId = {};

        // Canvas element to hold the heightmap image data.
        this.heightMapCanvas = null;

        try {
            // Retrieve initial coordinates from the API.
            const [lat, lon] = await GeoHelper.requestCurrentLocation();
            this.lat = lat;
            this.lng = lon; // consistently use 'lng' for longitude

            // Fetch map details and load the heightmap image.
            await this._initMapSettings();

            // Update the scene based on the new location.
            await this._changeLocation(this.lat, this.lng);
        } catch (error) {
            console.error("Error during initial location and map data initialization:", error);
        }
    }

    /**
     * This function initialises the ThreeJS scene, renderer, camera etc.
     * @private
     */
    _initThreeJS() {
        // Get the container element using the passed containerId.
        const container = document.getElementById(this.containerId);
        if (!container) {
            console.error(`Container with id "${this.containerId}" not found.`);
            return;
        }

        // Set up the renderer.
        this.renderer = new THREE.WebGLRenderer({antialias: true});
        this.renderer.outputColorSpace = THREE.SRGBColorSpace;
        this.renderer.setSize(container.clientWidth, container.clientHeight);
        this.renderer.setClearColor(0x5ac598);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        // Append the renderer to the container.
        container.appendChild(this.renderer.domElement);
        this.scene = new THREE.Scene();

        // Override default fog vertex shader chunk.
        THREE.ShaderChunk.fog_vertex = `
      #ifdef USE_FOG
        vFogDepth = length( mvPosition );
      #endif
    `;

        // Set up lighting.
        const ambientLight = new THREE.AmbientLight(0xffffff, 1);
        const directionalLight = new THREE.DirectionalLight(0xffffff, 2);
        directionalLight.position.set(10, 100, 200);
        directionalLight.castShadow = true;
        this.scene.add(directionalLight);
        this.scene.add(ambientLight);

        // Set up camera.
        this.camera = new THREE.PerspectiveCamera(
            45,
            container.clientWidth / container.clientHeight,
            1,
            300
        );

        // Set up orbit controls
        this.controls = new OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.enablePan = false;
        this.controls.minDistance = 2;
        this.controls.maxDistance = 7;
        this.controls.minPolarAngle = 0.3;
        this.controls.maxPolarAngle = 1.5;
        this.controls.autoRotate = false;
        this.controls.target.set(-77, 184, 24); // initial target position (update later)
        this.controls.update();
    }

    /**
     * Loads a heightmap image from a URL and stores its data in an offscreen canvas for easy pixel
     * access.
     *
     * @param {string} url - The URL of the heightmap image to load into the app
     * @return {Promise} Promise that resolves when the heightmap is fully loaded.
     */
    _initHeightMap(url) {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.crossOrigin = "anonymous";
            img.src = url;
            // Create a canvas so that we can read the pixel data.
            img.onload = () => {
                const canvas = document.createElement('canvas');
                canvas.width = img.width;
                canvas.height = img.height;
                const contex = canvas.getContext('2d');
                contex.drawImage(img, 0, 0);
                this.heightMapCanvas = canvas;
                resolve(canvas);
            };
            img.onerror = (error) => { // handle any errors nicely
                console.error("Error loading heightmap image:", error);
                reject(error);
            };
        });
    }

    /**
     * Fetches map data from the API, updates map bounds and grid values,
     * and loads the heightmap image.
     * @return {Promise} returns a promise that the map data has been loaded successfully.
     */
    async _initMapSettings() {
        try {
            const response = await fetch(`/locations/api/map_data`);
            const data = await response.json();

            if (data.length === 0) {
                return; // No data to process.
            }


            const mapData = data[0]; // Use the first entry of the returned data.
            // Get the bounds data for lat/lon and xyz
            this.mapBounds = {
                maxLat: parseFloat(mapData.max_lat), minLat: parseFloat(mapData.min_lat),
                maxLon: parseFloat(mapData.max_lon), minLon: parseFloat(mapData.min_lon)
            };

            this.mapGrid = {
                maxX: mapData.max_x, minX: mapData.min_x,
                maxY: mapData.max_y, minY: mapData.min_y,
                minZ: mapData.min_z, maxZ: mapData.max_z
            };

            const heightmapUrl = mapData.camera_map_url;
            await this._initHeightMap(heightmapUrl);

            const colour = mapData.bg_colour;
            this.render_dist = mapData.render_dist;
            this.camera.far = this.render_dist;
            this.camera.updateProjectionMatrix();
            this.scene.fog = new THREE.Fog(colour, Math.max(30, this.render_dist - 100),
                Math.max(100, this.render_dist - 50));
            this.renderer.setClearColor(colour);
        } catch (error) {
            console.error("Error fetching map data:", error);
        }
    }

    /* Chunk creation / deletion methods */

    /**
     * Retrieves an array of nearby tile file names from the API for a given location.
     *
     * @param {number} lat - Latitude
     * @param {number} lon - Longitude
     * @param {number} [radius=this.render_dist] - Search radius (default is this.render_dist).
     * @return {Promise<Array>} Promise resolving to an array of tile file names.
     */
    async getNearbyTiles(lat, lon, radius = this.render_dist) {
        if (!lat || !lon || isNaN(lat) || isNaN(lon)) {
            return []; // Coords aren't loaded yet
        }
        // Send API request to server to get nearby tiles.
        const response = await fetch(`/locations/api/nearby-tiles/?lat=${lat}&lon=${lon}&distance=${radius}`);
        const data = await response.json();

        const nearbyTileNames = []; // add them to the name-id map and return list of names
        for (const tile of data) {
            nearbyTileNames.push(tile['file']);
            // Create a name-to-id table.
            this.nameToId[tile['file']] = tile['id'];
        }
        return nearbyTileNames;
    }

    /**
     * Loads nearby 3D chunks into the scene based on the provided geodesic location.
     *
     * @param {number} lat - Latitude.
     * @param {number} lon - Longitude.
     * @param {number} [radius=this.render_dist] - Search radius (default is this.render_dist).
     */
    async _loadNearbyTiles(lat, lon, radius = this.render_dist) {
        // Retrieve the list of nearby tile names.
        const tileNames = await this.getNearbyTiles(lat, lon, this.render_dist);

        // Get the feature instances for the given tiles.
        let features_at_tiles = await this._getFeatureInstancesForTiles(tileNames);

        // Load each tile that hasn't already been loaded.
        for (const name of tileNames) {
            if (!this.loadedTiles[name]) {
                try {
                    // Load (maybe from cache) the GLTF asset.
                    const gltf = await this.gltfLoader.loadGLTF(name);
                    const mesh = gltf.scene;

                    // Position the tile
                    mesh.position.set(0, 0, 0);
                    this.scene.add(mesh);
                    this.loadedTiles[name] = mesh;

                    // Load in feature markers for this tile
                    if (features_at_tiles) {
                        if (features_at_tiles[name]) {
                            for (const feature of features_at_tiles[name]) {
                                const lat = feature['lat'];
                                const lon = feature['lon'];
                                const colour = feature['colour'];
                                const mesh_url = feature['mesh_url'];
                                await this.createMarker(lat, lon, colour, mesh, mesh_url);
                            }
                        } else { // error check if tile isnt in features table
                            console.error("Tile name not found in features at tiles table:", name);
                        }
                    } else { // error check if no features table
                        console.error("No features at tiles table found");
                    }
                } catch (error) { // handle any other tile errors nicely
                    console.error("Error loading tile:", name, error);
                }
            }
        }
    }

    /**
     * Unloads 3D tiles that aren't nearby for the specified location.
     *
     * @param {number} lat - Latitude.
     * @param {number} lon - Longitude.
     * @param {number} [radius=this.render_dist] - Valid area radius (default is this.render_dist).
     */
    async _unloadTiles(lat, lon, radius = this.render_dist) {
        const validTileNames = await this.getNearbyTiles(lat, lon, radius);

        // Remove any tiles that aren't nearby
        for (const name in this.loadedTiles) {
            if (!validTileNames.includes(name)) {
                const tile = this.loadedTiles[name];

                // Remove markers attached to this tile from activeMarkers
                this.activeMarkers = this.activeMarkers.filter(marker => {
                    if (marker.userData.parentTile === tile) {
                        if (marker.parent) {
                            marker.parent.remove(marker);
                        }
                        return false;
                    }
                    return true;
                });

                // Remove the tile from the scene and dispose its resources to ensure child marker
                // are removed
                this.scene.remove(tile);
                tile.traverse(child => {
                    if (child.isMesh) {
                        child.geometry.dispose();
                        child.material.dispose();
                    }
                });
                delete this.loadedTiles[name];
            }
        }
    }


    /**
     * Wait until all expected tiles for a given location are loaded or until a timeout.
     *
     * @param {number} lat - Latitude.
     * @param {number} lon - Longitude.
     * @param {number} [radius=this.render_dist] - Search radius (default this.render_dist)
     * @param {number} [timeout=5000] - Timeout time (default 5000ms)
     */
    async _waitForTiles(lat, lon, radius = this.render_dist, timeout = 5000) {
        const startTime = performance.now();
        const expectedTiles = await this.getNearbyTiles(lat, lon, radius);

        // Wait until all tiles are loaded or timed out
        while (true) {
            if (expectedTiles.every(name => name in this.loadedTiles)) {
                return;
            }
            if (performance.now() - startTime > timeout) {
                return;
            }
            // Wait 100ms before checking again.
            await new Promise(resolve => setTimeout(resolve, 100));
        }
    }

    /* Marker creation methods */

    /**
     * This creates a marker for a custom feature at a given Lat, lon
     * @param {number} lat -  The marker's latitude
     * @param {number} lon - The marker's longitude
     * @param {number|string} colour - The colour of the marker
     * @param {THREE.Object3D} parent - The parent object to attach the marker to
     * @param {string} [custom_mesh_url] - The URL to fetch a custom marker from
     * @return {Promise<void>} A promise resolving when the marker has been created.
     */
    async createMarker(lat, lon, colour, parent, custom_mesh_url = "None") {
        // Convert geographic coordinates to scene coordinates.

        // create a ray from above the x,z position to the floor to get the y position
        const [x, y] = this._latLonToXY(lat, lon);
        const raycaster = new THREE.Raycaster(new THREE.Vector3(x, 400, -y), new THREE.Vector3(0, -1, 0));
        const intersects = raycaster.intersectObject(parent, true);
        let z = (intersects.length > 0) ? intersects[0].point.y + 2.5 : 0;

        // Create the cylinder mesh for the marker.
        const geometry = new THREE.CylinderGeometry(0.2, 0.2, 5, 32);
        const material = new THREE.MeshPhongMaterial({color: colour});
        const cylinder = new THREE.Mesh(geometry, material);
        cylinder.castShadow = true;
        cylinder.receiveShadow = true;
        cylinder.position.set(x, z, -y);
        parent.add(cylinder);

        // Create the top marker object
        let object;
        if (custom_mesh_url === "None") { // no custom marker top specified so make sphere
            // Create a small sphere to sit on top of the cylinder.
            const sphereGeometry = new THREE.SphereGeometry(1, 32, 32);
            const sphereMaterial = new THREE.MeshPhongMaterial({color: colour});
            object = new THREE.Mesh(sphereGeometry, sphereMaterial);

        } else {
            // Create and load the custom mesh.
            const gltf = await this.gltfLoader.loadGLTF(custom_mesh_url);
            object = gltf.scene;
        }

        // set top marker shadow properties and material colour for all children
        object.traverse((child) => {
            if (child.isMesh) {
                child.castShadow = true;
                child.receiveShadow = true;
                child.material.color.set(colour);
                child.material.metalness = 0.0;
                child.material.roughness = 1.0;
            }
        });

        // Position the custom mesh relative to the cylinder so that it sits on top.
        object.position.set(0, 4, 0);
        cylinder.add(object);
        Object.defineProperty(object, 'parentTile', {
            value: parent,
            writable: true,
            configurable: true,
            enumerable: false, // This prevents the property from being enumerated in JSON.stringify.
        });
        // object.userData.parentTile = parent;
        this.activeMarkers.push(object); // Add the custom mesh to the list of rotating markers.
    }


    /**
     * This function takes in a list of tiles and retrieves the feature instances that are within
     * all of said tiles
     *
     * @param tiles The list of tiles to retrieve feature instances for
     * @return {Promise<void>} A promise that resolves when the feature instances have been retrieved
     * (Also returns the response).
     * @private
     */
    async _getFeatureInstancesForTiles(tiles) {
        // Make a list of tile ids from the tiles list which is comprised of names.
        const tileIds = [];
        for (const tile of tiles) {
            if (tile in this.nameToId) {
                tileIds.push(this.nameToId[tile]);
            } else {
                console.error("Tile name not found in name to id table:", tile);
            }
        }

        if (tileIds.length === 0) {
            return; // No need to make a request if there are no tile ids.
        }

        // Actually make and return request.
        const response = await fetch(`/locations/api/get_features_for_tile/?tiles=${tileIds}`);
        const data = await response.json();

        return data;
    }

    /* Location calculation methods */
    /**
     * Converts lat and lon coordinates to an [x, y] position
     * on the scene's map grid by lerping between bounds
     *
     * @param {number} lat - Latitude
     * @param {number} lon - Longitude
     * @return {[number, number]} An array containing the x and y coordinates.
     */
    _latLonToXY(lat, lon) {
        // open up the bounds for the scene
        const {maxLat, minLat, maxLon, minLon} = this.mapBounds;
        const {maxX, minX, maxY, minY} = this.mapGrid;

        // lerp between the min and max values to get the x and y values
        const x = ((lon - minLon) / (maxLon - minLon)) * (maxX - minX) + minX;
        const y = ((lat - minLat) / (maxLat - minLat)) * (maxY - minY) + minY;
        return [x, y];
    }

    /**
     * Calculates the height coordinate for a given position by reading and lerping from the
     * height map canvas.
     *
     * @param {number} lat - Latitude
     * @param {number} lon - Longitude
     * @return {number|null} The calculated terrain height or null if not loaded.
     */
    _getHeightAtPos(lat, lon) {
        if (!this.heightMapCanvas) {
            return null; // Heightmap not loaded
        }
        // Convert geographic coordinates to grid positions.
        const [x, y] = this._latLonToXY(lat, lon);
        const {minX, maxX, minY, maxY, minZ, maxZ} = this.mapGrid;

        // Normalize the grid coordinates.
        let pixelX = Math.floor(((x - minX) / (maxX - minX)) * this.heightMapCanvas.width);
        // Invert Y to match the image coordinate system.
        let pixelY = Math.floor((1 - (y - minY) / (maxY - minY)) * this.heightMapCanvas.height);
        pixelX = Math.min(Math.max(pixelX, 0), this.heightMapCanvas.width);
        pixelY = Math.min(Math.max(pixelY, 0), this.heightMapCanvas.height);

        // Read the pixel data from the canvas.
        const context = this.heightMapCanvas.getContext('2d', {willReadFrequently: true});
        const pixelValue = context.getImageData(pixelX, pixelY, 1, 1).data[0];
        return (pixelValue / 255) * (maxZ - minZ) + minZ;
    }

    /**
     * Checks whether the location has changed since last tile update and reloads tiles if so.
     */
    async _checkNeedUpdateLocation() {
        const [newLat, newLon] = await GeoHelper.requestCurrentLocation();
        const delta = GeoHelper.haversineDistance(this.lat, this.lng, newLat, newLon);

        const threshold = 50; // If changed > 50m then update location
        if (delta > threshold) {
            await this._changeLocation(newLat, newLon);
        }
    }

    /**
     * Changes the current location by lerping the camera's position and loading new tiles.
     *
     * @param {number} newLat - The new latitude.
     * @param {number} newLon - The new longitude.
     */
    async _changeLocation(newLat, newLon) {
        // Store the previous location.
        const oldLat = this.lat;
        const oldLon = this.lng;

        // When the camera is lerping from one location to another, we don't want unloaded tiles
        // along the way, so load tiles at intermediary steps along the path

        // Determine the number of intermediate steps (approximately every 100 meters).
        const steps = Math.ceil(GeoHelper.haversineDistance(oldLat, oldLon, newLat, newLon) /
            (this.render_dist / 2));

        // Load tiles for each intermediate interval.
        for (let i = 1; i < steps; i++) {
            const intermediateLat = oldLat + (i / steps) * (newLat - oldLat);
            const intermediateLon = oldLon + (i / steps) * (newLon - oldLon);
            // load and wait for intermediate tiles
            await this._loadNearbyTiles(intermediateLat, intermediateLon, this.render_dist);
            await this._waitForTiles(intermediateLat, intermediateLon, this.render_dist);
        }
        // load and wait for final lat/lon tiles
        await this._loadNearbyTiles(newLat, newLon, this.render_dist);
        await this._waitForTiles(newLat, newLon, this.render_dist);

        // Convert the new geographic coordinates to scene coordinates.
        const [newX, newY] = this._latLonToXY(newLat, newLon);
        let newHeight = this._getHeightAtPos(newLat, newLon);
        newHeight = newHeight !== null ? newHeight + this.heightOffset : this.heightOffset;
        const newPos = new THREE.Vector3(newX, newHeight, -newY);

        // lerp the camera to the new position while preserving the rotation offset.
        const offset = this.controls.target.clone().sub(this.camera.position);
        await this._lerpCamera(this.camera.position.clone(), newPos, offset, 1000);

        // Update stored location.
        this.lat = newLat;
        this.lng = newLon;

        await this._unloadTiles(newLat, newLon); // Unload tiles that aren't near anymore
    }

    /* Camera and rendering methods */

    /**
     * Adjusts camera and renderer settings on window resize.
     */
    _onWindowResize() {
        const container = document.getElementById(this.containerId);
        if (!container) return;
        this.camera.aspect = container.clientWidth / container.clientHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(container.clientWidth, container.clientHeight);
    }

    /**
     * The main animation loop that updates controls and renders the scene.
     */
    _animate() {

        if (!this.renderer || !this.scene || !this.camera || !this.controls) {
            return;
        }
        requestAnimationFrame(() => this._animate());

        // Rotate each marker in our rotatingMarkers array.
        this.activeMarkers.forEach(marker => {
            marker.rotation.y += 0.01;
            // make marker bob up and down
            marker.position.y = Math.sin(Date.now() * 0.002) * 0.3 + 4;
        });

        this.controls.update();
        this.renderer.render(this.scene, this.camera);
    }


    /**
     * Lerps the camera from a starting position to an end position while preserving the rotation.
     *
     * @param {THREE.Vector3} startPos - The start camera position.
     * @param {THREE.Vector3} endPos - The end camera position.
     * @param {THREE.Vector3} offset - The offset from the camera to its target.
     * @param {number} duration - The duration of the tween in ms.
     * @return {Promise} A promise that resolves when the tween is complete.
     */
    _lerpCamera(startPos, endPos, offset, duration) {

        function easeInOutQuad(t) { // Easing function: quadratic ease-in/out.
            return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
        }

        return new Promise((resolve) => {
            const startTime = performance.now();

            const animateLerp = () => {
                const currentTime = performance.now();
                const elapsed = currentTime - startTime;
                const normalisedPosition = Math.min(elapsed / duration, 1);
                const easedPosition = easeInOutQuad(normalisedPosition);

                // Interpolate between the start and end positions.
                // use .copy to avoid overwriting the original vectors
                const newPos = new THREE.Vector3().copy(startPos).lerp(endPos, easedPosition);
                this.camera.position.copy(newPos);

                // Update the OrbitControls target so they stay in sync
                this.controls.target.copy(newPos.clone().add(offset));
                this.controls.update();

                // Given this function is an await func the normal animation loop will not run
                // request frames here.
                if (normalisedPosition < 1) {
                    requestAnimationFrame(animateLerp);
                } else { // If the tween is complete, resolve the promise.
                    resolve();
                }
            };

            requestAnimationFrame(animateLerp);
        });
    }
}
