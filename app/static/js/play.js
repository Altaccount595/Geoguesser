// Main game functionality for play page with map interaction and game logic

// Extract game data from the server
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

// Map view configurations for different regions
const regionView = {
    nyc:    { center:[40.7128, -74.0060], zoom: 11 },
    europe: { center:[54.5, 15.0], zoom: 4 },
    us:     { center: [39.5, -98.35 ], zoom: 4 },
    asia:   { center: [34.0, 100.62], zoom: 3},
    oceania:{ center: [-25.27, 130.78], zoom: 3},
    world:  { center: [20, 0], zoom: 2 }
};

// Initialize map with region-specific view
const { center, zoom } = regionView[region] || regionView.world;
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

// Handle map container resize for smooth transitions
const container = document.getElementById('mini-container');
container.addEventListener('transitionend', () => {   //hover stuff (hopefully it owrks??)
    map.invalidateSize();
});

// Mini map hover interaction to enlarge and shrink
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

// Handle map clicks to place guess marker and capture coordinates
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

// Customize map attribution
map.attributionControl.setPrefix('');
map.attributionControl.addAttribution('© DevoGuessr');

// Submit guess when button is clicked
guessBtn.onclick=()=>document.getElementById('guessForm').submit();

// Timer functionality for timed game mode
if (mode === 'timed' && !guessed && remaining > 0) {
    (function(){
        let t = remaining;
        const box = document.getElementById('timer');
        const tick = setInterval(()=>{
        t -= 1;
        if (t <= 0){
            clearInterval(tick);
            // Submit a timeout form when time runs out
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

// Results display after a guess is submitted
if (guessed){
    // Create results map to show actual location and guess
    const res = L.map('resultMap',{zoomControl:false,attributionControl:false});
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(res);

    // Get players guess and actual answer coordinates
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

    // Animate points counter from 0 to earned points
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

    // Show next round button and handle progression
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
// Prompt: "how do i tell when a page is reshown by a back/forward button and automatically send the user to the home page when this button is pressed?”
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

// Enable dragging of the mini map container
 (function enableMiniMapDraggingAndResizing() {
  const container = document.getElementById('mini-container');
  const mapElement = document.getElementById('mini');

function debounce(fn, delay) {
  let timeout;
  return (...args) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => fn(...args), delay);
  };
}
const resizeObserver = new ResizeObserver(
  debounce(() => map.invalidateSize(), 100)
);

  // DRAG SUPPORT
  let isDragging = false;
  let offsetX = 0;
  let offsetY = 0;

  // Start dragging only when user clicks on container but *not* the map
  container.addEventListener("mousedown", function (e) {
    // If the user clicked inside the map, don't start dragging
    const mapRect = mapElement.getBoundingClientRect();
    if (
      e.clientX >= mapRect.left &&
      e.clientX <= mapRect.right &&
      e.clientY >= mapRect.top &&
      e.clientY <= mapRect.bottom
    ) {
      return;
    }

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
    container.style.bottom = "auto";
    container.style.right = "auto";
  });
})();

// Enable custom resizing of the mini map container using corner handles
(function enableCustomResize() {
  const container = document.getElementById('mini-container');
  const handles = container.querySelectorAll('.resize-handle');

  handles.forEach(handle => {
    handle.addEventListener('mousedown', function (e) {
      e.preventDefault();
      e.stopPropagation(); // prevent drag

      const startX = e.clientX;
      const startY = e.clientY;
      const startWidth = parseFloat(getComputedStyle(container).width);
      const startHeight = parseFloat(getComputedStyle(container).height);
      const startLeft = container.offsetLeft;
      const startTop = container.offsetTop;

      const isTop = handle.classList.contains('top-left') || handle.classList.contains('top-right');
      const isLeft = handle.classList.contains('top-left') || handle.classList.contains('bottom-left');

      function doDrag(e) {
        const dx = e.clientX - startX;
        const dy = e.clientY - startY;

        if (isLeft) {
          container.style.width = `${startWidth - dx}px`;
          container.style.left = `${startLeft + dx}px`;
        } else {
          container.style.width = `${startWidth + dx}px`;
        }

        if (isTop) {
          container.style.height = `${startHeight - dy}px`;
          container.style.top = `${startTop + dy}px`;
        } else {
          container.style.height = `${startHeight + dy}px`;
        }

        map.invalidateSize();
      }

      function stopDrag() {
        document.removeEventListener('mousemove', doDrag);
        document.removeEventListener('mouseup', stopDrag);
      }

      document.addEventListener('mousemove', doDrag);
      document.addEventListener('mouseup', stopDrag);
    });
  });
})();
