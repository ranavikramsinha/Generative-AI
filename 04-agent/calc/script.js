const keys = document.querySelector('.calculator-keys');
const display = document.querySelector('.calculator-screen');

let currentValue = '';
let resetScreen = false;

function updateDisplay() {
    display.value = currentValue;
}

keys.addEventListener('click', event => {
    if (!event.target.matches('button')) return;

    const key = event.target;
    const keyValue = key.value;

    if (key.classList.contains('operator')) {
        if (keyValue === '=') {
            try {
                currentValue = eval(currentValue).toString();
            } catch {
                currentValue = 'Error';
            }
            updateDisplay();
            resetScreen = true;
        } else {
            if (resetScreen) {
                resetScreen = false;
            }
            currentValue += keyValue;
            updateDisplay();
        }
        return;
    }

    if (key.classList.contains('all-clear')) {
        currentValue = '';
        updateDisplay();
        return;
    }

    if (key.classList.contains('decimal')) {
        if (resetScreen) {
            currentValue = '0';
            resetScreen = false;
        }
        if (!currentValue.includes('.')) {
            currentValue += '.';
        }
        updateDisplay();
        return;
    }

    if (resetScreen) {
        currentValue = '';
        resetScreen = false;
    }

    currentValue += keyValue;
    updateDisplay();
});