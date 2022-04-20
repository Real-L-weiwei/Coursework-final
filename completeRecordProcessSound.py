import soundfile

#import sounddevice library and shortening it to sd
import sounddevice as sd
import tensorflow as tf
import tensorflow_io as tfio
import matplotlib.pyplot as plt

from pydub import AudioSegment
from scipy.io import wavfile

from scipy.io.wavfile import write


def trim_wav(originalWavPath,newWavPath,start,end):
    '''
    :param originalWavPath: the path to the source wav file
    :param newWavPath: output wav file * can be same path as original
    :param start: time in seconds
    :param end: time in seconds
    :return:
    '''
    sampleRate, waveData = wavfile.read(originalWavPath)
    startSample = int(start * sampleRate)
    endSample = int(end * sampleRate)
    wavfile.write(newWavPath, sampleRate, waveData[startSample:endSample])

def soundMain(filename):
    issue=False
    
    filename = str(filename)+".wav"
    
    #Defining sample rate = 16000 [Same value as sample files]
    fs = 16000

    #Length of recording in seconds
    time = 1

    ##filename = str(input("Input file name (with.wav ending)"))

    ##input("Press enter to start recording")
    print("Recording...")

    #My neural network model only handles one channel
    recording = sd.rec(int(time * fs), samplerate=fs, channels=1)
    sd.wait()  

    print("Recording ended")

    #Saving audio file externally
    write('temp.wav', fs, recording)  


    data, samplerate = soundfile.read('temp.wav')
    soundfile.write(filename, data, samplerate, subtype='PCM_16')

        

    audio = tfio.audio.AudioIOTensor(filename)

    #data, fs = librosa.load('1.1.wav')
    #data_tensor = tf.convert_to_tensor(data)

    audio_slice = audio[100:]
    audio_tensor = tf.squeeze(audio_slice, axis=[-1])

    tensor = tf.cast(audio_tensor, tf.float32) / 32768.0

    #plt.show()
    plt.figure()
    plt.plot(tensor.numpy())
    #Amplitude greater or less than 0.05 at the front or back end are trimmed
    position = tfio.audio.trim(tensor, axis=0, epsilon=0.05)
    print(position)

    start = position[0]
    stop = position[1]
    print(start, stop)

    start1 = (position[0].numpy())
    stop1 = (position[1].numpy())
    print(start1, stop1)

    processed = tensor[start:stop]

    print(processed)
    #plt.show()
    plt.figure()
    plt.plot(processed.numpy())

     
    wp = filename
    trim_wav(wp, wp.replace(".wav", "_trimmed.wav"), start1/16000,stop1/16000) #16000 samples = 1 second

    #If there was no trimming to the audio file, it can be assumed that the input has been way too quiet
    if start1 == 15900 and stop1 == 15900:
        issue=True
    #return this result (identification)
    return issue

    ##<---Notes--->
    ## I used AudioIOTensor to identify the data points where the audio should be trimmed from then trim_wav function to 
    ## do the actual trimming 

#soundMain()

