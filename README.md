🛒 Online Shopping Voice Assistant for Visually Impaired People
📌 Project Overview

This project is a voice-based shopping assistant designed for visually impaired users.
It allows users to search products across multiple e-commerce platforms using voice commands only.
The assistant handles speech recognition, translation, scraping product details, and text-to-speech so that users can interact without typing or reading.

🎯 Features

🎙️ Voice Input – Users give shopping queries through speech.

🌐 Language Detection & Translation – Detects user’s language and translates queries into English.

🔍 Product Search – Scrapes product details from e-commerce websites.

⚡ Parallel Processing – Fetches results faster from multiple platforms.

📖 Voice Output – Reads out product details using Text-to-Speech.

🌍 Opens Product Page – Automatically launches the product page in the browser for safe transactions.

🏗️ Tech Stack
Frontend

Gradio

webbrowser

Backend

SpeechRecognition / Whisper API

langdetect

deep_translator (GoogleTranslator)

Selenium WebDriver + BeautifulSoup

ThreadPoolExecutor / threading

gTTS

time, platform, OS commands, webdriver_manager

🚀 How It Works

User speaks a product query (e.g., “Search red shoes”).

Speech is converted to text (SpeechRecognition / Whisper API).

Language is auto-detected and translated to English if needed.

Selenium + BeautifulSoup scrape product details from supported sites.

Results are read aloud using gTTS.

Product links automatically open in the default browser.

Final purchase is securely done on the official website.

🔐 Security Note

The assistant does not handle payments.

All transactions happen on the official e-commerce platforms (Amazon, Flipkart, Snapdeal, etc.) following PCI compliance.
