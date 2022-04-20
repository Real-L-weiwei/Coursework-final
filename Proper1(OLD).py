#*Summary*

#I decided to base my coursework project on a Speech-To-Text program. 
#I have made good progress thus far, having built a model which has been trained to identify 
#words from a small set of vocabulary. I realised that for audio data to be trained, they must be 
#visualised on spectrograms, which shows the intensity of the audio file over time. 
#I used a Short-time Fourier transform on my audio data instead of the regular Fourier transform because 
#I wanted to retain all the time information. A spectrogram has been generated through this process,
#which represents audio data as image data, which made it easier for me to use a 2D 
#Convolutional Neural Network (CNN) 
#to train my dataset and treat each audio data as if they were individual pictures. 
#[CNN is better suited at training images than regular DNN - CNN can have an accuracy of 97% when classifying spoken digit sounds.] 
#During the training process, I identified the problem regarding overfitting, where the model is trained so well 
#that excessive information like noise is considered. 
#This situation truly surprised me, as I always had the belief that more accurate the data, the better – 
#an approach I used to solve underfitting, when training and validation loss both decreased after certain epochs. 
#To tackle this problem, I used a regularisation technique called dropout, and set its value of 0.5 to reduce 
#the effects of overfitting. I have deliberately chosen 0.5 because the regularisation parameter is maximum at 
#this value, thus yielding maximum regularisation. I have also realised the importance of using standardised 
#input data after undergoing this project. My model can only decode .wav files with specific dimensions. 
#I had difficulties finding files which would be able to be compared using my model.



#Importing necessary modules and dependencies for the program to run. Notably, plotting, tensorflow and tensorflow-required
#libraries are used.
import os
import pathlib

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import tensorflow as tf

from tensorflow.keras.layers.experimental import preprocessing
from tensorflow.keras import layers
from tensorflow.keras import models
from IPython import display

#Seed has been set to reflect experiment reproducability, as you want to train your model in the most similar way possible every time
seed = 42
tf.random.set_seed(seed)
np.random.seed(seed)

#Decode process normalises the values contained in the .wav file to the range [-1.0, 1.0]
def decode_audio(audio_binary):
  audio, _ = tf.audio.decode_wav(audio_binary)
  return tf.squeeze(audio, axis=-1)

#The label for each WAV file is its parent directory, so split the strings
#Easier for identification of data
def get_label(file_path):
  parts = tf.strings.split(file_path, os.path.sep)
  return parts[-2]

#This takes in the filename of the WAV file and output a tuple containing the audio and labels for training
#Previously defined functions are used here
def get_waveform_and_label(file_path):
  label = get_label(file_path)
  audio_binary = tf.io.read_file(file_path)
  waveform = decode_audio(audio_binary)
  return waveform, label

#This function transforms the waveform into a spectrogram, which analyses the intensity of sound over time.
#This has been done using Short-Time Fourier Transform, retaining the time information
#Problem relating to the 'time-frequency compromise' has been noted,
#An appropriate sample rate has been used.
#Process of zero padding adds pixels to the 'image' (spectrogram), ensuring that the output has the same shape as the input data
#Only padding for files with less than 16000 samples
#Audio data should be of the same length 
def get_spectrogram(waveform):
  zero_padding = tf.zeros([16000] - tf.shape(waveform), dtype=tf.float32)
  waveform = tf.cast(waveform, tf.float32)
  equal_length = tf.concat([waveform, zero_padding], 0)
  spectrogram = tf.signal.stft(
      equal_length, frame_length=255, frame_step=128)

  spectrogram = tf.abs(spectrogram)

  return spectrogram

#Method for plotting - defining the general axis and what information they should contain
def plot_spectrogram(spectrogram, ax):
  # Convert to frequencies to log scale and transpose so that the time is
  # represented in the x-axis (columns).
  log_spec = np.log(spectrogram.T)
  height = log_spec.shape[0]
  width = log_spec.shape[1]
  X = np.linspace(0, np.size(spectrogram), num=width, dtype=int)
  Y = range(height)
  ax.pcolormesh(X, Y, log_spec)
    
#Waveform dataset transformed to have spectrogram images and their corresponding labels as integer IDs.    
def get_spectrogram_and_label_id(audio, label):
  spectrogram = get_spectrogram(audio)
  spectrogram = tf.expand_dims(spectrogram, -1)
  label_id = tf.argmax(label == commands)
  return spectrogram, label_id

#Preprocessing is carried our on the validation and test sets.
def preprocess_dataset(files):
  files_ds = tf.data.Dataset.from_tensor_slices(files)
  output_ds = files_ds.map(get_waveform_and_label, num_parallel_calls=AUTOTUNE)
  output_ds = output_ds.map(
      get_spectrogram_and_label_id,  num_parallel_calls=AUTOTUNE)
  return output_ds


#Importing the dataset from its directory
data_dir = pathlib.Path('data/mini_speech_commands')
if not data_dir.exists():
  tf.keras.utils.get_file(
      'mini_speech_commands',
      origin="/Users/home/Documents/mini_speech_commands",
      extract=True,
      cache_dir='.', cache_subdir='data')

#Checking for information of the imported dataset by printing them out 
commands = np.array(tf.io.gfile.listdir(str(data_dir)))
commands = commands[commands != 'README.md']
print('Commands:', commands)

#Shuffling the dataset, which are audio files, after they have been extracted
#Then pring the information necessary for training
filenames = tf.io.gfile.glob(str(data_dir) + '/*/*')
filenames = tf.random.shuffle(filenames)
print(filenames)
num_samples = len(filenames)
print('Number of total examples:', num_samples)
print('Number of examples per label:',
      len(tf.io.gfile.listdir(str(data_dir/commands[0]))))
print('Example file tensor:', filenames[0])

#Split the files into training, validation and test sets using a 80:10:10 ratio. The training dataset must take
#The majority, the others are only used for checking and evaluation
train_files = filenames[:6400]
val_files = filenames[6400: 6400 + 600]
test_files = filenames[-800:]

#Print sizes to check
print('Training set size', len(train_files))
print('Validation set size', len(val_files))
print('Test set size', len(test_files))

#tf.data extracts the data
#Define file_ds and waveform_ds by manipulating the raw dataset
#Autotune dynamically tunes the buffer size
AUTOTUNE = tf.data.AUTOTUNE
files_ds = tf.data.Dataset.from_tensor_slices(train_files)
waveform_ds = files_ds.map(get_waveform_and_label, num_parallel_calls=AUTOTUNE)

#Plotting waveforms of the data onto graphs for visualisation
#I have defined to plot 9 diagrams (3x3) with 9 different pronounced words
#Methods have been used to reveal which words' waveform I have plotted
rows = 3
cols = 3
n = rows*cols
fig, axes = plt.subplots(rows, cols, figsize=(10, 12))
for i, (audio, label) in enumerate(waveform_ds.take(n)):
  r = i // cols
  c = i % cols
  ax = axes[r][c]
  ax.plot(audio.numpy())
  ax.set_yticks(np.arange(-1.2, 1.2, 0.2))
  label = label.numpy().decode('utf-8')
  ax.set_title(label)

plt.show()

#Exploring the data - The waveform, the spectrogram and an example of the audio data have been compared
#Output the information
for waveform, label in waveform_ds.take(1):
  label = label.numpy().decode('utf-8')
  spectrogram = get_spectrogram(waveform)

print('Label:', label)
print('Waveform shape:', waveform.shape)
print('Spectrogram shape:', spectrogram.shape)
print('Audio playback')
display.display(display.Audio(waveform, rate=16000))

#Plotting spectrogram and feeding in the specific information into the paramatera
#Add the information of the axis
fig, axes = plt.subplots(2, figsize=(12, 8))
timescale = np.arange(waveform.shape[0])
axes[0].plot(timescale, waveform.numpy())
axes[0].set_title('Waveform')
axes[0].set_xlim([0, 16000])
plot_spectrogram(spectrogram.numpy(), axes[1])
axes[1].set_title('Spectrogram')
plt.show()

#Spectrogram transformation
spectrogram_ds = waveform_ds.map(
    get_spectrogram_and_label_id, num_parallel_calls=AUTOTUNE)

# Outputting and displaying the spectrograms for the 9 waveforms previously outputted
#Hide the axis
rows = 3
cols = 3
n = rows*cols
fig, axes = plt.subplots(rows, cols, figsize=(10, 10))
for i, (spectrogram, label_id) in enumerate(spectrogram_ds.take(n)):
  r = i // cols
  c = i % cols
  ax = axes[r][c]
  plot_spectrogram(np.squeeze(spectrogram.numpy()), ax)
  ax.set_title(commands[label_id.numpy()])
  ax.axis('off')

plt.show()

#Defining the three datasets
train_ds = spectrogram_ds
val_ds = preprocess_dataset(val_files)
test_ds = preprocess_dataset(test_files)

#Thw training and validation sets are batched for model training.
#Batching allows many data to be trained at once and sets a 'frame' for training
batch_size = 64
train_ds = train_ds.batch(batch_size)
val_ds = val_ds.batch(batch_size)

#This reduces latency when training the model
train_ds = train_ds.cache().prefetch(AUTOTUNE)
val_ds = val_ds.cache().prefetch(AUTOTUNE)


for spectrogram, _ in spectrogram_ds.take(1):
  input_shape = spectrogram.shape
print('Input shape:', input_shape)
num_labels = len(commands)

norm_layer = preprocessing.Normalization()
norm_layer.adapt(spectrogram_ds.map(lambda x, _: x))

#*Defining the model*
# Resizing layer has been introduced to downsample the input for faster training of the model [less data]
# In the normalization layer, each pixel in the image is normalised using mathematical methods which
#determine the mean and standard deviation
#Output the summary of model afterwards
model = models.Sequential([
    layers.Input(shape=input_shape),
    preprocessing.Resizing(32, 32), 
    norm_layer,
    layers.Conv2D(32, 3, activation='relu'),
    layers.Conv2D(64, 3, activation='relu'),
    layers.MaxPooling2D(),
    layers.Dropout(0.25),
    layers.Flatten(),
    layers.Dense(128, activation='relu'),
    layers.Dropout(0.5),
    layers.Dense(num_labels),
])

model.summary()

#Adam is a replacement optimisation algorithm for stochastic gradient descent, which smoothens the curve
#By optimising an objective function using methematical iterative methods
model.compile(
    optimizer=tf.keras.optimizers.Adam(),
    loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
    metrics=['accuracy'],
)

#Setting the number of epochs - number of times trained
EPOCHS = 10
history = model.fit(
    train_ds, 
    validation_data=val_ds,  
    epochs=EPOCHS,
    callbacks=tf.keras.callbacks.EarlyStopping(verbose=1, patience=2),
)

#Plotting training and validation loss curves
#Useful for identifying underfitting
metrics = history.history
plt.plot(history.epoch, metrics['loss'], metrics['val_loss'])
plt.legend(['loss', 'val_loss'])
plt.show()

#Evlauation of the model
#Outputs the accuracy
test_audio = []
test_labels = []

for audio, label in test_ds:
  test_audio.append(audio.numpy())
  test_labels.append(label.numpy())

test_audio = np.array(test_audio)
test_labels = np.array(test_labels)

y_pred = np.argmax(model.predict(test_audio), axis=1)
y_true = test_labels

test_acc = sum(y_pred == y_true) / len(y_true)
print(f'Test set accuracy: {test_acc:.0%}')

#Using a confusion matrix to visualise how well the model has been trained
confusion_mtx = tf.math.confusion_matrix(y_true, y_pred) 
plt.figure(figsize=(10, 8))
sns.heatmap(confusion_mtx, xticklabels=commands, yticklabels=commands, 
            annot=True, fmt='g')
plt.xlabel('Prediction')
plt.ylabel('Label')
plt.show()

#Using a sample file to see how well the model can predict the word

#Output the result
#This is the *important* bit where you feed your own data into the model and see how
#well the model recognises your data

##sample_file = '/Users/home/Documents/mini_speech_commands/no/01bb6a2a_nohash_0.wav'
sample_file = '/Users/home/Documents/mini_speech_commands/me/no1c.wav'

sample_ds = preprocess_dataset([str(sample_file)])

#Displays the prediction for what the word could be according to the model, in the form of a bar chart
for spectrogram, label in sample_ds.batch(1):
  prediction = model(spectrogram)
  plt.bar(commands, tf.nn.softmax(prediction[0]))
  plt.title(f'Predictions for "{commands[label[0]]}"')
  plt.show()
