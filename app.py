import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob
from textblob import TextBlob
import pandas as pd
import cv2
import numpy as np
import pytesseract

from gtts import gTTS
from googletrans import Translator

selected_page = st.sidebar.radio("Selecciona una opción:", ["Te escuchamos", "Cámara"])

if selected_page == "Te escuchamos":
    st.subheader("¿Que frase quieres decirnos?")
    
    
    image = Image.open('emotion.jpg')
    st.image(image)
    
    stt_button = Button(label=" Graba aquí ", width=300)
    
    stt_button.js_on_event("button_click", CustomJS(code="""
        var recognition = new webkitSpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
     
        recognition.onresult = function (e) {
            var value = "";
            for (var i = e.resultIndex; i < e.results.length; ++i) {
                if (e.results[i].isFinal) {
                    value += e.results[i][0].transcript;
                }
            }
            if ( value != "") {
                document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
            }
        }
        recognition.start();
        """))
    
    result = streamlit_bokeh_events(
        stt_button,
        events="GET_TEXT",
        key="listen",
        refresh_on_update=False,
        override_height=75,
        debounce_time=0)
    
    if result:
        if "GET_TEXT" in result:
            st.write(result.get("GET_TEXT"))
        try:
            os.mkdir("temp")
        except:
            pass
            
        text = str(result.get("GET_TEXT"))
        
        def remove_files(n):
            mp3_files = glob.glob("temp/*mp3")
            if len(mp3_files) != 0:
                now = time.time()
                n_days = n * 86400
                for f in mp3_files:
                    if os.stat(f).st_mtime < now - n_days:
                        os.remove(f)
                        print("Deleted ", f)
    
        remove_files(7)

        translator = Translator()
        st.header('¿Quieres hacer un análisis de sentimiento?')
        if st.button("Analizar"):
            if text:
                translation = translator.translate(text, src="es", dest="en")
                trans_text = translation.text
                blob = TextBlob(trans_text)
                st.write('Polarity: ', round(blob.sentiment.polarity,2))
                st.write('Subjectivity: ', round(blob.sentiment.subjectivity,2))
                x=round(blob.sentiment.polarity,2)
                if x >= 0.5:
                    st.write( 'Es un sentimiento Positivo 😊')
                elif x <= -0.5:
                    st.write( 'Es un sentimiento Negativo 😔')
                else:
                    st.write( 'Es un sentimiento Neutral 😐')

elif selected_page == "Cámara":
    st.title("¿Que frase quieres fotografiar?")

    image = Image.open('photo.webp')
    st.image(image)

    img_file_buffer = st.camera_input("Toma una Foto")
    
    if img_file_buffer is not None:
        # To read image file buffer with OpenCV:
        bytes_data = img_file_buffer.getvalue()
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
            
        img_rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
        text=pytesseract.image_to_string(img_rgb)
        st.write(text)

        translator = Translator()
        st.header('¿Quieres hacer un análisis de sentimiento?')
        if st.button("Analizar"):
            if text:
                translation = translator.translate(text, src="es", dest="en")
                trans_text = translation.text
                blob = TextBlob(trans_text)
                st.write('Polarity: ', round(blob.sentiment.polarity,2))
                st.write('Subjectivity: ', round(blob.sentiment.subjectivity,2))
                x=round(blob.sentiment.polarity,2)
                if x >= 0.5:
                    st.write( 'Es un sentimiento Positivo 😊')
                elif x <= -0.5:
                    st.write( 'Es un sentimiento Negativo 😔')
                else:
                    st.write( 'Es un sentimiento Neutral 😐')

    
