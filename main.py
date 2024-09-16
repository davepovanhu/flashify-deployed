from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import os
from io import BytesIO

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to restrict to specific domains if needed
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Configure Google Generative AI API Key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)


@app.post("/generate-flashcards/")
async def generate_flashcards(summary: str = Form(...)):
    """
    Generate flashcards from the provided summary.
    If no summary is provided, return an error message.
    """
    if not summary:
        return {"error": "No text provided to generate flashcards"}

    try:
        # Use the Generative AI to generate questions and answers from the summary
        model = genai.GenerativeModel("gemini-1.5-flash")
        flashcard_result = model.generate_content([summary, "Generate flashcards in a Question || Answer format."])

        # Split the result into flashcards assuming it generates them in "Question || Answer" pairs
        flashcards = [
            {"question": fc.split("||")[0].strip(), "answer": fc.split("||")[1].strip()}
            for fc in flashcard_result.text.split("\n") if "||" in fc
        ]

        return {"flashcards": flashcards}

    except Exception as e:
        return {"error": str(e)}


@app.get("/")
async def root():
    """
    Simple GET endpoint to verify the service is running.
    """
    return {"message": "Flashcard Generator is running! You can post summaries to /generate-flashcards to get flashcards."}

# To run the app: uvicorn main:app --reload
