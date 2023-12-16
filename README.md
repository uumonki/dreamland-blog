# dreamland-blog

## Overview
This project is a Flask-based web application created for myself and a friend to log & compare our dreams. It features a dual narrative layout where dreams are displayed side by side on a vertical timeline. The front end is implemented using pure CSS and JavaScript since the small scale of the project does not necessitate more complex frameworks. Google OAuth is used for user authentication, and SQLite is used to store blog posts and user data. Other external resources include [`html2canvas`](https://html2canvas.hertzen.com/) and [`long-press-event`](https://github.com/john-doherty/long-press-event).

Please note that this project is not optimized for UX. The audience is quite limited, and having users "scavenger hunt" through the UI encourages them to read the text in its entirety.

## Getting Started
This blog application can be adapted for other dual narrative projects or as a template for individual blogs. To run the app locally, follow these steps.
1. Clone the repository.
2. Install the necessary Python packages (`pip install -r requirements.txt`).
3. Set up the .env file in the same directory as app.py. You should include the following.
   - `FLASK_SECRET_KEY` ([Where do I get secret key for Flask?](https://stackoverflow.com/questions/34902378/where-do-i-get-secret-key-for-flask))
   - `DATABASE_URI` (something like `sqlite:///blog.db`)
   - `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` ([Where do I get Client ID and Secret?](https://analytify.io/get-google-client-id-and-client-secret/))
   - `ADMIN_EMAILS=admin1@email.com,admin2@email.com`
5. Run app.py to start the Flask server.
6. Access the blog at `localhost:5000`.

Feel free to adapt this project to your needs, whether for personal use or as a template for a different type of dual-narrative blog.
