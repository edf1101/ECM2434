import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {DRACOLoader} from 'three/addons/loaders/DRACOLoader.js';

/**
 * Main application class that sets up a Three.js scene with dynamic map tiles,
 * heightmap integration, and geolocation-based camera movement.
 */
class ThreeJSApp {
    /**
     * Constructs a new ThreeJSApp instance, initializing properties, renderer,
     * scene, camera, controls, loaders, event listeners, and starts animation and
     * periodic location updates.
     */
    constructor() {
        this._initProperties();
        this._initRenderer();
        this._initScene();
        this._initCamera();
        this._initControls();
        this._initLoaders();

        // Set up window resize events and begin the render loop.
        this._setupEventListeners();
        this._animate();

        // Start periodic location updates.
        this._startLocationUpdates();

        // Immediately initialize location and map data from the API.
        this._initLocationAndMapData();
    }

    /**
     * Asynchronously initializes the location and map data.
     * 1. Requests the initial location from the API.
     * 2. Loads map data (including the heightmap).
     * 3. Updates the scene (camera position) based on the initial location.
     */
    async _initLocationAndMapData() {
        try {
            // Retrieve initial coordinates from the API.
            const [lat, lon] = await GeolocationHelper.requestCurrentLocation();
            this.lat = lat;
            this.lng = lon; // consistently use 'lng' for longitude
            console.log(`Initial API location: ${lat}, ${lon}`);

            // Fetch map details and load the heightmap image.
            await this._loadMapData();

            // Update the scene based on the new location.
            await this._changeLocation(this.lat, this.lng);
        } catch (error) {
            console.error("Error during initial location and map data initialization:", error);
        }
    }

    /**
     * Initializes internal properties and default values.
     */
    _initProperties() {
        // Default coordinates (to be updated by the API).
        this.lat = 0;
        this.lng = 0;

        // Map bounds (latitude/longitude) details.
        this.mapBounds = {maxLat: 0, minLat: 0, maxLon: 0, minLon: 0};

        // Grid definitions for the map (x/y/z coordinates).
        this.mapGrid = {maxX: 0, minX: 0, maxY: 0, minY: 0};

        // Dictionary for keeping track of loaded tiles.
        this.loadedTiles = {};

        // Canvas element to hold the heightmap image data.
        this.heightMapCanvas = null;
    }

    /**
     * Initializes the Three.js WebGL renderer.
     */
    _initRenderer() {
        this.renderer = new THREE.WebGLRenderer({antialias: true});
        this.renderer.outputColorSpace = THREE.SRGBColorSpace;
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setClearColor(0x5ac598);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        document.body.appendChild(this.renderer.domElement);
    }

    /**
     * Initializes the Three.js scene and configures fog.
     */
    _initScene() {
        this.scene = new THREE.Scene();

        // Override the default fog vertex shader chunk if necessary.
        THREE.ShaderChunk.fog_vertex = `
      #ifdef USE_FOG
        vFogDepth = length( mvPosition );
      #endif
    `;
        // Configure scene fog with the same color as the clear color.
        this.scene.fog = new THREE.Fog(0x5ac598, 150, 200);
    }

    /**
     * Initializes the perspective camera.
     */
    _initCamera() {
        this.camera = new THREE.PerspectiveCamera(
            45,
            window.innerWidth / window.innerHeight,
            1,
            300
        );
    }

    /**
     * Initializes the OrbitControls to allow user interaction with the camera.
     */
    _initControls() {
        this.controls = new OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.enablePan = false;
        this.controls.minDistance = 5;
        this.controls.maxDistance = 5;
        this.controls.minPolarAngle = 0.3;
        this.controls.maxPolarAngle = 1.5;
        this.controls.autoRotate = false;

        // Set an initial target for the camera (will be updated later).
        this.controls.target.set(-77, 184, 24);
        this.controls.update();
    }

    /**
     * Initializes the GLTF loader and attaches a DRACOLoader for compressed assets.
     */
    _initLoaders() {
        this.dracoLoader = new DRACOLoader();
        this.dracoLoader.setDecoderPath('https://www.gstatic.com/draco/versioned/decoders/1.4.3/');

        this.loader = new GLTFLoader();
        this.loader.setDRACOLoader(this.dracoLoader);
    }

    /**
     * Loads a GLTF asset from a given URL.
     *
     * @param {string} url - The URL of the GLTF asset.
     * @returns {Promise} Promise that resolves with the loaded GLTF object.
     */
    _loadGLTF(url) {
        return new Promise((resolve, reject) => {
            this.loader.load(
                url,
                (gltf) => resolve(gltf),
                undefined,
                (error) => reject(error)
            );
        });
    }

    /**
     * Loads a heightmap image from a URL and stores its data in an offscreen canvas.
     *
     * @param {string} url - The URL of the heightmap image.
     * @returns {Promise} Promise that resolves when the heightmap is fully loaded.
     */
    _loadHeightMap(url) {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.crossOrigin = "anonymous";
            img.src = url;
            img.onload = () => {
                const canvas = document.createElement('canvas');
                canvas.width = img.width;
                canvas.height = img.height;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0);
                this.heightMapCanvas = canvas;
                console.log("Heightmap loaded:", canvas.width, canvas.height);
                resolve(canvas);
            };
            img.onerror = (error) => {
                console.error("Error loading heightmap image:", error);
                reject(error);
            };
        });
    }

    /**
     * Fetches map data from the API, updates map bounds and grid values,
     * and loads the heightmap image.
     */
    async _loadMapData() {
        try {
            const response = await fetch(`/locations/api/map_data`);
            const data = await response.json();

            if (data.length === 0) {
                console.warn("No map data received.");
                return;
            }

            // Use the first entry of the returned data.
            const mapData = data[0];
            this.mapBounds = {
                maxLat: parseFloat(mapData.max_lat),
                minLat: parseFloat(mapData.min_lat),
                maxLon: parseFloat(mapData.max_lon),
                minLon: parseFloat(mapData.min_lon)
            };

            this.mapGrid = {
                maxX: mapData.max_x,
                minX: mapData.min_x,
                maxY: mapData.max_y,
                minY: mapData.min_y,
                minZ: mapData.min_z,
                maxZ: mapData.max_z
            };

            const heightmapUrl = mapData.camera_map_url;
            console.log("Heightmap URL:", heightmapUrl);
            // Wait until the heightmap image is fully loaded.
            await this._loadHeightMap(heightmapUrl);
        } catch (error) {
            console.error("Error fetching map data:", error);
        }
    }

    /**
     * Converts latitude and longitude coordinates to an [x, y] position
     * on the scene's map grid.
     *
     * @param {number} lat - Latitude.
     * @param {number} lon - Longitude.
     * @returns {[number, number]} An array containing the x and y coordinates.
     */
    _latLonToXY(lat, lon) {
        const {maxLat, minLat, maxLon, minLon} = this.mapBounds;
        const {maxX, minX, maxY, minY} = this.mapGrid;

        // Linearly interpolate the longitude to the x-axis.
        const x = ((lon - minLon) / (maxLon - minLon)) * (maxX - minX) + minX;
        // Linearly interpolate the latitude to the y-axis.
        const y = ((lat - minLat) / (maxLat - minLat)) * (maxY - minY) + minY;
        return [x, y];
    }

    /**
     * Retrieves the terrain height at a given latitude and longitude by reading
     * from the heightmap canvas.
     *
     * @param {number} lat - Latitude.
     * @param {number} lon - Longitude.
     * @returns {number|null} The calculated terrain height or null if the heightmap is not loaded.
     */
    _getHeightAtPos(lat, lon) {
        if (!this.heightMapCanvas) {
            console.warn("Heightmap not loaded yet.");
            return null;
        }

        // Convert geographic coordinates to grid positions.
        const [x, y] = this._latLonToXY(lat, lon);
        const {minX, maxX, minY, maxY, minZ, maxZ} = this.mapGrid;

        // Normalize the grid coordinates.
        const normalizedX = (x - minX) / (maxX - minX);
        // Invert Y to match the image coordinate system.
        const normalizedY = 1 - (y - minY) / (maxY - minY);
        const clampedX = Math.min(Math.max(normalizedX, 0), 1);
        const clampedY = Math.min(Math.max(normalizedY, 0), 1);

        // Convert normalized coordinates to pixel positions.
        const xPixel = Math.floor(clampedX * this.heightMapCanvas.width);
        const yPixel = Math.floor(clampedY * this.heightMapCanvas.height);

        // Read the pixel data from the canvas.
        const ctx = this.heightMapCanvas.getContext('2d', {willReadFrequently: true});
        const pixelData = ctx.getImageData(xPixel, yPixel, 1, 1).data;
        const pixelValue = pixelData[0]; // Assume grayscale data (red channel)
        const normalizedHeight = pixelValue / 255;

        // Map the normalized value to an actual terrain height.
        return normalizedHeight * (maxZ - minZ) + minZ;
    }

    /**
     * Retrieves an array of nearby tile file names from the API for a given location.
     *
     * @param {number} lat - Latitude.
     * @param {number} lon - Longitude.
     * @param {number} [radius=100] - Search radius (default is 100).
     * @returns {Promise<Array>} Promise resolving to an array of tile file names.
     */
    async getNearbyTiles(lat, lon, radius = 100) {
        if (!lat || !lon || isNaN(lat) || isNaN(lon)) {
            console.error("Latitude and longitude are required.");
            return [];
        }

        const response = await fetch(
            `/locations/api/nearby-tiles/?lat=${lat}&lon=${lon}&distance=250`
        );
        const data = await response.json();

        const nearbyTileNames = [];
        for (const tile of data) {
            nearbyTileNames.push(tile['file']);
        }
        return nearbyTileNames;
    }

    /**
     * Loads nearby 3D tiles based on the provided geographic location.
     *
     * @param {number} lat - Latitude.
     * @param {number} lon - Longitude.
     * @param {number} [radius=100] - Search radius (default is 100).
     */
    async _loadNearbyTiles(lat, lon, radius = 100) {
        // Retrieve the list of nearby tile names.
        const tileNames = await this.getNearbyTiles(lat, lon, 250);

        // Load each tile that hasn't already been loaded.
        for (const name of tileNames) {
            if (!this.loadedTiles[name]) {
                console.log("Loading tile:", name);
                try {
                    // Load the GLTF asset.
                    const gltf = await this._loadGLTF(name);
                    const mesh = gltf.scene;

                    // Ensure that all mesh children cast and receive shadows.
                    mesh.traverse((child) => {
                        if (child.isMesh) {
                            child.castShadow = true;
                            child.receiveShadow = true;
                        }
                    });

                    // Position the tile (adjustments can be made here if necessary).
                    mesh.position.set(0, 0, 0);
                    this.scene.add(mesh);
                    this.loadedTiles[name] = mesh;
                } catch (error) {
                    console.error("Error loading tile:", name, error);
                }
            }
        }
    }

    /**
     * Unloads 3D tiles that fall outside the valid nearby area for the specified location.
     *
     * @param {number} lat - Latitude.
     * @param {number} lon - Longitude.
     * @param {number} [radius=100] - Valid area radius (default is 100).
     */
    async _unloadTiles(lat, lon, radius = 100) {
        // Retrieve the list of valid nearby tile names.
        const validTileNames = await this.getNearbyTiles(lat, lon, radius);

        // Remove any tiles that are no longer nearby.
        for (const name in this.loadedTiles) {
            if (!validTileNames.includes(name)) {
                this.scene.remove(this.loadedTiles[name]);
                delete this.loadedTiles[name];
            }
        }
    }

    /**
     * Waits until all expected tiles for a given location are loaded or until a timeout is reached.
     *
     * @param {number} lat - Latitude.
     * @param {number} lon - Longitude.
     * @param {number} [radius=250] - Search radius.
     * @param {number} [timeout=5000] - Maximum time to wait in milliseconds.
     */
    async _waitForTiles(lat, lon, radius = 250, timeout = 5000) {
        const startTime = performance.now();
        const expectedTiles = await this.getNearbyTiles(lat, lon, radius);

        // Poll until all expected tiles are loaded or the timeout is reached.
        while (true) {
            const allLoaded = expectedTiles.every(name => name in this.loadedTiles);
            if (allLoaded) {
                console.log("All expected tiles loaded for lat:", lat, "lon:", lon);
                return;
            }
            if (performance.now() - startTime > timeout) {
                console.warn("Timeout waiting for tiles at lat:", lat, "lon:", lon);
                return;
            }
            // Wait 100ms before checking again.
            await new Promise(resolve => setTimeout(resolve, 100));
        }
    }

    /**
     * Sets up event listeners, such as window resize handling.
     */
    _setupEventListeners() {
        window.addEventListener('resize', () => this._onWindowResize());
    }

    /**
     * Adjusts camera and renderer settings on window resize.
     */
    _onWindowResize() {
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
    }

    /**
     * The main animation loop that updates controls and renders the scene.
     */
    _animate() {
        requestAnimationFrame(() => this._animate());
        this.controls.update();
        this.renderer.render(this.scene, this.camera);
    }

    /**
     * Starts periodic updates to check if the user's location has changed.
     */
    _startLocationUpdates() {
        // Check for location updates every 5000 milliseconds.
        setInterval(() => this._checkNeedUpdateLocation(), 5000);
    }

    /**
     * Checks whether the location has changed significantly (more than 50 meters)
     * and triggers an update if needed.
     */
    async _checkNeedUpdateLocation() {
        const [newLat, newLon] = await GeolocationHelper.requestCurrentLocation();
        const delta = GeolocationHelper.haversineDistance(this.lat, this.lng, newLat, newLon);

        const threshold = 50; // meters
        if (delta > threshold) {
            console.log("Location change detected (delta = " + delta + " m), updating...");
            await this._changeLocation(newLat, newLon);
        }
    }

    /**
     * Changes the current location by tweening the camera's position while preserving its rotation.
     * It loads nearby tiles along the path at ~100m intervals before tweening.
     *
     * @param {number} newLat - The new latitude.
     * @param {number} newLon - The new longitude.
     */
    async _changeLocation(newLat, newLon) {
        // Store the previous location.
        const oldLat = this.lat;
        const oldLon = this.lng;

        // Calculate the distance between the old and new locations.
        const totalDistance = GeolocationHelper.haversineDistance(oldLat, oldLon, newLat, newLon);
        console.log("Total distance to move: " + totalDistance + " m");

        // Determine the number of intermediate steps (approximately every 100 meters).
        const steps = Math.ceil(totalDistance / 100);
        console.log("Loading intermediate chunks in " + steps + " steps.");

        // Load tiles for each intermediate step.
        for (let i = 1; i < steps; i++) {
            const t = i / steps;
            const interpLat = oldLat + t * (newLat - oldLat);
            const interpLon = oldLon + t * (newLon - oldLon);
            console.log("Loading nearby tiles at intermediate point: lat=" + interpLat + ", lon=" + interpLon);
            await this._loadNearbyTiles(interpLat, interpLon);
            await this._waitForTiles(interpLat, interpLon);
        }

        // Load tiles for the final destination.
        await this._loadNearbyTiles(newLat, newLon);
        await this._waitForTiles(newLat, newLon);
        console.log("Loaded new tiles for location:", newLat, newLon);

        // Convert the new geographic coordinates to scene coordinates.
        const [x, y] = this._latLonToXY(newLat, newLon);
        const terrainHeight = this._getHeightAtPos(newLat, newLon);
        const height = terrainHeight !== null ? terrainHeight + 50 : 50;
        console.log("Setting camera position to:", x, height, -y);

        // Compute the current offset between the camera and its target.
        const offset = this.controls.target.clone().sub(this.camera.position);
        const newPos = new THREE.Vector3(x, height, -y);

        // Tween the camera to the new position while preserving the rotation offset.
        await this._tweenCameraPreserveRotation(this.camera.position.clone(), newPos, offset, 1000);

        // Update stored location.
        this.lat = newLat;
        this.lng = newLon;

        // Unload tiles that are no longer near the new location.
        await this._unloadTiles(newLat, newLon);
    }

    /**
     * Tweens the camera's position (and the OrbitControls target) from a start position
     * to an end position over a given duration while preserving the initial offset.
     * Uses an ease-in/out quadratic easing function.
     *
     * @param {THREE.Vector3} startPos - The starting camera position.
     * @param {THREE.Vector3} endPos - The target camera position.
     * @param {THREE.Vector3} offset - The offset from the camera to its target.
     * @param {number} duration - The duration of the tween in milliseconds.
     * @returns {Promise} A promise that resolves when the tween is complete.
     */
    _tweenCameraPreserveRotation(startPos, endPos, offset, duration) {
        // Easing function: quadratic ease-in/out.
        function easeInOutQuad(t) {
            return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
        }

        return new Promise((resolve) => {
            const startTime = performance.now();

            const animateTween = () => {
                const currentTime = performance.now();
                const elapsed = currentTime - startTime;
                const t = Math.min(elapsed / duration, 1);
                const easedT = easeInOutQuad(t);

                // Interpolate between the start and end positions.
                const newPos = new THREE.Vector3().copy(startPos).lerp(endPos, easedT);
                this.camera.position.copy(newPos);

                // Update the OrbitControls target while preserving the offset.
                this.controls.target.copy(newPos.clone().add(offset));
                this.controls.update();

                if (t < 1) {
                    requestAnimationFrame(animateTween);
                } else {
                    resolve();
                }
            };

            requestAnimationFrame(animateTween);
        });
    }
}

/**
 * Helper class for geolocation-related tasks.
 */
class GeolocationHelper {
    /**
     * Initiates a geolocation request to log the user's current position.
     */
    static getLocation() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(GeolocationHelper.showPosition);
        } else {
            console.log("Geolocation is not supported by this browser.");
        }
    }

    /**
     * Callback to display the current position.
     *
     * @param {GeolocationPosition} position - The geolocation position object.
     */
    static showPosition(position) {
        console.log(`Latitude: ${position.coords.latitude}, Longitude: ${position.coords.longitude}`);
    }

    /**
     * Requests the current location from the API.
     *
     * @returns {Promise<[number, number]>} A promise that resolves with [latitude, longitude].
     */
    static async requestCurrentLocation() {
        try {
            const response = await fetch(`/locations/api/get_location`);
            const data = await response.json();
            if (data.lat && data.lon) {
                return [data.lat, data.lon];
            } else {
                console.error("Error fetching location data");
                return [0, 0];
            }
        } catch (error) {
            console.error("Error fetching location data:", error);
            return [0, 0];
        }
    }

    /**
     * Calculates the great-circle distance between two points on Earth using the Haversine formula.
     *
     * @param {number} lat1 - Latitude of the first point (in degrees).
     * @param {number} lon1 - Longitude of the first point (in degrees).
     * @param {number} lat2 - Latitude of the second point (in degrees).
     * @param {number} lon2 - Longitude of the second point (in degrees).
     * @returns {number} The distance between the two points in meters.
     */
    static haversineDistance(lat1, lon1, lat2, lon2) {
        function toRadians(degrees) {
            return degrees * Math.PI / 180;
        }

        // Earth's radius in kilometers.
        const earthRadiusKm = 6371;

        // Calculate the differences between the coordinates.
        const deltaLat = toRadians(lat2 - lat1);
        const deltaLon = toRadians(lon2 - lon1);

        // Convert the starting and ending latitudes to radians.
        const radLat1 = toRadians(lat1);
        const radLat2 = toRadians(lat2);

        // Apply the Haversine formula.
        const a = Math.sin(deltaLat / 2) ** 2 +
            Math.cos(radLat1) * Math.cos(radLat2) *
            Math.sin(deltaLon / 2) ** 2;
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

        // Calculate the distance in meters.
        return earthRadiusKm * c * 1000;
    }
}

// Start the Three.js application.
new ThreeJSApp();
