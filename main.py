from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Configure Google Generative AI API Key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY is not set in the environment")

genai.configure(api_key=GOOGLE_API_KEY)

# FastAPI app setup
app = FastAPI()

# Allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from any domain for testing
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Flashcards generation endpoint
@app.post("/generate-flashcards/")
async def generate_flashcards(summary: str = Form(...)):
    """
    Generate flashcards from the provided summary using Google Generative AI.
    Returns a list of flashcards in Question || Answer format.
    """
    if not summary:
        return {"error": "No summary provided to generate flashcards"}

    try:
        # Use the Generative AI to generate flashcards
        model = genai.GenerativeModel("gemini-1.5-flash")
        flashcard_result = model.generate_content([summary, "Generate Question and Answer from the summary."])

        # Extract the text from the result
        generated_text = flashcard_result.text

        # Split the text into lines
        lines = generated_text.split("\n")

        # Initialize lists to store questions and answers
        questions = []
        answers = []

        # Process the lines and extract questions and answers
        for i in range(len(lines)):
            if '**Question:**' in lines[i]:
                question = lines[i].replace('**Question:** ', '').strip()
                questions.append(question)
            elif '**Answer:**' in lines[i]:
                answer = lines[i].replace('**Answer:** ', '').strip()
                answers.append(answer)

        # Combine questions and answers into flashcard pairs
        flashcards = list(zip(questions, answers))

        # Format the flashcards into the desired JSON structure
        flashcards_json = [{"question": q, "answer": a} for q, a in flashcards]

        return {"flashcards": flashcards_json}

    except Exception as e:
        return {"error": f"Error generating flashcards: {str(e)}"}


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint to ensure the service is running properly.
    """
    return {"status": "ok", "message": "Flashcard generator is healthy"}


# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the Flashcard Generator API!"}
