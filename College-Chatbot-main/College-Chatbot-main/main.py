from flask import Flask, request, jsonify, send_from_directory # for server-side rendering
import os # Import os for accessing files
from dotenv import load_dotenv  # Import dotenv to load environment variables
import firebase_admin # Import Firebase Admin SDK
from firebase_admin import credentials, firestore
from sentence_transformers import SentenceTransformer, util  # Import SentenceTransformer for semantic similarity
import google.generativeai as genai  # Re-import google.generativeai

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='.', static_url_path='')

# Initialize Firebase Admin SDK
cred = credentials.Certificate({
    "type": "service_account",
    "project_id": "chatbot-ac650",
    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL"),
    "universe_domain": "googleapis.com"
})
firebase_admin.initialize_app(cred)
db = firestore.client()

# Load pre-trained SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Define a function to get chatbot responses
def get_response(query):
    original_query = query.strip()  # Store the original query for logging
    query = query.lower().strip()
    
    # Fetch FAQ data from Firestore dynamically to ensure the latest data is used
    faq_docs = db.collection('FAQs').stream()
    questions = []
    answers = []
    for doc in faq_docs:
        faq = doc.to_dict()

         # Check if the document contains a single question or multiple questions
        if isinstance(faq['Question'], list):  # One answer with many questions
            for question in faq['Question']:
                questions.append(question)
                answers.append(faq['Answer'])
        else:  # One-to-one mapping
            questions.append(faq['Question'])
            answers.append(faq['Answer'])
    
    # Encode the questions using the SentenceTransformer model
    question_embeddings = model.encode(questions, convert_to_tensor=True)
    
    # Encode the query using the SentenceTransformer model
    query_embedding = model.encode(query, convert_to_tensor=True)
    
    # Compute cosine similarity between the query and FAQ questions
    similarities = util.cos_sim(query_embedding, question_embeddings)
    
    # Sort indices by similarity scores in descending order
    sorted_indices = similarities[0].argsort(descending=True)
    
    # Collect answers for the top 3 most similar questions if their scores exceed the threshold
    threshold = 0.5  # Semantic similarity confidence threshold
    top_answers = []
    for idx in sorted_indices[:3]:  # Top 3 matches
        if similarities[0, idx].item() > threshold:
            top_answers.append((answers[idx], questions[idx]))
    
    # Check for semantic similarity matches in the query
    best_match_answer = None
    if top_answers:
        best_match_answer = top_answers[0][0]  # Take the answer with the highest similarity score
    
    # Return the best match answer if found, otherwise provide a fallback response
    if not best_match_answer:
        unanswered_docs = db.collection('UnansweredQuestions').stream()
        for doc in unanswered_docs:
            unanswered_data = doc.to_dict()
            if unanswered_data.get('question', '').lower() == original_query.lower():
                # If an updated answer exists, return it
                if 'answer' in unanswered_data:
                    return unanswered_data['answer']
        
        unanswered_question = {
            "question": original_query,
            "timestamp": firestore.SERVER_TIMESTAMP
        }
        db.collection('UnansweredQuestions').add(unanswered_question)
        return """I'm sorry, I don't have information on that. For more information All Enquiries:
                  +91-88852-19222
                  +91-98482-50750
                  +91-91776-50018
                  Email: principal@pscmr.ac.in
                  Website: https://www.pscmr.ac.in/
                """
    return best_match_answer


def sendPrompt(data, question):
    # Set your free API key from Google AI Studio
    API_KEY = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=API_KEY)

    # Load Gemini 1.5 Flash model
    model = genai.GenerativeModel(model_name="gemini-2.0-flash")

    prompt = f"""
        Don't give any unnecessary response other than the 'Query' asked.
        Give only response from the 'Data' provided and give the complete data for that 'Query'.
        
        Data: 
        {data}
        
        Query:
        {question}
    """

    # Generate content using the free API key
    response = model.generate_content(prompt)
    return response.text

# Flask route to handle chatbot requests
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')

    # Auto-correct the user's message using Gemini
    autocorrect_prompt = f"""
        Correct the spelling and grammar of the following sentence. 
        Provide only the corrected sentence without any additional explanation or response.
        
        Sentence:
        {user_message}
    """
    API_KEY = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel(model_name="gemini-2.0-flash")
    autocorrected_message = model.generate_content(autocorrect_prompt).text.strip()

    # Use the auto-corrected message for further processing
    response_data = get_response(autocorrected_message)
    bot_reply = sendPrompt(response_data, autocorrected_message)
    return jsonify({'reply': bot_reply})

# Serve the homepage
@app.route('/')
def homepage():
    return send_from_directory('.', 'homepage.html')

# Serve the contact page
@app.route('/contact')
def contact():
    return send_from_directory('.', 'contact.html')

# Serve the about page
@app.route('/about')
def about():
    return send_from_directory('.', 'about.html')

# Serve the academics page
@app.route('/academics')
def academics():
    return send_from_directory('.', 'academics.html')

if __name__ == '__main__':
    app.run(debug=True)