/**
 * Helper class for geolocation-related tasks.
 */
export class GeoHelper {
    /**
     * Initiates a geolocation request to log the user's current position.
     */
    static getLocation() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(GeoHelper.showPosition);
        } else {
            console.error("Geolocation is not supported by this browser.");
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