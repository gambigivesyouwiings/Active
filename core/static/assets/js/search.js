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

    function handleOutsideClick(event) {
        const container = document.getElementById('chatContainer');
        const icon = document.querySelector('.chat-icon');

        // Check if the click is outside the chat container or chat icon
        if (!container.contains(event.target) && !icon.contains(event.target)) {
            toggleChat(); // Close the chat
        }
    }

    function toggleChat() {
            const container = document.getElementById('chatContainer');
            const header = document.getElementById('chat-header-two');
            isChatOpen = !isChatOpen;
            container.style.display = isChatOpen ? 'flex' : 'none';
            if (isChatOpen) {
            document.addEventListener('click', handleOutsideClick);
            } else {
            document.removeEventListener('click', handleOutsideClick);
        }
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
function handleWhatsAppKeyPress(event) {
        if (event.key === 'Enter') {
            const userInput = document.getElementById('userInput').value;

            // Encode the message and phone number
            const phoneNumber = '+254732252382';
            const message = encodeURIComponent(userInput);

            // Construct the WhatsApp link
            const whatsappUrl = `https://wa.me/${phoneNumber}?text=${message}`;

            // Open the WhatsApp URL in a new tab or window
            window.open(whatsappUrl, '_blank');
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

function addEventOnInput() {
    // Attach the document click listener only when the user types in the input
    document.addEventListener("click", handleDocumentClick);
}


function onFormSubmit(event) {
        // Prevent the default search (form submission) behavior
        event.preventDefault();
        console.log("Default search function of #myForm disabled");
}


function chooseFilter(event) {
    var filterActions = document.getElementById("filter-actions");
    // Check if the clicked element is a button
    if (event.target && event.target.tagName === "BUTTON") {
        // Remove the 'active' class from all buttons
        const buttons = filterActions.getElementsByClassName("toggle-btn");
        for (let button of buttons) {
            button.classList.remove("active");
        }

        // Add the 'active' class to the clicked button
        event.target.classList.add("active");
    }
};

  function performSearch() {

    var csrfToken = document.getElementById('csrf').value
    const formData = {
        keyword: document.getElementById('keyword').value,
        brand: document.getElementById('brand').value,
        model: document.getElementById('model').value,
        order: document.getElementById('feature').value,
        price: Array.from(document.querySelectorAll('input[name="price"]:checked')).map(cb => cb.value),
        availability: document.querySelector('.toggle-btn.active').dataset.value
        // features: Array.from(document.getElementById('features').selectedOptions).map(opt => opt.value)
    };
1
    fetch('/vehicles', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRF-Token': csrfToken
        },
        body: JSON.stringify(formData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.text(); // Return the response as HTML
    })
    .then(html => {
        // Update the part of the page with the new HTML
        document.getElementById('results-container').innerHTML = html;
    })
    .catch(error => console.error('Error:', error));
}

function clearFilters() {
    document.getElementById('searchForm').reset();
    document.querySelectorAll('.toggle-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelector('.toggle-btn[data-value="all"]').classList.add('active');
}

function toggleFilterForm() {
            const form = document.getElementById("target");
            const button = document.getElementById('filterButton');

            if (form.style.display === 'none' || form.style.display === '') {
                form.style.display = 'block';
                button.textContent = 'Hide filters';
            } else {
                form.style.display = 'none';
                button.textContent = 'Show filters';
            }
        }
function filterItems(category) {
      const cards = document.querySelectorAll('.check');
      cards.forEach(card => {
        if (card.dataset.category === category) {
          card.classList.remove('hidden');
        } else {
          card.classList.add('hidden');
        }
      });
    }