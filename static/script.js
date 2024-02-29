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
        // Display the chatbot's answer in the chat area
        chatArea.innerHTML += `<p class="bot-answer">Bot: ${data.answer}</p>`;

        // Check if the server response includes a prompt to clear the chat history
        if (data.prompt_clear_chat) {
          showClearChatOption(); // Show the option to clear the chat
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

  window.clearChat = function (shouldClear) {
    if (shouldClear) {
      // If the user chose to clear the chat, remove the chat history
      chatArea.innerHTML = "";
      // No need to contact the server here if you're just clearing the client-side chat
    } else {
      // If the user chose not to clear the chat, remove the Yes/No prompt
      var clearChatQuestion = document.querySelector(".clear-chat-question");
      clearChatQuestion.remove();
    }
    // Enable the ask button again as the clear chat confirmation has been handled
    askButton.disabled = false;
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
