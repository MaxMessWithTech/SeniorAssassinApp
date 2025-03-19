const notOffCanvas = new bootstrap.Offcanvas('#notificationOC');
const purgeModel = new bootstrap.Modal("#purgeModel");
const purgeCountdownDiv = document.getElementById("purge-countdown");
const purgeCountdownEndDiv = document.getElementById("purge-end-countdown");

const not_btn = document.getElementById('notification_btn_id');

      
document.getElementById('model-dismiss').addEventListener("click", () => {
    purgeModel.hide()
});
      
document.getElementById('notification-dismiss').addEventListener("click", (e) => {
    e.preventDefault();
    notOffCanvas.hide();
});

not_btn.addEventListener("click", (e) => {
    e.preventDefault();
    notOffCanvas.show();
});

function getDistance(a) {
    const now = new Date().getTime();
    
    // Find the distance between now and the countdown date
    return a - now;
}

function startCountdown() {
  // Update the countdown every 1 second
  const x = setInterval(() => {
    // Find the distance between now and the countdown date
    const distance = getDistance(countDownDate);
    console.log(distance);
    
    if (distance < 0) {
      purgeCountdownDiv.style.display = "none";
      clearInterval(x);
      return;
    }
    purgeCountdownDiv.style.display = "flex";
    
    // Time calculations for days, hours, minutes and seconds
    const days = Math.floor(distance / (1000 * 60 * 60 * 24));
    const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((distance % (1000 * 60)) / 1000);
  
    // Display the result
    document.getElementById("hours").innerHTML = hours.toString().padStart(2, '0');
    document.getElementById("minutes").innerHTML = minutes.toString().padStart(2, '0');
    document.getElementById("seconds").innerHTML = seconds.toString().padStart(2, '0');
  }, 1000);
}


function startEndCountdown() {
    // Update the countdown every 1 second
    const x2 = setInterval(() => {
        // Find the distance between now and the countdown date
        const distance = getDistance(countDownEndDate);
        console.log(distance);
        
        if (distance < 0) {
        purgeCountdownEndDiv.style.display = "none";
        clearInterval(x2);
        return;
        }
        purgeCountdownEndDiv.style.display = "flex";
        
        // Time calculations for days, hours, minutes and seconds
        const days = Math.floor(distance / (1000 * 60 * 60 * 24));
        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);
    
        // Display the result
        document.getElementById("hours2").innerHTML = hours.toString().padStart(2, '0');
        document.getElementById("minutes2").innerHTML = minutes.toString().padStart(2, '0');
        document.getElementById("seconds2").innerHTML = seconds.toString().padStart(2, '0');
    }, 1000);
}

if (rule_suspension) {
    purgeModel.show();
}