import pickle
import tkinter
from turtle import bgcolor
from tkinter import *
from PIL import Image, ImageTk
from keras.models import load_model
import nltk
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
from nltk import punkt
import json
import random
import numpy as np
import re
import webbrowser
from functools import partial
from tkHyperlinkManager import*
import pyttsx3
import speech_recognition as sr
from playsound import  playsound
import requests
import string
import lxml
import googlesearch
from lxml import html
from googlesearch import search
from bs4 import BeautifulSoup

from gtts import gTTS
from time import sleep
import os

base = Tk()
helv18 = ("Helvetica",18)
base.title("IGIT CHATBOT")

base.iconbitmap('icon.ico')
base.geometry("415x540")
base.configure(bg='light blue')
base.resizable(width=True,height=True)
img = ImageTk.PhotoImage(file="image.png")
label = Label(base, image = img)
label.pack(fill = "both", expand = "yes")
#base.attributes('-alpha',0.5)



intents = json.loads(open('Igit_intents.json').read())
model = load_model('chatbot_model.h5')
words = pickle.load(open('words.pkl','rb'))
classes= pickle.load(open('classes.pkl','rb'))

def bow(sentence):
    print('sentence',sentence)
    sentence_word = nltk.word_tokenize(sentence)
    sentence_word = [lemmatizer.lemmatize(word.lower())for word in sentence_word]
    bag = [0]*len(words)
    print(words)
    for s in sentence_word:
        for i,w in enumerate(words):
            if w == s:
                bag[i]=1
    print("bag",(np.array(bag)))
    return (np.array(bag))

def predict_class(sentence):
    sentence_bag = bow(sentence)
    res = model.predict(np.array([sentence_bag]))[0]
    #print("res ",res)
    #print("res ", enumerate(res))
    ERROR_THRESHOLD = 0.75
    for i, r in enumerate(res):
        print(i,r)
    print('---------')

    results = [[i,r] for i,r in enumerate(res) if r > ERROR_THRESHOLD]
    #print("result",results)
    #sorting by probality
    results.sort(key=lambda x: x[1],reverse=True)
    return_list = []
    for r in results:
        return_list.append({'intent':classes[r[0]],'probality':str(r[1])})
    #print("R L ",return_list)
    return return_list

def getResponse(ints):
    tag = ints[0]['intent']
    list_of_intents = intents['intents']
    for i in list_of_intents:
        if(i['tag']== tag):
            result = random.choice(i['responses'])
            break

    return result


def chatbot_query(msg,index=0):
    fallback = 'Sorry, I cannot think of a reply for that.'
    result = ''
    try:
        search_result_list = list(search(msg, tld="co.in", num=15, stop=3, pause=1))

        page = requests.get(search_result_list[index])

        tree = html.fromstring(page.content)

        soup = BeautifulSoup(page.content, features="lxml")

        article_text = ''
        article = soup.findAll('p')
        for element in article:
            article_text += '\n' + ''.join(element.findAll(text=True))
            article_text = article_text.replace('\n', '')
            first_sentence = article_text.split('.')
            first_sentence = first_sentence[0].split('?')[0]
            print(first_sentence)

            chars_without_whitespace = first_sentence.translate({ord(c): None for c in string.whitespace})

        if len(chars_without_whitespace) > 0:
            result = first_sentence
        else:
            result = fallback

        return result
    except:
        if len(result) == 0:
            result = fallback
            return result


def chatbot_response(msg):
    ints = predict_class(msg)
    #print('ints',ints)
    if ints != []:
        res = getResponse(ints)
    else:
        res = chatbot_query(msg)
    #return'static text\n\n'
    return res

def enterkey(event):
    return send()

def send():
    msg = TextEntryBox.get("1.0",'end-1c').strip()
    TextEntryBox.delete("1.0",'end')

    if msg != '':

            chatHistory.config(state=NORMAL)
            chatHistory.insert('end', '\t\tYou: ' + msg)

            res = chatbot_response(msg)

            urls = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+',res)
            if len(urls)==0:
                chatHistory.insert('end', '\n\nIGIT Bot: ' + res + '\n\n')
            else:
                url = re.search("(?P<url>https?://[^\s]+)", res).group("url")
                res1 = res.removesuffix(re.search("(?P<url>https?://[^\s]+)", res).group("url"))

                print(url)
                #chatHistory.insert('end', '\n\nIGIT Bot: ' + res + re.search("(?P<url>https?://[^\s]+)", res).group("url")+ '\n\n')
                chatHistory.insert('end','\n\nIGIT Bot: ' + res1 )
                hyperlink = HyperlinkManager(chatHistory)

                chatHistory.insert('end',url, hyperlink.add(partial(webbrowser.open, url)))
                chatHistory.insert('end','\n\n')


            chatHistory.config(state=DISABLED)
            chatHistory.yview('end')
    audio_voice(res)

        #chatHistory.place(x=6, y=58, height=50, width=376)
        #chatHistory.insert('end',"IGIT Bot: "+res)
def audio_voice(res):
    try:
        obj = gTTS(text=res, lang='en', slow=True)

        obj.save('audio.mp3')

        playsound("audio.mp3")

        del obj
    except:
        vc = pyttsx3.init()
        rate = vc.getProperty("rate")
        vc.setProperty("rate", 120)
        voices = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0"
        vc.setProperty("voice", voices)
        vc.say(res)
        vc.runAndWait()



def ClearChat():
    chatHistory.config(state=NORMAL)
    chatHistory.delete("1.0", 'end')
    chatHistory.config(state=DISABLED)

def Speak():
    chatHistory.config(state=NORMAL)
    chatHistory.insert('end', 'IGIT Bot: Listening ...\n\n')
    chatHistory.config(state=DISABLED)

    spch = sr.Recognizer()

    with sr.Microphone() as source:

        print("Listening ...")
        audio = spch.listen(source)

        try:
            text = spch.recognize_google(audio)
            TextEntryBox.insert('end',text)
            send()
            print(text)
        except:
            chatHistory.config(state=NORMAL)
            chatHistory.insert('end', '\nIGIT Bot: Sorry !! Could not understand what you told.\n')
            print("couldn't understand you")
            chatHistory.insert('end', '\n\n')
            chatHistory.config(state=DISABLED)


#chat history
scroll_bar = tkinter.Scrollbar(base,)

chatHistory = Text(base,bd=0,bg="LightSteelBlue3",font=helv18,fg='Black',yscrollcommand = scroll_bar.set ,wrap=WORD)
scroll_bar['command'] = chatHistory.yview
wt = 'HEY THERE !! how can I help u?'
chatHistory.insert('end', 'IGIT Bot: '+wt+' \n\n')

chatHistory.config(state=DISABLED)
audio_voice(wt)

SendButton = Button(base,font=helv18,text="Send !!",bg="Light Blue",activebackground="cyan",fg="Black",command=send)
TextEntryBox= Text(base,bd=0,bg="LightSteelBlue2",font=helv18,wrap=WORD)
TextEntryBox.bind("<Return>",enterkey)
ClearChatButton = Button(base,font=helv18,text="Clear Chat",bg="Light Blue",activebackground="cyan",fg="Black",command=ClearChat)
SpeakButton = Button(base,font=helv18,text="Speak",bg="Light Blue",activebackground="cyan",fg="Black",command=Speak)

chatHistory.place(x=12,y=6,height=386,width=376)
scroll_bar.place(x=393,y=5,height=386,width=20)
TextEntryBox.place(x=6,y=430,height=50,width=265)
SendButton.place(x=272,y=430,height=50,width=125)
ClearChatButton.place(x=40,y=485,height=35,width=150)
SpeakButton.place(x=200,y=485,height=35,width=150)

base.mainloop()