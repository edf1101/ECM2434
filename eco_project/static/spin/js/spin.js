document.addEventListener("DOMContentLoaded", function() {
    console.log("DEBUG: DOM fully loaded in spin.js");
  
    // Get the canvas element and its 2D context
    const canvas = document.getElementById("wheel");
    if (!canvas) {
      console.error("DEBUG: Canvas element not found!");
      return;
    }
    const ctx = canvas.getContext("2d");
    if (!ctx) {
      console.error("DEBUG: 2D context not obtained!");
      return;
    }
    console.log("DEBUG: Canvas and context obtained:", canvas, ctx);
  
    // Define six sectors for the wheel with a more gamified feel
    const sectors = [
      { color: "#f82", label: "nothing" },
      { color: "#e91e63", label: "nothing" },
      { color: "#9c27b0", label: "+100 bucks" },
      { color: "#3f51b5", label: "+100 points" },
      { color: "#03a9f4", label: "-50 bucks" },
      { color: "#4caf50", label: "lose all points :(" }
    ];
    const tot = sectors.length;
    const dia = canvas.width;  // 300
    const rad = dia / 2;       // 150
    const PI = Math.PI;
    const TAU = 2 * PI;
    const arc = TAU / tot;     // Each sector spans 60°
  
    // Function to draw the wheel with sectors, outlines, and labels
    function drawWheel(rotationAngle) {
      ctx.clearRect(0, 0, dia, dia);
      for (let i = 0; i < tot; i++) {
        const startAngle = i * arc + rotationAngle;
        ctx.save();
        ctx.beginPath();
        ctx.moveTo(rad, rad);
        ctx.arc(rad, rad, rad, startAngle, startAngle + arc);
        ctx.closePath();
        ctx.fillStyle = sectors[i].color;
        ctx.fill();
        // Draw white outline for clarity
        ctx.strokeStyle = "#fff";
        ctx.lineWidth = 2;
        ctx.stroke();
        // Draw label in the center of the sector
        ctx.translate(rad, rad);
        ctx.rotate(startAngle + arc / 2);
        ctx.textAlign = "right";
        ctx.fillStyle = "#fff";
        ctx.font = "bold 16px 'Press Start 2P', cursive";
        ctx.fillText(sectors[i].label, rad - 10, 10);
        ctx.restore();
      }
    }
  
    // Initial drawing of the wheel with no rotation
    let currentAngle = 0;
    drawWheel(currentAngle);
    console.log("DEBUG: Wheel drawn on canvas.");
  
    // Spin animation variables
    let isSpinning = false;
    let spinStartTime = null;
    const spinDuration = 4000; // 4-second spin duration
    let spinTotalAngle = 0;    // Total angle (radians) to spin
  
    // Animation function using requestAnimationFrame
    function animateSpin(timestamp) {
      if (!spinStartTime) spinStartTime = timestamp;
      const progress = timestamp - spinStartTime;
      let fraction = progress / spinDuration;
      if (fraction > 1) fraction = 1;
      // Ease-out cubic easing
      const easeOut = 1 - Math.pow(1 - fraction, 3);
      const angle = currentAngle + spinTotalAngle * easeOut;
      drawWheel(angle);
      if (progress < spinDuration) {
        requestAnimationFrame(animateSpin);
      } else {
        currentAngle = (currentAngle + spinTotalAngle) % TAU;
        // Adjust final angle so that 0 is at the top (for outcome calculation)
        let finalAngle = (currentAngle + PI / 2) % TAU;
        const sectorIndex = Math.floor(finalAngle / arc);
        const outcome = sectors[sectorIndex].label;
        document.getElementById("resultMessage").innerHTML =
          "<p>🎁 You landed on: <strong>" + outcome + "</strong>! 🎉</p>";
        isSpinning = false;
        spinStartTime = null;
      }
    }
  
    // Spin button event: Only allow spin if pet bucks are 50 or more
    const spinButton = document.getElementById("spinButton");
    spinButton.addEventListener("click", function() {
      const petBucks = parseInt(spinButton.getAttribute("data-pet-bucks"), 10);
      if (petBucks < 50) {
        alert("You need at least 50 Pet Bucks to spin the wheel!");
        return;
      }
      if (isSpinning) return;
      isSpinning = true;
      // Random spin: at least 2 full rotations plus a random extra angle (in radians)
      spinTotalAngle = (2 * TAU) + (Math.random() * TAU);
      document.getElementById("resultMessage").innerHTML = "";
      canvas.style.transition = "transform 4s ease-out";
      requestAnimationFrame(animateSpin);
    });
  
    console.log("DEBUG: Spin functionality initialized in spin.js.");
  });
  