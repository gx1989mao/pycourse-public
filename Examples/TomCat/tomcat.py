
import wave
import time
import datetime
import numpy as np
import pyaudio
from subprocess import Popen, PIPE


def Monitor():
    CHUNK = 4096 #录音时每次采集的帧数
    FORMAT = pyaudio.paInt16 #采样位数
    CHANNELS = 2 #通道数
    RATE = 48000 #采样率
    THRESHOLD = 3600 #录音阈值

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("开始缓存录音")
    print('当前阈值：',THRESHOLD)
    frames = []
    recording=False
    nowavenum=0
 
    while (True):
        # 检测是否有声音
        if recording==False:
            print('检测中... ')
            # 采集小段声音
            frames=[]
            for i in range(0, 4):
                data = stream.read(CHUNK,exception_on_overflow=False)
                frames.append(data)

            audio_data = np.fromstring(b''.join(frames), dtype = np.int16)
            large_sample_count = np.sum( audio_data >= THRESHOLD/3 )

            # 如果有符合条件的声音，则开始录制
            # temp = np.max(audio_data)
            # if temp > THRESHOLD :
            if large_sample_count >= THRESHOLD*1.8:
                print("检测到信号")
                recording=True
        else:
            while True:
                print("持续录音中...")
                subframes=[]
                for i in range(0, 5):
                    data = stream.read(CHUNK,exception_on_overflow=False)
                    subframes.append(data)
                    frames.append(data)

                audio_data = np.fromstring(b''.join(subframes), dtype=np.int16)
                temp = np.max(audio_data)
                if temp <= THRESHOLD*0.8:
                    nowavenum+=1
                else:
                    nowavenum=0

                if nowavenum>=1:
                    print("等待超时，开始保存")

                    j=1
                    while j>0:
                        frames.pop()
                        j-=1

                    # 保存声音文件
                    orignalWave= datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')+'.wav'  
                    wf = wave.open(orignalWave, 'wb')
                    wf.setnchannels(CHANNELS)
                    wf.setsampwidth(p.get_sample_size(FORMAT))
                    wf.setframerate(RATE)
                    wf.writeframes(b''.join(frames))
                    wf.close()

                    # 清理声音缓存
                    nowavenum=0
                    frames=[]
                    recording=False

                    # 变声
                    print("开始变声")
                    popen = Popen("soundstretch "+orignalWave+" output.wav -rate=+45 -pitch=+3", shell=True, stdout=PIPE, stderr=PIPE)  
                    popen.wait()  
                    if popen.returncode != 0:  
                        print("Error.")

                    # 播放
                    print("开始播放")
                    playAudio('output.wav')
                    break

    stream.stop_stream()
    stream.close()
    p.terminate()

def playAudio(filename):
        # 定义数据流块
    CHUNK = 1024

    # 只读方式打开wav文件
    wf = wave.open(filename, 'rb')

    play = pyaudio.PyAudio()

    # 打开数据流
    stream = play.open(format=play.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    # 读取数据
    data = wf.readframes(CHUNK)

    # 播放  
    while data!= b'':
        stream.write(data)
        data = wf.readframes(CHUNK)

    # 停止数据流  
    stream.stop_stream()
    stream.close()

    # 关闭 PyAudio  
    play.terminate()  
    return

if __name__ == '__main__':
    Monitor()