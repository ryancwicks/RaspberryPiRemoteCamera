"use strict";

function RemoteCameraControls(control_elements, api_instance) {

    let api = api_instance;

    const required_control_elements = [
        "image_control_div",
        "preview_div",
        "capture_control_div",
    ];

    let preview_canvas;
    let current_preview_image = new Image();
    let image_update_timer;
    let image_controls;
    let capture_controls;

    (async function initialize() {
        let valid_setup = true;
        let required_keys = Object.keys(control_elements);
        required_control_elements.forEach((key) => {
            if (!required_keys.includes(key)) {
                console.log("Missing control element " + key + " in remote camera controls setup.");
                valid_setup = false;
            }
        });

        if (!valid_setup) {
            console.log("Failed to load required controls.")
            return;
        }


        preview_canvas = setupDisplayCanvas(control_elements.preview_div);
        current_preview_image.addEventListener("load", () => {
            preview_canvas.drawImage(current_preview_image);
        });
        await startImageUpdate();

        image_controls = setupImageControls(control_elements.image_control_div);
        capture_controls = setupCaptureControls(control_elements.capture_control_div);

    })()

    async function updateImage() {
        let image_size = preview_canvas.getCanvasSize();
        current_preview_image.src = await api.getImage(image_size.width, image_size.height);
    }

    async function startImageUpdate() {
        await updateImage()
        image_update_timer = setTimeout(startImageUpdate, 500);
    }

    function stopImageUpdate() {
        clearInterval(image_update_timer);
    }

    async function setupImageControls(controls_div_element) {
        const min_exposure = 0;
        const max_exposure = 50;

        let exposure_slider = document.createElement("INPUT");
        exposure_slider.type = "range";
        exposure_slider.min = min_exposure;
        exposure_slider.max = max_exposure;
        exposure_slider.step = 1;
        exposure_slider.addEventListener("change", sliderChanged);

        let exposure_input = document.createElement("INPUT");
        exposure_input.type = "number";
        exposure_input.min = exposure_slider.min;
        exposure_input.max = exposure_slider.max;
        exposure_input.step = exposure_slider.step;
        exposure_input.addEventListener("change", inputChanged);

        {
            let exposure = await api.getExposure();
            updateExposure(exposure);
        }

        function sliderChanged() {
            exposure_input.value = exposure_slider.value;
            changeExposure(exposure_slider.value);
        };

        function inputChanged() {
            exposure_slider.value = exposure_input.value;
            changeExposure(exposure_input.value);
        };

        async function changeExposure(exposure) {

            let new_exposure = await api.setExposure(exposure);
            updateExposure(new_exposure);
        };

        function updateExposure(exposure) {
            if (exposure > min_exposure && exposure < max_exposure) {
                exposure_slider.value = exposure;
                exposure_input.value = exposure;
            }
        };

        { //scoped document setup.
            let controls_div = document.getElementById(controls_div_element);
            let table = document.createElement("TABLE");
            let row = document.createElement("TR");
            let data = document.createElement("TD");
            data.innerHTML = "Exposure (ms)";
            row.appendChild(data);
            data = document.createElement("TD")
            data.appendChild(exposure_slider)
            row.appendChild(data);
            data = document.createElement("TD")
            data.appendChild(exposure_input)
            row.appendChild(data);
            table.appendChild(row);
            controls_div.appendChild(table);
        };

        return {

        };
    }

    function setupCaptureControls(controls_div_element) {
        const file_extension = ".jpg";
        let capture_button = document.createElement("INPUT");
        capture_button.type = "button";
        capture_button.addEventListener("click", capture);
        let filename_box = document.createElement("INPUT");
        filename_box.type = "text";

        function capture() {
            stopImageUpdate();
            let image = api.getImage();
            let filename = filename_box.value + file_extension;
            downloadImage(filename, image);
            updateFilename();
            startImageUpdate();
        };

        function downloadImage(filename, image_source) {
            let element = document.createElement("A");
            element.setAttribute('href', image_source);//'data:image/jpeg;base64,' + image_source);
            element.setAttribute('download', filename);
            element.style.display = "none";
            document.body.appendChild(element);

            element.click();

            document.body.removeChild(element);
        };

        function updateFilename() {
            let filename = filename_box.value;

            /**
             * if the filename doesn't have the extension _### at the end, add it.
             * Otherwise, convert the #### to a number, add one to it, and continue
             */
            let index_under = filename.lastIndexOf("_");
            if (index_under === -1) { //no match for _
                filename += "_0001";
            } else {
                if (index_under === filename.length - 1) { //underscore at end of filename
                    filename += "0001";
                } else {
                    let last_bit = Number(filename.substring(index_under + 1));
                    if (last_bit.isNaN()) { //text past underscore is not a number
                        filename += "_0001";
                    } else { //we have a number past the underscore, increment it and replace.
                        last_bit += 1
                        filename = filename.substring(0, index_under + 1) + last_bit.toString().padStart(4, "0");
                    }
                }
            }

            filename_box.value = filename;
        };

        { //scoped document setup
            let controls_div = document.getElementById(controls_div_element);
            let table = document.createElement("TABLE");
            let row = document.createElement("TR");
            let data = document.createElement("TD");
            data.innerHTML = "Filename";
            row.appendChild(data);
            data = document.createElement("TD")
            data.appendChild(filename_box)
            row.appendChild(data);
            data = document.createElement("TD")
            data.appendChild(capture_button)
            row.appendChild(data);
            table.appendChild(row);
            controls_div.appendChild(table);
        };

        return {

        };
    };

    return {

    };
}


/*******************
* Canvas Controls
******************/
/**
 * Setup the canvas and return a set of controls.
 * @param {string id of div to contain canvas to setup} canvas_div_id 
 */
function setupDisplayCanvas(canvas_div_id) {
    let canvas = document.createElement("CANVAS");
    let container = document.getElementById(canvas_div_id)
    container.appendChild(canvas);
    let ctx = canvas.getContext("2d");

    resize();
    canvas.addEventListener("resize", resize);

    function resize() {
        //let aspect = canvas.height/canvas.width;
        let width = container.offsetWidth;
        let height = container.offsetHeight;

        canvas.width = width;
        canvas.height = height;
    };

    function clear() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    };

    function drawImage(img) {
        ctx.drawImage(img, 0, 0, container.offsetWidth, container.offsetHeight);
    }


    return {
        clear: clear,
        resize: resize,
        drawImage: drawImage,
        getCanvasSize: () => {
            return {
                width: canvas.width,
                height: canvas.height,
            }
        },
    };
};
/******************************
 * END CANVAS CONTROLS
 ******************************/