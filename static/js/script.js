async function askQuestion() {
    const question = document.getElementById("question").value;
    if (!question.trim()) {
        document.getElementById("answer").innerText = "Please type a question!";
        return;
    }
    const response = await fetch("/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: question })
    });
    const data = await response.json();
    document.getElementById("answer").innerText = data.answer || data.error;
}
