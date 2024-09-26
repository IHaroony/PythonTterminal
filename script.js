document.addEventListener('DOMContentLoaded', () => {
    const socket = io('https://pythontterminal-production.up.railway.app');


    const term = new Terminal({
        cursorBlink: true,  // Make the cursor blink
        fontFamily: 'Cascadia Code, Courier New, monospace',
        fontSize: 14,
        theme: {
            background: 'rgba(255, 255, 255, 0.8)', // Semi-transparent background
            foreground: '#333', // Dark text color
            cursor: '#007ACC', // Light blue cursor
            selection: 'rgba(0, 120, 212, 0.3)', // Blue selection highlight
        }
    });

    const container = document.getElementById('terminal');
    const terminalContainer = document.getElementById('terminal-container');
    term.open(container); // Open the terminal in the container


    let inputBuffer = ''; // To store user input

    // Handle user input
    term.onData(data => {
        // Handle backspace
        if (data === '\x7f') { // ASCII for backspace
            if (inputBuffer.length > 0) {
                inputBuffer = inputBuffer.slice(0, -1); // Remove last character
                term.write('\b \b'); // Visually remove last character
            }
        } else if (data === '\r') { // Enter key
            term.write('\r\n'); // Move to new line
            socket.emit('input', inputBuffer); // Send input to backend
            inputBuffer = ''; // Clear input buffer
        } else {
            inputBuffer += data; // Store user input
            term.write(data); // Display the input in the terminal
        }
    });

    // Handle output from the backend
    socket.on('output', (data) => {
        term.write(data + '\r\n'); // Print output to the terminal
    });

    // Error handling if connection fails
    socket.on('connect_error', (error) => {
        term.write('Connection error: ' + error + '\r\n');
    });

    // Toggle expansion when clicking the terminal
    terminalContainer.addEventListener('click', () => {
        terminalContainer.classList.toggle('expanded');
    });
});
