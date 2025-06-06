// Region page game mode and timer selection functionality

// Wait for the page to load
document.addEventListener('DOMContentLoaded', function() {
    // Get all the buttons and elements we need
    const moveButtons = document.querySelectorAll('.mode-selector');
    const playButton = document.getElementById('playBtn');
    const timeSlider = document.getElementById('timerRange');
    const timeDisplay = document.getElementById('timerValue');
    
    // Keep track of what the user selected
    const userChoices = {
        moveMode: 'move',
        timeInSeconds: 0
    };
    
    // Handle clicks on Move/No Move buttons
    moveButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const buttonGroup = this.dataset.group;
            const buttonMode = this.dataset.mode;
            
            // Only handle movement buttons
            if (buttonGroup === 'movement') {
                // Remove active class from all movement buttons
                moveButtons.forEach(function(btn) {
                    if (btn.dataset.group === 'movement') {
                        btn.classList.remove('active');
                    }
                });
                
                // Add active class to clicked button
                this.classList.add('active');
                
                // Save the user's choice
                userChoices.moveMode = buttonMode;
            }
        });
    });
    
    // Handle time slider changes and update display format
    if (timeSlider) {
        timeSlider.addEventListener('input', function() {
            const seconds = parseInt(this.value);
            userChoices.timeInSeconds = seconds;
            
            // Update the display text based on time value
            if (seconds === 0) {
                timeDisplay.textContent = 'No limit';
            } else if (seconds < 60) {
                timeDisplay.textContent = seconds + 's';
            } else {
                // Convert to minutes and seconds format
                const minutes = Math.floor(seconds / 60);
                const leftoverSeconds = seconds % 60;
                
                if (leftoverSeconds === 0) {
                    timeDisplay.textContent = minutes + 'm';
                } else {
                    timeDisplay.textContent = minutes + 'm ' + leftoverSeconds + 's';
                }
            }
        });
    }
    
    // Handle play button click and redirect to game with selected settings
    if (playButton) {
        playButton.addEventListener('click', function() {
            // Get the region from the page data
            const region = window.regionData.region;
            
            // Decide if it's timed or untimed based on timer setting
            let gameMode = 'untimed';
            if (userChoices.timeInSeconds > 0) {
                gameMode = 'timed';
            }
            
            // Build the URL with game parameters
            let url = '/play/' + gameMode + '/' + region + '?fresh=1';
            url = url + '&move=' + userChoices.moveMode;
            
            if (gameMode === 'timed' && userChoices.timeInSeconds > 0) {
                url = url + '&timer=' + userChoices.timeInSeconds;
            }
            
            // Go to the game
            window.location.href = url;
        });
    }
}); 