document.addEventListener('DOMContentLoaded', function () {
    
    // Function to setup adjustable input for both number and date
    function setupAdjustableInput(elementId, min, max) {
        const inputEl = document.querySelector('#' + elementId);
        const minusBtn = inputEl.parentElement.querySelector('.btn-minus');
        const plusBtn = inputEl.parentElement.querySelector('.btn-plus');
        let adjustingInterval = null;
        let initialPressTimer = null;
        let isAdjusting = false;
        
        function adjustValue(delta) {
            let currentValue = parseInt(inputEl.value);
            let newValue = currentValue + delta;
            if (newValue >= min && newValue <= max) {
                inputEl.value = newValue;
            }
        }

        function startInitialPress(delta) {
            adjustValue(delta);
            initialPressTimer = setTimeout(() => startContinuousAdjust(delta), 500);
        }

        function startContinuousAdjust(delta) {
            if (adjustingInterval) clearInterval(adjustingInterval);
            adjustingInterval = setInterval(() => adjustValue(delta), 80);
        }

        function stopAdjusting() {
            if (initialPressTimer) clearTimeout(initialPressTimer);
            if (adjustingInterval) clearInterval(adjustingInterval);
            isAdjusting = false;
        }

        minusBtn.addEventListener('mousedown', function() {
            if (!isAdjusting) {
                isAdjusting = true;
                startInitialPress(-1);
            }
        });
        minusBtn.addEventListener('touchstart', function(event) {
            event.preventDefault(); // Prevents emulated mouse events
            if (!isAdjusting) {
                isAdjusting = true;
                startInitialPress(-1);
            }
        });
        
        plusBtn.addEventListener('mousedown', function() {
            if (!isAdjusting) {
                isAdjusting = true;
                startInitialPress(1);
            }
        });
        plusBtn.addEventListener('touchstart', function(event) {
            event.preventDefault(); // Prevents emulated mouse events
            if (!isAdjusting) {
                isAdjusting = true;
                startInitialPress(1);
            }
        });
        
        document.addEventListener('mouseup', function() {
            if (isAdjusting) stopAdjusting();
        });
        document.addEventListener('touchend', function(event) {
            if (isAdjusting) stopAdjusting();
        });        
    }

    setupAdjustableInput('rating', 0, 30);

    document.getElementById('rating').addEventListener('input', function() {
        let value = parseInt(this.value);
        if (isNaN(value)) value = 0;
        if (value < 0) value = 0;
        if (value > 30) value = 30;
        this.value = value;
        document.getElementById('rating-display').textContent = value;
    });

    // auto-resize textarea
    const tx = document.getElementsByTagName("textarea");
    for (let i = 0; i < tx.length; i++) {
        tx[i].addEventListener("input", resizeTextarea, false);
    }
    
    function resizeTextarea() {
        this.style.height = 0;
        this.style.height = (this.scrollHeight - 18) + "px";
    }

    document.querySelector('form').addEventListener('submit', function(event) {
        var textArea = document.getElementById('text');
        if (!textArea.value.trim()) {
            textArea.classList.add('fade-to-black');
            setTimeout(() => textArea.classList.remove('fade-to-black'), 2000);
            textArea.value = '';
            event.preventDefault(); // Prevent form submission
        } else {
            textArea.classList.remove('fade-to-black');
        }
    });    
    
});
