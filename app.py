from flask import Flask, render_template, request, redirect, url_for
from bs4 import BeautifulSoup
import requests
import re
from collections import Counter
from unidecode import unidecode
import mysql.connector

app = Flask(__name__)

# Database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",  # Change to your MySQL username
    password="Subhash@1492004",  # Change to your MySQL password
    database="Db"  # Ensure this database exists
)

cursor = db.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS word_counts (
        id INT AUTO_INCREMENT PRIMARY KEY,
        word VARCHAR(255),
        frequency INT
    )
''')
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/fetch-words', methods=['POST'])
def fetch_words():
    url = request.form.get('url')
    top_n = int(request.form.get('top_n'))

    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()
        # Normalize and clean text
        text = unidecode(text)
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        # Count word frequency
        word_counts = Counter(words)
        word_data = word_counts.most_common(top_n)

        # Clear previous records and insert new data into the database
        cursor.execute("DELETE FROM word_counts")
        for word, freq in word_data:
            cursor.execute("INSERT INTO word_counts (word, frequency) VALUES (%s, %s)", (word, freq))
        db.commit()

        return render_template('table.html', word_data=word_data, top_n=top_n, url= url)

    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == '__main__':
    app.run(debug=True)

