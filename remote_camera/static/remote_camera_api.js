"use strict";

function RemoteCameraAPI() {

    const api_base_url = "/api/v1.0/";
    const requests = {
        image: api_base_url + "get_image",
        exposure: api_base_url + "exposure",
        start: api_base_url + "start_capture",
        stop: api_base_url + "stop_capture",
    };

    /**
     * This is  a helper method for getting json responses from the server.
     * @param {string} url 
     */
    async function getJSONResponse(url) {
        let response;
        let json_response;
        try {
            response = await request(url);
            json_response = await response.json();
        } catch (e) {
            console.log(e)
            return {
                "success": false,
                "message": "Client side exception while handling request: " + e
            };
        }

        return json_response;

    }

    async function setExposure(exposure) {
        let url = requests.exposure + "/" + exposure.toString();
        let json_response = await getJSONResponse(url);
        try {
            if (!json_response.success) {
                console.log(json_response.message);
                return -1;
            }
            return json_response.exposure;
        } catch (e) {
            console.log("Failed to parse set exposure request: " + e);
            return -1;
        }
    };

    async function getExposure() {
        let url = requests.exposure;
        let json_response = await getJSONResponse(url);
        try {
            if (!json_response.success) {
                console.log(json_response.message);
                return -1;
            }
            return json_response.exposure;
        } catch (e) {
            console.log("Failed to parse get exposure request: " + e);
            return -1;
        }
    };

    async function getImage(width = undefined, height = undefined) {
        let url = requests.get_image;
        if (width !== undefined && height != undefined) {
            url += width.toString() + "," + height.toString();
        }
        let json_response = await getJSONResponse(url);
        try {
            if (!json_response.success) {
                console.log(json_response.message);
                return -1;
            }
            return json_response.image;
        } catch (e) {
            console.log("Failed to parse set exposure request: " + e);
            return -1;
        }
    };

    async function startCapture() {
        let url = requests.start;
        let json_response = await getJSONResponse(url);
        try {
            if (!json_response.success) {
                console.log(json_response.message);
            }
        } catch (e) {
            console.log("Failed to parse start capture request: " + e);
        }
    };

    async function stopCapture() {
        let url = requests.stop;
        let json_response = await getJSONResponse(url);
        try {
            if (!json_response.success) {
                console.log(json_response.message);
            }
        } catch (e) {
            console.log("Failed to parse stop capture request: " + e);
        }
    };

    return {
        getExposure: getExposure,
        setExposure: setExposure,
        getImage: getImage,
        start: startCapture,
        stop: stopCapture,
    };
}