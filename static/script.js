document.addEventListener("DOMContentLoaded", function () {
  var askButton = document.getElementById("askButton");
  var userQuestionInput = document.getElementById("userQuestion");
  var chatArea = document.getElementById("chatArea");

  function askQuestion() {
    var userQuestion = userQuestionInput.value.trim();
    userQuestionInput.value = ""; // Clear the input after sending the question

    // Append user's question to the chat area
    chatArea.innerHTML += `<p class="user-question">You: ${userQuestion}</p>`;

    fetch("/ask", {
      method: "POST",
      body: new URLSearchParams({ question: userQuestion }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.clear_chat) {
          // If the backend indicates the chat should be cleared, prompt the user
          chatArea.innerHTML += `<p class="bot-answer">Bot: ${data.answer}</p>`;
          showClearChatOption();
        } else {
          // Display the chatbot's answer in the chat area
          chatArea.innerHTML += `<p class="bot-answer">Bot: ${data.answer}</p>`;
        }
        // Auto scroll to the bottom of the chat area to show the latest message
        chatArea.scrollTop = chatArea.scrollHeight;
      })
      .catch((error) => console.error("Error:", error));
  }

  function showClearChatOption() {
    // Provide Yes/No buttons for user to choose whether to clear chat history
    chatArea.innerHTML += `
            <p class="clear-chat-question">Clear chat history? <button onclick="clearChat(true)">Yes</button> <button onclick="clearChat(false)">No</button></p>
        `;
    // Disable the ask button since we are now only expecting a clear chat confirmation
    askButton.disabled = true;
  }

  window.clearChat = function (clear) {
    // Enable the ask button again as the clear chat confirmation has been handled
    askButton.disabled = false;
    if (clear) {
      // Send a 'yes' response to the server to clear the chat history
      fetch("/ask", {
        method: "POST",
        body: new URLSearchParams({ question: "yes" }),
      })
        .then((response) => response.json())
        .then((data) => {
          chatArea.innerHTML = ""; // Clears the chat history
          chatArea.innerHTML += `<p class="bot-answer">Bot: ${data.answer}</p>`;
        })
        .catch((error) => console.error("Error:", error));
    } else {
      // If the user selects 'No', the chat history is preserved and the user can continue
      var clearChatQuestion = document.querySelector(".clear-chat-question");
      if (clearChatQuestion) clearChatQuestion.remove();
    }
  };

  askButton.onclick = function () {
    askQuestion();
  };

  // Allow pressing Enter to send a question
  userQuestionInput.addEventListener("keypress", function (event) {
    if (event.key === "Enter") {
      event.preventDefault();
      askButton.click();
    }
  });
});
