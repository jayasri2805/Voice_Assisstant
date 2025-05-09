from flask import Flask, request, jsonify, render_template
import speech_recognition as sr
from gtts import gTTS
import os
import platform
from deep_translator import GoogleTranslator
from langdetect import detect
import webbrowser
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

app = Flask(__name__)

# WebDriver setup for scraping
def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

# Scrape Snapdeal (example scraping method)
def scrape_snapdeal(query):
    driver = get_driver()
    driver.get(f"https://www.snapdeal.com/search?keyword={query.replace(' ', '%20')}")
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    products = soup.find_all("div", class_="product-tuple-listing")[:1]
    results = []
    for p in products:
        title = p.find("p", class_="product-title")
        price = p.find("span", class_="lfloat product-price")
        link = p.find("a", class_="dp-widget-link")

        if title and price and link:
            product_url = link['href']
            results.append(f"{title.text.strip()} - {price.text.strip()} - {product_url}")
            webbrowser.open(product_url)

    return results if results else ["No products found on Snapdeal."]

# Function to recognize speech and convert to text
def recognize_speech(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        recognizer.adjust_for_ambient_noise(source)
        audio_data = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio_data)
        return text
    except Exception as e:
        print(f"Error recognizing speech: {e}")
        return "❌ Speech recognition failed."

# Function to translate text
def translate_text(text, src_lang, dest_lang="en"):
    if src_lang == dest_lang:
        return text
    return GoogleTranslator(source=src_lang, target=dest_lang).translate(text)

# Text to speech (using gTTS)
def text_to_speech(text, lang="en"):
    tts = gTTS(text=text, lang=lang)
    audio_file = "output.mp3"
    tts.save(audio_file)

    if platform.system() == "Windows":
        os.system(f"start {audio_file}")
    else:
        os.system(f"mpg321 {audio_file}")

    return audio_file

# Function to detect the language of the user's speech
def detect_language(text):
    try:
        return detect(text)
    except Exception as e:
        print(f"Error detecting language: {e}")
        return "en"  # Default to English if detection fails

# Function to process user query and fetch product data
def process_audio_query(audio_path):
    query = recognize_speech(audio_path)
    if "❌" in query:
        return query

    # Detect the language of the query
    lang = detect_language(query)
    print(f"Detected language: {lang}")

    # Translate the query to English (if needed)
    translated_query = translate_text(query, lang, "en")

    # Fetch product data
    product_results = scrape_snapdeal(translated_query)

    # Prepare the response for the user
    response = "You asked for: " + query + "\n\nBest product found: " + "\n".join(product_results)

    # Translate the response back to the user's language
    translated_response = translate_text(response, "en", lang)

    # Provide the response in the user's language
    text_to_speech(translated_response, lang)

    return translated_response

# Endpoint for handling voice input
@app.route('/voice_order', methods=['POST'])
def voice_order():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files['audio']
    audio_path = "user_input.wav"
    audio_file.save(audio_path)

    # Process the audio and fetch product details
    response = process_audio_query(audio_path)

    return jsonify({"response": response})

# Home route for the web app
@app.route('/')
def index():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)







