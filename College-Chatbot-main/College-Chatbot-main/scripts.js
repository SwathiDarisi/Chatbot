const chatbotBody = document.getElementById('chatbot-body');
const chatbotContainer = document.getElementById('chatbot-container');
const openButton = document.getElementById('open-chatbot');
const closeButton = document.getElementById('close-chatbot');

// Toggle chatbot container visibility
openButton.addEventListener('click', function() {
  chatbotContainer.style.display = 
    chatbotContainer.style.display === 'none' || 
    chatbotContainer.style.display === '' ? 'block' : 'none';
});

// Close chatbot container
closeButton.addEventListener('click', function() {
  chatbotContainer.style.display = 'none';
});

// Input field functionality
const inputField = document.querySelector('#chatbot-footer input[type="text"]');
const sendButton = document.getElementById('send-message');

async function fetchPythonResponse(userMessage) {
  const apiUrl = 'http://127.0.0.1:5000/chat'; // Flask server URL

  try {
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message: userMessage }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      console.error('API Error:', errorData);
      throw new Error(errorData.error || 'Unknown API error');
    }

    const data = await response.json();
    return data.reply || 'Sorry, no response received from the bot.';
  } catch (error) {
    console.error('Error fetching Python API response:', error);
    return 'Sorry, I am unable to process your request at the moment.';
  }
}

const scrollButton = document.getElementById('scroll-button');

// Toggle scroll button visibility and functionality
chatbotBody.addEventListener('scroll', () => {
  const icon = scrollButton.querySelector('i');
  if (chatbotBody.scrollTop > 0) {
    scrollButton.style.display = 'block';
    icon.classList.remove('fa-angle-double-down');
    icon.classList.add('fa-angle-double-up'); // Change to up icon
  } else {
    icon.classList.remove('fa-angle-double-up');
    icon.classList.add('fa-angle-double-down'); // Change to down icon
  }
});

scrollButton.addEventListener('click', () => {
  if (scrollButton.querySelector('i').classList.contains('fa-angle-double-up')) {
    chatbotBody.scrollTo({ top: 0, behavior: 'smooth' }); // Scroll to top
  } else {
    chatbotBody.scrollTo({ top: chatbotBody.scrollHeight, behavior: 'smooth' }); // Scroll to bottom
  }
});

// Ensure scroll button visibility updates on new messages
function updateScrollButton() {
  if (chatbotBody.scrollTop + chatbotBody.clientHeight < chatbotBody.scrollHeight) {
    scrollButton.style.display = 'block';
  } else {
    scrollButton.style.display = 'none';
  }
}

function addMessage(message, isUser = true) {
  const messageElement = document.createElement('p');
  messageElement.textContent = message;
  if (isUser) {
    messageElement.classList.add('user-message');
  } else {
    messageElement.classList.add('bot-message');
  }
  chatbotBody.appendChild(messageElement);
  chatbotBody.scrollTop = chatbotBody.scrollHeight; // Scroll to the latest message
  updateScrollButton();
}

if (inputField && sendButton) {
  sendButton.addEventListener('click', async function () {
    if (inputField.value.trim() !== '') {
      const userMessage = inputField.value;
      addMessage(`${userMessage}`);
      inputField.value = '';

      // Fetch and display the Python API response
      const botReply = await fetchPythonResponse(userMessage);
      addMessage(`${botReply}`, false);
    }
  });

  inputField.addEventListener('keypress', async function (e) {
    if (e.key === 'Enter' && inputField.value.trim() !== '') {
      const userMessage = inputField.value;
      addMessage(`${userMessage}`);
      inputField.value = '';

      // Fetch and display the Python API response
      const botReply = await fetchPythonResponse(userMessage);
      addMessage(`${botReply}`, false);
    }
  });
}

// Handle option clicks
document.querySelectorAll('.option-box').forEach(option => {
  option.addEventListener('click', async function () {
    const userMessage = this.getAttribute('data-option');
    addMessage(`${userMessage}`);
    
    // Fetch and display the Python API response
    const botReply = await fetchPythonResponse(userMessage);
    addMessage(`${botReply}`, false);
  });
});

// Debounce scroll event
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Improved scroll handler
const handleScroll = debounce(() => {
  const header = document.querySelector('.header');
  const body = document.body;
  if (window.scrollY > 0) {
    header.classList.add('sticky');
    body.classList.add('sticky-padding');
  } else {
    header.classList.remove('sticky');
    body.classList.remove('sticky-padding');
  }
}, 16);

window.addEventListener('scroll', handleScroll);

// Improved mobile menu
const mobileMenu = {
  button: document.querySelector('.mobile-menu-btn'),
  nav: document.querySelector('.nav-menu'),
  isOpen: false,
  
  init() {
    this.button.addEventListener('click', () => this.toggle());
    // Close menu on outside click
    document.addEventListener('click', (e) => {
      if (!this.nav.contains(e.target) && !this.button.contains(e.target)) {
        this.close();
      }
    });
  },
  
  toggle() {
    this.isOpen = !this.isOpen;
    this.nav.classList.toggle('active');
    this.button.setAttribute('aria-expanded', this.isOpen);
  },
  
  close() {
    this.isOpen = false;
    this.nav.classList.remove('active');
    this.button.setAttribute('aria-expanded', false);
  }
};

mobileMenu.init();

// Popup functionality for "How can I help you?"
const chatbotPopup = document.getElementById('chatbot-popup');

// Show the popup initially
chatbotPopup.style.display = 'block';

// Toggle the popup every 10 seconds
setInterval(() => {
  chatbotPopup.style.display = chatbotPopup.style.display === 'none' || chatbotPopup.style.display === '' ? 'block' : 'none';
}, 10000);
