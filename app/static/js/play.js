const {
    lat: initLat,
    lon: initLon,
    mode,
    remaining,
    guessed,
    guessLat,
    guessLon,
    region,
    pts: roundPts
} = window.gameData;


var map = L.map('mini').setView([40, -95], 4);

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

if (mode === 'timed' && !guessed) {
    (function(){
        let t = remaining;
        const box = document.getElementById('timer');
        const tick = setInterval(()=>{
        t -= 1;
        if (t <= 0){
            clearInterval(tick);
            location.reload();
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
    const g = [guessLat, guessLon];
    const a = [initLat, initLon];

    L.circleMarker(g,{radius:6}).addTo(res);  //blue marker for players guess
    L.circleMarker(a,{radius:6,color:'red',fillColor:'red'}).addTo(res); //red marker for actual location
    L.polyline([g,a],{dashArray:'6 6'}).addTo(res); //dashed line
    res.fitBounds([g,a],{padding:[40,40]}); //fit map bounds

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
        document.querySelector('input[name="next"]').disabled=false;
        document.getElementById('guessForm').submit();
    };
}

// Adapted from: MODEL: ChatGPT 4o TIME: 2025-05-24 6:45PM
// Purpose: redirect user to home if browser navigation is back/forward
// Prompt: how do i tell when a page is reshown by a back/forward button and automatically send the user to the home page when this button is pressed?”
if (performance.getEntriesByType("navigation")[0].type === "back_forward") {
    location.replace("/region/" + region);
  }
