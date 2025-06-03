const {
    lat: initLat,
    lon: initLon,
    mode,
    remaining,
    guessed,
    guessLat,
    guessLon,
    region,
    pts: roundPts,
    timeout
} = window.gameData;

const regionView = {
    nyc:    { center:[40.7128, -74.0060], zoom: 11 },
    europe: { center:[54.5, 15.0], zoom: 4 },
    us:     { center: [39.5, -98.35 ], zoom: 4 },
    asia:   { center: [34.0, 100.62], zoom: 3},
    oceania:{ center: [22.7, 140.0], zoom: 3},
    global: { center: [20, 0], zoom: 2 }
};

const { center, zoom } = regionView[region] || regionView.global;
var map = L.map('mini').setView(center, zoom);

const guessBtn = document.getElementById('guessBtn');
var lat = 0
var lon = 0

const textBox = document.getElementById('input');
textBox.value = 0 + ", " + 0;

// Add OpenStreetMap layer
L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
//attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

const container = document.getElementById('mini-container');
container.addEventListener('transitionend', () => {   //hover stuff (hopefully it owrks??)
    map.invalidateSize();
});

const miniContainer = document.getElementById('mini-container');
let shrinkTimeout;

miniContainer.addEventListener('mouseenter', () => {
    clearTimeout(shrinkTimeout); // Cancel any pending shrink
    miniContainer.classList.add('enlarged');
});

miniContainer.addEventListener('mouseleave', () => {
    shrinkTimeout = setTimeout(() => {
        miniContainer.classList.remove('enlarged');
    }, 500); // Delay shrinking by 500ms
});

map.on('click', function(e) {
    L.popup({closeButton: false})
        .setLatLng(e.latlng)
        .setContent('Your guess')
        .openOn(map);

    lat = e.latlng.lat.toFixed(4);
    lon = e.latlng.lng.toFixed(4);
    console.log("these are the coords:" + lat + lon)

    textBox.value = lat + ", " + lon;
    guessBtn.hidden = false;
});

guessBtn.onclick=()=>document.getElementById('guessForm').submit();

if (mode === 'timed' && !guessed && remaining > 0) {
    (function(){
        let t = remaining;
        const box = document.getElementById('timer');
        const tick = setInterval(()=>{
        t -= 1;
        if (t <= 0){
            clearInterval(tick);
            // Submit a timeout form 
            const form = document.getElementById('guessForm');
            const timeoutInput = document.createElement('input');
            timeoutInput.type = 'hidden';
            timeoutInput.name = 'timeout';
            timeoutInput.value = 'true';
            form.appendChild(timeoutInput);
            form.submit();
            return;
        } else {
            box.textContent = t;
        }
        }, 1000);
    })();
}

if (guessed){
    const res = L.map('resultMap',{zoomControl:false,attributionControl:false});
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(res);

    //get players guess g and actual answer a
    const a = [initLat, initLon];

    // Only show guess marker and line if not a timeout
    if (!timeout && guessLat !== 0 && guessLon !== 0) {
        const g = [guessLat, guessLon];
        L.circleMarker(g,{radius:6}).addTo(res);  //blue marker for players guess
        L.polyline([g,a],{dashArray:'6 6'}).addTo(res); //dashed line
        res.fitBounds([g,a],{padding:[40,40]}); //fit map bounds
    } else {
        res.setView(a, 10);
    }
    
    L.circleMarker(a,{radius:6,color:'red',fillColor:'red'}).addTo(res); //red marker for actual location

    // credit to Doctor Stanley H[Wh]oo blackjack.js animateBalanceChange
    const ptsSpan = document.getElementById('pts');
    const ptsTarget = roundPts;
    let current = 0;
    const inc = Math.max(1, Math.round(ptsTarget / 50));

    const tick = setInterval(() => {
        current += inc;
        if (current >= ptsTarget) {
            current = ptsTarget;
            clearInterval(tick);
        }
        ptsSpan.textContent = current;
    }, 20);

    const nextBtn=document.getElementById('nextBtn');
    nextBtn.hidden=false;
    nextBtn.onclick=()=>{
        if (window.history && window.history.replaceState) {
            window.history.replaceState({gameState: true}, null, window.location.href);
        }
        
        document.querySelector('input[name="next"]').disabled=false;
        document.getElementById('guessForm').submit();
    };
}

// Adapted from: MODEL: ChatGPT 4o TIME: 2025-05-24 6:45PM and from: MODEL : ChatGPT 4o TIME: 2025-06-02 10:35PM
// Purpose: redirect user to home if browser navigation is back/forward
// Prompt: how do i tell when a page is reshown by a back/forward button and automatically send the user to the home page when this button is pressed?”
// Handle navigation control - prevent going back through rounds
(function setupNavigationControl() {
    let hasLeftGame = false;
    
    // Detect if this page was reached via back/forward navigation
    if (performance.getEntriesByType("navigation")[0].type === "back_forward") {
        // Clear game state on server and redirect to region page
        fetch('/leave', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: 'region=' + encodeURIComponent(region)
        }).then(() => {
            location.replace("/region/" + region);
        }).catch(() => {
            location.replace("/region/" + region);
        });
        return;
    }
    
    // Handle back button - always go to region page and clear game state
    window.addEventListener('popstate', function(event) {
        if (!hasLeftGame) {
            hasLeftGame = true;
            
            // Clear game state on server
            fetch('/leave', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: 'region=' + encodeURIComponent(region)
            }).then(() => {
                location.replace("/region/" + region);
            }).catch(() => {
                location.replace("/region/" + region);
            });
        }
    });
    
    // Push a state entry to capture back button presses
    if (window.history && window.history.pushState) {
        window.history.pushState({gameState: true}, null, window.location.href);
    }
})();

(function enableMiniMapDraggingAndResizing() {
    // Setup ResizeObserver to handle map resizing when container changes size
    const resizeObserver = new ResizeObserver(() => {
      map.invalidateSize(); // Let Leaflet know the size changed
    });
    resizeObserver.observe(document.getElementById('mini-container'));

    // Dragging support
    const container = document.getElementById('mini-container');
    let isDragging = false;
    let offsetX = 0;
    let offsetY = 0;

    container.addEventListener("mousedown", function (e) {
      // Prevent dragging if user clicks on the guess button
      if (e.target !== container) return;

      isDragging = true;
      offsetX = e.clientX - container.offsetLeft;
      offsetY = e.clientY - container.offsetTop;
      container.style.cursor = "grabbing";
    });

    document.addEventListener("mouseup", function () {
      isDragging = false;
      container.style.cursor = "move";
    });

    document.addEventListener("mousemove", function (e) {
      if (!isDragging) return;

      container.style.left = `${e.clientX - offsetX}px`;
      container.style.top = `${e.clientY - offsetY}px`;
      container.style.bottom = "auto"; // Reset auto positioning
      container.style.right = "auto";
    });
  })();
