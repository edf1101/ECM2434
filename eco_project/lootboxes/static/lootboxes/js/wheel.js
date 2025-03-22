window.addEventListener('load', function () { // when loaded in
    // Get all the elements on the DOM that we will use
    const canvas = document.getElementById('wheel');
    const ctx = canvas.getContext('2d');
    const resultMessage = document.getElementById('result-message');
    const winMessage = document.getElementById('win-message');

    let isSpinning = false;
    const options = window.wheelOptions;
    const numOptions = options.length;
    const arcSize = (2 * Math.PI) / numOptions;
    let currentRotation = 0;
    let newPetBucks = null;


    /**
     * This function sizes the canvas according to the device screen size
     * (makes it responsive)
     */
    function resizeCanvas() {
        const container = document.getElementById('wheel-container');
        const rect = container.getBoundingClientRect();
        const dpr = window.devicePixelRatio || 1;
        canvas.width = rect.width * dpr;
        canvas.height = rect.width * dpr; // keep it square
        canvas.style.width = rect.width + 'px';
        canvas.style.height = rect.width + 'px';
        ctx.setTransform(1, 0, 0, 1, 0, 0);
        ctx.scale(dpr, dpr);
        drawWheel(currentRotation);
    }

    window.addEventListener('resize', resizeCanvas); // update canvas size for first time
    resizeCanvas();

    /**
     * This function is used to fit text size within the wheel so it displays properly
     *
     * @param text Text to display
     * @param baseFontSize Normal size for font
     * @param availableWidth The width of the sector in the wheel
     * @returns {*|number} The new size for the text
     */
    function getAdjustedFontSize(text, baseFontSize, availableWidth) {
        ctx.font = `bold ${baseFontSize}px sans-serif`;

        let textWidth = ctx.measureText(text).width;

        if (textWidth > availableWidth) { // if it is too big then scale it down
            let newSize = Math.max(baseFontSize * (availableWidth / textWidth), 10);
            return newSize;
        }
        return baseFontSize;
    }

    /**
     * Draw the wheel to the canvas
     *
     * @param rotation The rotation to initially draw (default 0)
     */
    function drawWheel(rotation = 0) {
        ctx.clearRect(0, 0, canvas.width, canvas.height); // reset it on start

        const size = canvas.clientWidth;
        const centerX = size / 2;
        const centerY = size / 2;
        const radius = centerX - 10;
        const baseFontSize = Math.floor(radius / 8);
        const availableWidth = radius * arcSize * 0.9;

        for (let i = 0; i < numOptions; i++) { // go through each option and draw its sector
            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            const startAngle = i * arcSize + rotation;
            const endAngle = startAngle + arcSize;
            ctx.arc(centerX, centerY, radius, startAngle, endAngle);

            // can adjust colours for sectors here and it will alternate between them
            const colours = ["#208048", "#30c46e", "#a9dfbf"];
            ctx.fillStyle = colours[i % colours.length];
            ctx.fill();
            ctx.stroke();

            // draw text inside the sector
            let adjustedFontSize = getAdjustedFontSize(options[i], baseFontSize, availableWidth);
            ctx.font = `bold ${adjustedFontSize}px sans-serif`;
            ctx.save();
            ctx.translate(centerX, centerY);
            ctx.rotate(startAngle + arcSize / 2);
            ctx.textAlign = "right";
            ctx.fillStyle = "#000";
            ctx.fillText(options[i], radius - 10, adjustedFontSize / 2);
            ctx.restore();
        }
    }

    /**
     * This function actually spins the wheel / gets the result from the backend
     */
    function spinWheel() {

        if (isSpinning) return; // start it spinning if it isnt already
        isSpinning = true;

        resultMessage.textContent = ''; // clear old result
        winMessage.textContent = '';
        winMessage.classList.remove('show');

        fetch(window.spinWheelUrl, { // call the API to get the result
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken
            }
        })
            .then(response => {
                if (!response.ok) { // display errors (ie cant afford it)
                    return response.json().then(err => {
                        resultMessage.textContent = err.error;
                        isSpinning = false;
                        throw new Error(err.error);
                    });
                }
                return response.json();
            })
            .then(data => {
                newPetBucks = data.pet_bucks;
                const targetOption = data.result;
                const targetIndex = options.indexOf(targetOption);
                if (targetIndex === -1) {
                    resultMessage.textContent = "Error: Unknown option received!";
                    isSpinning = false;
                    return;
                }

                // calculate what angle it should end up at
                const targetMidAngle = -Math.PI / 2;
                const optionStartAngle = targetIndex * arcSize;
                const optionMidAngle = optionStartAngle + arcSize / 2;
                const totalRotation = 5 * 2 * Math.PI + (targetMidAngle - optionMidAngle);

                // settings for length of animation
                const duration = 3000;
                const startTime = performance.now();

                /**
                 * This func gets called each frame to animate it moving
                 * @param time
                 */
                function animate(time) {
                    // calculate how far through it is from 0-1 in a eased / gamified way
                    const elapsed = time - startTime;
                    const progress = Math.min(elapsed / duration, 1);
                    const easedProgress = 1 - Math.pow(1 - progress, 3);

                    currentRotation = easedProgress * totalRotation;

                    drawWheel(currentRotation); // draw wheel with that rot

                    if (progress < 1) {
                        requestAnimationFrame(animate);
                    } else { // when finished display a win message for a bit
                        isSpinning = false;
                        winMessage.textContent = "You won " + targetOption + "!";
                        winMessage.classList.add('show');

                        // after 3s fade away the msg so it doesnt take up the whole screen
                        setTimeout(function () {
                            winMessage.classList.remove('show');
                            setTimeout(function () {
                                winMessage.textContent = "";
                            }, 500);
                            document.getElementById('petbucks').textContent = newPetBucks;
                        }, 3000);
                    }
                }

                requestAnimationFrame(animate); // start animating
            })
            .catch(error => {
                console.error("Error:", error);
                isSpinning = false;
            });
    }

    canvas.addEventListener('click', spinWheel);
});
