async function startTranscription() {
    const fileInput = document.getElementById("audioFile");  // Make sure this matches your input elements id
    const resultText = document.getElementById("resultText");

    if (!fileInput.files[0]) {
        alert("Please select an audio file.");
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);  // Ensure this matches the FastAPI parameter name ('file')

    resultText.textContent = "Transcribing... Please wait.";

    try {
        const response = await fetch("/api/transcribe/", {
            method: "POST",
            body: formData,  // This sends the file in the request body
        });

        const data = await response.json();

        if (!response.ok) {
            console.log("Server responded with an error:", data);
            resultText.textContent = `Error: ${data.detail || "Failed to transcribe"}`;
            return;
        }

        resultText.textContent = data.transcription || "No transcription available.";
    } catch (error) {
        console.error("Error during transcription:", error);
        resultText.textContent = "Error during transcription. Please try again.";
    }
}
