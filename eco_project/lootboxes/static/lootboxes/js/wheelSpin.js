/*
document.addEventListener("DOMContentLoaded", function () {
    const wheelCanvas = document.getElementById("wheelCanvas");
    const ctx = wheelCanvas.getContext("2d");
    const spinButton = document.querySelector(".spin-button");

    const prizes = ["Win Big", "Win Small", "Lose", "Win Bucks"];
    const colors = ["#FF5733", "#33FF57", "#5733FF", "#FFD700"];
    const numSegments = prizes.length;
    const anglePerSegment = (2 * Math.PI) / numSegments;
    let currentAngle = 0;
    let isSpinning = false;

    // Draw wheel function
    function drawWheel(angleOffset = 0) {
        ctx.clearRect(0, 0, wheelCanvas.width, wheelCanvas.height); // Clear canvas

        ctx.save();
        ctx.translate(150, 150); // Move origin to center
        ctx.rotate(angleOffset); // Rotate the whole wheel
        ctx.translate(-150, -150); // Move back

        for (let i = 0; i < numSegments; i++) {
            const startAngle = i * anglePerSegment;
            const endAngle = startAngle + anglePerSegment;

            // Draw segment
            ctx.beginPath();
            ctx.moveTo(150, 150);
            ctx.arc(150, 150, 150, startAngle, endAngle);
            ctx.fillStyle = colors[i];
            ctx.fill();
            ctx.closePath();

            // Add text in the center of the segment
            ctx.save();
            ctx.translate(150, 150);
            ctx.rotate(startAngle + anglePerSegment / 2);
            ctx.textAlign = "right";
            ctx.fillStyle = "white";
            ctx.font = "16px Arial";
            ctx.fillText(prizes[i], 120, 10); // Adjust position if needed
            ctx.restore();
        }

        ctx.restore();
    }

    // Spin wheel function
    function spinWheel() {
        if (isSpinning) return;
        isSpinning = true;

        let spinAngle = Math.random() * 360 + 1800; // Random (5+ full spins)
        let spinTime = 4000; // 4 seconds

        let start = null;
        function animateSpin(timestamp) {
            if (!start) start = timestamp;
            let progress = timestamp - start;

            if (progress < spinTime) {
                let easeOut = 1 - Math.pow(1 - progress / spinTime, 3);
                currentAngle = (easeOut * spinAngle * Math.PI) / 180;
                drawWheel(currentAngle);
                requestAnimationFrame(animateSpin);
            } else {
                isSpinning = false;
                currentAngle %= 2 * Math.PI;

                // Determine the winning prize
                let winningIndex = Math.floor((2 * Math.PI - currentAngle) / (2 * Math.PI / numSegments)) % numSegments;
                alert(`🎉 You won: ${prizes[winningIndex]}! 🎁`);
            }
        }

        requestAnimationFrame(animateSpin);
    }

    spinButton.addEventListener("click", spinWheel);

    // Initial drawing of the wheel
    drawWheel();
});
*/
document.addEventListener("DOMContentLoaded", function () {
    const wheelCanvas = document.getElementById("wheelCanvas");
    const ctx = wheelCanvas.getContext("2d");
    const spinButton = document.querySelector(".spin-button");
    let isSpinning = false;
    const prizes = ["100 Coins", "200 Coins", "500 Coins", "1 Free Spin", "Jackpot", "Nothing"];
    const colors = ["#FF5733", "#33FF57", "#5733FF", "#FFD700", "#FF33A8", "#33FFF2"];
    const wheelRadius = 150;  // Radius of the wheel
    let rotation = 0;

    function drawWheel() {
        const numSegments = prizes.length;
        const angle = (2 * Math.PI) / numSegments;
        ctx.clearRect(0, 0, wheelCanvas.width, wheelCanvas.height); // Clear the canvas before redrawing
        
        for (let i = 0; i < numSegments; i++) {
            // Draw each segment of the wheel
            ctx.beginPath();
            ctx.moveTo(wheelRadius, wheelRadius);
            ctx.arc(wheelRadius, wheelRadius, wheelRadius, i * angle, (i + 1) * angle);
            ctx.fillStyle = colors[i];
            ctx.fill();
            ctx.closePath();
            
            // Draw text in the middle of each segment
            ctx.fillStyle = "white";
            ctx.font = "14px Arial";
            const textAngle = i * angle + angle / 2;
            const x = wheelRadius + Math.cos(textAngle) * 100 - 30; // Adjust the text position
            const y = wheelRadius + Math.sin(textAngle) * 100 + 5;  // Adjust the text position
            ctx.fillText(prizes[i], x, y);
        }
    }

    drawWheel(); // Draw the wheel when the page is ready

    spinButton.addEventListener("click", function () {
        if (isSpinning) return;
        isSpinning = true;

        let randomDegrees = Math.floor(3600 + Math.random() * 360);
        let finalRotation = randomDegrees % 360;
        let segment = Math.floor(finalRotation / (360 / prizes.length));

        // Add smooth transition for spinning
        wheelCanvas.style.transition = "transform 4s ease-out";
        wheelCanvas.style.transform = `rotate(${randomDegrees}deg)`;

        setTimeout(() => {
            isSpinning = false;
            alert("You won: " + prizes[segment]);
        }, 4000);
    });
});