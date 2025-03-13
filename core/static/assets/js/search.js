let isChatOpen = false;
let chatHistory = [];

//addMessageToHistory('Hello, I\'m here to answer any Insurance-related question you have according to the policies offered by Faithful Insurance', 'bot')
async function sendMessage() {
            const input = document.getElementById('userInput');
            const message = input.value.trim();
            if (!message) return;

            addMessageToHistory(message, 'user');
            input.value = '';

            try {
                const typingIndicator = addTypingIndicator();

                // Send to Flask backend
                const response = await fetch('http://localhost:5000/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ message: message })
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();

                typingIndicator.remove();
                addMessageToHistory(data.response, 'bot');

            } catch (error) {
                console.error('Error:', error);
                addMessageToHistory('Sorry, there was an error processing your request.', 'bot');
            }
        }
    function toggleChat() {
            const container = document.getElementById('chatContainer');
            const header = document.getElementById('chat-header-two');
            isChatOpen = !isChatOpen;
            container.style.display = isChatOpen ? 'flex' : 'none';
            header.addEventListener('mousedown', (e) => {
    isMouseDown = true;
    const x = e.clientX - container.offsetLeft;
    const y = e.clientY - container.offsetTop;

    window.addEventListener('mousemove', (e) => {
        if (isMouseDown) {
            container.style.setProperty('--left', `${e.clientX - x}px`);
            container.style.setProperty('--top', `${e.clientY - y}px`);
        }
    });

    container.addEventListener('mouseup', () => {
        isMouseDown = false;
    });
});
        }

    function closeSearch (){
    let targetDiv = document.getElementById('results');
    let myInput = document.getElementById('myInput');
    targetDiv.classList.add("hide")
    targetDiv.replaceChildren();
    document.getElementById('myForm').reset();
    }

    function addMessageToHistory(text, sender) {
            const history = document.getElementById('chatHistory');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;
            messageDiv.textContent = text;
            history.appendChild(messageDiv);
            history.scrollTop = history.scrollHeight;
        }

        function addTypingIndicator() {
            const history = document.getElementById('chatHistory');
            const typingDiv = document.createElement('div');
            typingDiv.className = 'message bot-message';
            typingDiv.textContent = '...';
            typingDiv.id = 'typingIndicator';
            history.appendChild(typingDiv);
            return typingDiv;
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }
// Function to handle the document-level click event
function handleDocumentClick(event) {
    const startTime = performance.now();
    var formElement = document.getElementById("myForm");
    var resultsDiv = document.getElementById("results");

    // Check if the click happened inside the form
    if (formElement && formElement.contains(event.target)  || resultsDiv && resultsDiv.contains(event.target)) {
        console.log("Click inside #myForm, propagation stopped");
        return;
    }

    // Avoid layout thrashing by batching reads and writes
    if (resultsDiv) {
        const hasHideClass = resultsDiv.classList.contains("hide"); // Batch read
        debounceTimer = setTimeout(() => {
            requestAnimationFrame(() => {
                if (!hasHideClass) {
                    resultsDiv.classList.add("hide");
                    resultsDiv.replaceChildren();
                    console.log("Class 'hide' added to the #results div");
                }
            });
        }, 100); // Adjust debounce interval if needed
    }

    // Remove the event listener after it's triggered
    document.removeEventListener("click", handleDocumentClick);
    console.log("Document click listener removed");
    const duration = performance.now() - startTime;
    console.log(`someMethodIThinkMightBeSlow took ${duration}ms`);
}

// Add an event listener to the input field
var inputField = document.getElementById("myInput");
inputField.addEventListener("input", function() {
    // Attach the document click listener only when the user types in the input
    document.addEventListener("click", handleDocumentClick);
});

// Get the form element with the id "myForm"
var myForm = document.getElementById("myForm");

// Add an event listener to the form for the 'submit' event
myForm.addEventListener("submit", function(event) {
    // Prevent the default search (form submission) behavior
    event.preventDefault();
    console.log("Default search function of #myForm disabled");
});
