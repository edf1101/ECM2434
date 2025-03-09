import { DRACOLoader } from '../../three/jsm/loaders/DRACOLoader.js';
import { GLTFLoader } from '../../three/jsm/loaders/GLTFLoader.js';


export class GltfLoader {

    constructor() {
        // create the loader objects
        this.dracoLoader = new DRACOLoader();
        this.dracoLoader.setDecoderPath('https://www.gstatic.com/draco/versioned/decoders/1.4.3/');

        this.loader = new GLTFLoader();
        this.loader.setDRACOLoader(this.dracoLoader);

        // For caching loaded glTF models.
        this.gltfCache = {};
    }

    /**
     * Loads a GLTF asset from a given URL.
     * Implements caching so that the model is only loaded once and then cloned.
     *
     * @param {string} url - The URL of the GLTF asset.
     * @return {Promise} Promise that resolves with the loaded GLTF object.
     */
    loadGLTF(url) {
        return new Promise((resolve, reject) => {
            // Check the cache first.
            if (this.gltfCache[url]) {
                // Return a clone of the cached scene.
                let cachedScene = this.gltfCache[url];
                let gltf = { scene: cachedScene.clone(true) };
                resolve(gltf);
                return;
            }
            this.loader.load(
                url,
                (gltf) => {
                    // Store the loaded scene in the cache.
                    this.gltfCache[url] = gltf.scene;
                    resolve(gltf);
                },
                undefined,
                (error) => reject(error)
            );
        });
    }
}