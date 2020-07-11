from aip import AipSpeech
import pyaudio
import pygame
import ffmpy
import time
import wave
import os


# BaiduAPI
APP_ID = '21181648'
API_KEY = 'xBiRZmyMU4WiuN8Aac0IRBXh'
SECRET_KEY = 'wv4pYcNTcEZ4aZqg1RP48XeeG612jZBz'
client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

# 语音识别
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 16000
RECORD_SECONDS = 2
WAVE_OUTPUT_FILENAME = "input.wav"

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("开始录音,请说话......")

frames = []

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

print("AI：让我听听你在说什么.....")

stream.stop_stream()
stream.close()
p.terminate()

wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()


# FFmpeg调用
ff = ffmpy.FFmpeg(
    inputs={'input.wav': None},
    outputs={'output.pcm': '-f s16le -ar 16000 -ac 1 -acodec pcm_s16le -y'}
)
ff.run()

# 创建函数 读取文件
def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

# 识别本地文件 语音转文字
result_dict = client.asr(get_file_content('output.pcm'), 'pcm', 16000, {
    'dev_pid': 1537,
})
result_list = result_dict['result']
user_PO = result_list[0]  #转换后的字符串存入PO

print("你说： %s"% user_PO)

# AI回答转语音
result  = client.synthesis(user_PO, 'zh', 1, {
    'vol': 5, 'per': 4
})
if not isinstance(result, dict):
    with open('audio.mp3', 'wb') as f:
        f.write(result)

# 自定义函数，用于播放mp3音频
def play_mp3(file):
    pygame.mixer.init()
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(1)
    pygame.mixer.music.stop()
    pygame.mixer.quit()
play_mp3('audio.mp3')
