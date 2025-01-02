async function askQuestion() {
    const questionInput = document.getElementById("question");
    const chatHistory = document.getElementById("chat-history");

    const userQuestion = questionInput.value.trim();
    if (!userQuestion) {
        alert("Please enter a question.");
        return;
    }

    // Display user's message
    const userMessage = document.createElement("div");
    userMessage.classList.add("chat-message", "user-message");
    userMessage.textContent = userQuestion;
    chatHistory.appendChild(userMessage);

    // Clear input field
    questionInput.value = "";

    // Display loading animation
    const loadingMessage = document.createElement("div");
    loadingMessage.classList.add("chat-message", "loading-message");
    loadingMessage.innerHTML = `
        <span>Sharif's AI Assistant is thinking...</span>
        <div class="loading-spinner"></div>
    `;
    chatHistory.appendChild(loadingMessage);

    chatHistory.scrollTop = chatHistory.scrollHeight; // Auto-scroll to bottom

    try {
        // Send the question to the server
        const response = await fetch("/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question: userQuestion }),
        });

        const result = await response.json();
        const botAnswer = result.answer || "Sorry, I couldn't find an answer.";

        // Remove loading animation
        chatHistory.removeChild(loadingMessage);

        // Display bot's response
        const botMessage = document.createElement("div");
        botMessage.classList.add("chat-message", "bot-message");
        botMessage.textContent = botAnswer;
        chatHistory.appendChild(botMessage);
    } catch (error) {
        console.error("Error fetching answer:", error);

        // Remove loading animation
        chatHistory.removeChild(loadingMessage);

        // Display error message
        const errorMessage = document.createElement("div");
        errorMessage.classList.add("chat-message", "bot-message");
        errorMessage.textContent = "Sorry, an error occurred.";
        chatHistory.appendChild(errorMessage);
    } finally {
        chatHistory.scrollTop = chatHistory.scrollHeight; // Auto-scroll to bottom
    }
}
