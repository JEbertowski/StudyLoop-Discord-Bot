**StudyLoop - Discord Bot**

*StudyLoop is an interactive Discord bot designed to help individuals and study groups learn efficiently through flashcards. Users can create, view, and quiz themselves on flashcards—either manually or by uploading PDFs of study material. The bot is fully functional, persistent, and hosted online for 24/7 access.*

🚀 **Features**

- Create and manage personal flashcards via Discord commands
- Study with randomized flashcard quizzes
- Organize flashcards using tags and filters
- Upload PDFs to auto-generate flashcards (short-answer and multiple choice supported)
- Persistent storage using JSON
- Export flashcards to share or back them up
- Import flashcards from a shared file
- !help command for full command list and guidance

🛠️ **Technologies Used**

- Python 3.x
- discord.api
- PyMuPDF (fitz) for PDF parsing
- JSON for local flashcard storage
- Render.com for hosting
- Git / GitHub for version control

🔧 **Setup Instructions**

1. Clone the repository:

   git clone https://github.com/JEbertowski/StudyLoop-Discord-Bot.git
   cd StudyLoop-Discord-Bot

2. Install the required dependencies:

   pip install -r requirements.txt

3. Create a .env file in the root directory and add your bot token:

   DISCORD_TOKEN=your_bot_token_here

4. Run the bot locally:

   python main.py

💬 **Available Commands**

Flashcard Commands:
• !addcard question | answer | [optional tag] – Add a new flashcard manually
• !viewcards [tag] – View your flashcards (optionally filter by tag)
• !clearcards – Delete all your flashcards

Study Commands:
• !study [tag] – Study flashcards one by one
• !reveal – Reveal the answer to the current flashcard
• !study_mcq [tag] – Study multiple-choice flashcards (auto-check answer)
• !answer a/b/c/... – Submit your answer for MCQ

Import/Export:
• !upload – Upload a PDF of flashcards to import
• !exportcards – Export flashcards as text
• !exportpdf – Export flashcards as a PDF file

🌐 **Deployment**

StudyLoop is deployed on Render.com as a Background Worker, ensuring it stays online and connected to Discord 24/7.

📄 **License**

This project is licensed under the MIT License.

Created with ❤️ by JEbertowski (https://github.com/JEbertowski)
