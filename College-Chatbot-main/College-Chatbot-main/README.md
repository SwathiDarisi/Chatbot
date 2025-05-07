# College-Chatbot

## Project Description
This project is a chatbot designed to assist users with queries related to college information.

## Prerequisites
- Python 3.x installed on your system.
- A valid `serviceAccountKey.json` file for Firebase authentication.
- A `.env` file containing necessary environment variables.

## Setup Instructions
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd College-Chatbot-main
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Add the required files:
   - Place the `serviceAccountKey.json` file in the root directory.
   - Create a `.env` file in the root directory and add the following environment variables:
     ```
     FIREBASE_PRIVATE_KEY="Your Firebase private key"
     FIREBASE_CLIENT_EMAIL="Your Firebase client email"
     GOOGLE_API_KEY="Your Google API key"
     ```

4. Run the application:
   ```bash
   python main.py
   ```

5. Open your browser and navigate to `http://localhost:5000` to view the application.

## Notes
- Ensure that the `FIREBASE_PRIVATE_KEY` value in the `.env` file replaces all newline characters (`\n`) with `\\n`.
- Obtain the `GOOGLE_API_KEY` from the Google Cloud Console.

## Deployment
Follow the deployment instructions for your hosting platform (e.g., AWS, Heroku, etc.).

## License
This project is licensed under the MIT License.