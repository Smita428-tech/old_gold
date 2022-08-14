import random
import numpy as np


import nltk
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
from nltk import punkt
import json
import pickle
from keras.models import Sequential
from keras.layers import Dense,Dropout,Activation,Flatten
from tensorflow.keras.optimizers import SGD

words=[]
classes = []
documents = []
ignore_words=['?','!','.']
data_file = open('Igit_intents.json').read()
intents = json.loads(data_file)

for intent in intents['intents']:
    for pattern in intent['patterns']:
        #tokenisation
        w = nltk.word_tokenize(pattern)
        #print("TOKEN IS :{}".format(w))
        words.extend(w)
        #({'hey','you'},'greeting')
        documents.append((w,intent['tag']))
        #add to class list
        if intent['tag'] not in classes:
            classes.append(intent['tag'])

#final list
#print('words list is : {}'.format(words))
#print('Docs are : {}'.format(documents))
#print('Classes are : {}'.format(classes))

words = [lemmatizer.lemmatize(w.lower())for w in words if w not in ignore_words]
words = list(set(words))
classes = list(set(classes))

#print(words)
pickle.dump(words,open('words.pkl','wb'))
pickle.dump(classes,open('classes.pkl','wb'))

training = []
output_empty = [0]*len(classes)

for doc in documents:
    bag = []
    pattern_words = doc[0]
    pattern_words = [lemmatizer.lemmatize(word.lower()) for word in pattern_words]
    print('Pattern words: {}'.format(pattern_words))

    for w in words:
        bag.append(1) if w in pattern_words else bag.append(0)

    print('Current bag:{}'.format(bag))

    output_row = list(output_empty)
    output_row[classes.index(doc[1])] = 1
    print('Current Output : {}'.format(output_row))

    training.append([bag,output_row])

#print('Training data:{}'.format(training))
random.shuffle(training)
training = np.array(training)

train_x = list(training[:,0])
train_y = list(training[:,1])
print('x:{}'.format(train_x))
print('y:{}'.format(train_y))

model = Sequential()
model.add(Dense(128,input_shape=(len(train_x[0]),),activation = 'relu'))
model.add(Dropout(0.5))
model.add(Dense(64,activation='relu'))
model.add(Dense(len(train_y[0]),activation='softmax'))

#compile the model & optimize
sgd = SGD(learning_rate=0.01, decay=1e-6, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy',optimizer=sgd,metrics=['accuracy'])
print(type(train_x))
X = np.array(train_x)
Y = np.array(train_y)

mfit = model.fit(X,Y, epochs=200, batch_size=5, verbose=1)
model.save('chatbot_model.h5',mfit)

print('1st Chatbot model')
