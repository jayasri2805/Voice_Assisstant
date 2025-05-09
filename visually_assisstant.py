import gradio as gr
import speech_recognition as sr
from deep_translator import GoogleTranslator
from langdetect import detect
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
from gtts import gTTS
import os
import platform
from webdriver_manager.chrome import ChromeDriverManager
from concurrent.futures import ThreadPoolExecutor
import threading
import webbrowser

# WebDriver setup
def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

# Function to scrape Myntra
def scrape_myntra(query):
    driver = get_driver()
    driver.get(f"https://www.myntra.com/{query.replace(' ', '-')}")
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    products = soup.find_all("li", class_="product-base")[:1]
    results = []
    for p in products:
        title = p.find("h4", class_="product-product")
        price = p.find("div", class_="product-price")
        link = p.find("a", class_="product-base")

        if title and price and link:
            product_url = f"https://www.myntra.com{link['href']}"
            results.append(f"{title.text} - {price.text} - {product_url}")
            webbrowser.open(product_url)

    return results if results else ["No products found on Myntra."]

# Function to scrape Snapdeal
def scrape_snapdeal(query):
    driver = get_driver()
    driver.get(f"https://www.snapdeal.com/search?keyword={query.replace(' ', '%20')}")
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    product = soup.find("div", class_="product-tuple-listing")
    results = []
    if product:
        title = product.find("p", class_="product-title")
        price = product.find("span", class_="lfloat product-price")
        link = product.find("a", href=True)

        if title and price and link:
            product_url = link["href"]
            results.append(f"{title.text.strip()} - {price.text.strip()} - {product_url}")
            webbrowser.open(product_url)
    else:
        results.append("No products found on Snapdeal.")

    return results

# Parallel scraping
def fetch_product_data_parallel(query):
    with ThreadPoolExecutor() as executor:
        results = {
            "Myntra": executor.submit(scrape_myntra, query),
            "Snapdeal": executor.submit(scrape_snapdeal, query),
        }
    return {platform: result.result() for platform, result in results.items()}

# Speech recognition
def recognize_speech(audio):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio) as source:
        recognizer.adjust_for_ambient_noise(source)
        audio_data = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio_data, language="ta-IN,hi-IN,ml-IN,en-IN,te-IN")
        detected_lang = detect(text)
        return text, detected_lang
    except:
        return "❌ Speech recognition failed.", None

# Translation function
def translate_text(text, src_lang, dest_lang="en"):
    if src_lang == dest_lang:
        return text
    return GoogleTranslator(source=src_lang, target=dest_lang).translate(text)

# Text-to-speech function
def text_to_speech(text, lang):
    tts = gTTS(text=text, lang=lang)
    audio_file = "output.mp3"
    tts.save(audio_file)

    if platform.system() == "Windows":
        os.system(f"start {audio_file}")
    else:
        os.system(f"mpg321 {audio_file}")

    return audio_file

# Main function
def process_audio(audio):
    query, user_lang = recognize_speech(audio)
    if not user_lang:
        return "❌ Speech recognition failed.", None

    translated_query = translate_text(query, user_lang, "en")
    products = fetch_product_data_parallel(translated_query)

    translated_results = {
        platform: [translate_text(result, "en", user_lang) for result in data]
        for platform, data in products.items()
    }

    response_text = f"You said: {query} (Language: {user_lang})\n\n" + \
                    f"Translated Query: {translated_query}\n\n" + \
                    "\n Best Deals Found:\n" + "\n".join(
                        [f"{platform}:\n" + "\n".join(data) for platform, data in translated_results.items()]
                    )

    threading.Thread(target=text_to_speech, args=(response_text, user_lang)).start()
    return response_text, "output.mp3"

# Gradio Interface
gr.Interface(
    fn=process_audio,
    inputs=gr.Audio(type="filepath"),
    outputs=[gr.Textbox(label="Product Search Results"), gr.Audio(label="Audio Output")],
    title="🚀 AI Powered Online Shopping Voice Assistant for Visually Impaired People 🎧🛍",
    description="Speak the product name, and the assistant finds the best deals for you in multiple languages! The product pages will open automatically.",
).launch()



