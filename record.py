# Import modules
import logging
import time
import concurrent.futures
import cv2
import numpy as np
import pyautogui
import pyaudio
import wave
import subprocess

# Set screen dimensions, framerate and duration
REGION = (100, 100, 1800, 900)
SCREEN_SIZE = (REGION[2], REGION[3])
FPS = 20
DURATION = 3600
SHOW_CURSOR = True
CURSOR_SIZE = 5
SHOW_FRAME = False
VIDEO_FILE_NAME = 'output.avi'
SHOW_RATE = False

# Set output audio file parameters
AUDIO_FILE_NAME = "output.wav"
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
SAMPLE_RATE = 44100
RECORD_SPEAKER = True
RECORD_MICROPHONE = True

# Set output combined file name
OUTPUT_FILE_NAME = 'output.mp4'

def record_speaker_audio(AUDIO_FILE_NAME="output.wav", p=pyaudio.PyAudio()):
    '''This function records the audio that would normally be output to computer speakers'''
    # Initialize PyAudio object and open stream
    logging.info("speaker %s: starting", AUDIO_FILE_NAME)
    for i1 in range(p.get_device_count()):
        dev1 = p.get_device_info_by_index(i1)
        if (dev1['name'] == 'Stereo Mix (Realtek(R) Audio)' and dev1['hostApi'] == 0):
            dev_index1 = dev1['index'];
            print(dev1)
            print('dev_index', dev_index1)
    stream1 = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=SAMPLE_RATE,
                    input=True,
                    input_device_index = dev_index1,
                    frames_per_buffer=CHUNK)
    frames1 = []
    print("Recording...")
    for i1 in range(int(44100 / CHUNK * DURATION)):
        data1 = stream1.read(CHUNK)
        frames1.append(data1)
    print("Finished recording.")
    stream1.stop_stream()
    stream1.close()
    # Save audio file
    if RECORD_SPEAKER and RECORD_MICROPHONE:
        fname_a = AUDIO_FILE_NAME.split('.')[0] + '_a.' + AUDIO_FILE_NAME.split('.')[1]
    else:
        fname_a = AUDIO_FILE_NAME
    wf1 = wave.open(fname_a, "wb")
    wf1.setnchannels(CHANNELS)
    wf1.setsampwidth(p.get_sample_size(FORMAT))
    wf1.setframerate(SAMPLE_RATE)
    wf1.writeframes(b"".join(frames1))
    wf1.close()


def record_microphone_audio(AUDIO_FILE_NAME="output.wav", p=pyaudio.PyAudio()):
    '''This function records audio from the microphone using PyAudio'''
    # Initialize PyAudio object and open stream
    logging.info("mic %s: starting", AUDIO_FILE_NAME)
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=SAMPLE_RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    frames = []
    print("Recording...")
    for i in range(int(44100 / CHUNK * DURATION)):
        data = stream.read(CHUNK)
        frames.append(data)
    print("Finished recording.")
    stream.stop_stream()
    stream.close()
    # Save audio file
    if RECORD_SPEAKER and RECORD_MICROPHONE:
        fname_b = AUDIO_FILE_NAME.split('.')[0] + '_b.' + AUDIO_FILE_NAME.split('.')[1]
    else:
        fname_b = AUDIO_FILE_NAME
    wf = wave.open(fname_b, "wb")
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(b"".join(frames))
    wf.close()


def record_screen_video(VIDEO_FILE_NAME = 'output.avi'):
    '''This function records the video from the screen using autopygui.'''
    # Define the codec and create video write object
    if VIDEO_FILE_NAME[-4:] == '.avi':
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
    elif VIDEO_FILE_NAME[-4:] == '.mp4':
        fourcc = cv2.VideoWriter_fourcc(*'MP4V')
    else:
        print(VIDEO_FILE_NAME[-4:] + ' not valid...')
        exit
    out = cv2.VideoWriter(VIDEO_FILE_NAME, fourcc, FPS, SCREEN_SIZE)
    # Start time and frame counters to keep recording in sync
    start = time.time()
    now = time.time()
    frames = 0
    repeat_frames = 0
    while time.time() - start < DURATION:
        if time.time() - now >= 1/FPS:
            now = time.time()
            # Make screenshot frame
            frame = cv2.cvtColor(np.array(pyautogui.screenshot(region=REGION)), cv2.COLOR_BGR2RGB)
            if SHOW_CURSOR:
                # Get mouse coords
                (x, y) = pyautogui.position()
                # Draw cursor highlight on screen frame
                for xx in range(-CURSOR_SIZE, CURSOR_SIZE + 1):
                    for yy in range(-CURSOR_SIZE, CURSOR_SIZE + 1):
                        try:
                            if abs(yy) >= int(CURSOR_SIZE * .75) or abs(xx) >= int(CURSOR_SIZE * .75):
                                frame[y+yy-REGION[1], x+xx-REGION[0]] = np.array([0,0,0])
                            else:
                                frame[y+yy-REGION[1], x+xx-REGION[0]] = np.array([255,255,255])
                        except Exception:
                            pass
            # Write frame until in caught up with output FPS
            repeat_frames += -1
            while frames/(now - start) < FPS:
                out.write(frame)
                frames += 1
                repeat_frames += 1
                if SHOW_RATE:
                    print('{} seconds elapsed. {} FPS ({} actual)'.format(
                        round(now - start,2), 
                        round(frames/(now - start),2), 
                        round((frames-repeat_frames)/(now - start),2)))
    out.release()


def thread_function(name):
    '''This function asigns a specific function to each thread such as recording video or audio'''
    logging.info("Thread %s: starting", name)
    try:
        if name == 0:
            print('Recording screen video')
            record_screen_video(VIDEO_FILE_NAME)
        elif (name == 1) and RECORD_SPEAKER:
                print('Recording speaker audio')
                record_speaker_audio(AUDIO_FILE_NAME, p)
        elif (name == 2) and RECORD_MICROPHONE:
                print('Recording microphone audio')
                record_microphone_audio(AUDIO_FILE_NAME, p)
    except Exception as e:
        print('error...', flush=True)
        print(e, flush=True)
        exit
    logging.info("Thread %s: finishing", name)


if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    p = pyaudio.PyAudio()
    future_list = []
    # Map thread function to each concurrent thread
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        future = executor.map(thread_function, range(3))
        future_list.append(future)
    
    # Execute and show thread output, including errors
    for future in future_list:
        try:
            print(future.result())
        except Exception as e:
            print(e)
    
    p.terminate()
    time.sleep(2)
    print('Combining audio and video files...')
    # If speaker and microphone are recorded, combine wave files first
    if RECORD_SPEAKER and RECORD_MICROPHONE:
        fname_a = AUDIO_FILE_NAME.split('.')[0] + '_a.' + AUDIO_FILE_NAME.split('.')[1]
        fname_b = AUDIO_FILE_NAME.split('.')[0] + '_b.' + AUDIO_FILE_NAME.split('.')[1]
        subprocess.call(
            "ffmpeg -i %s -i %s -filter_complex amix=inputs=2:duration=first:dropout_transition=0 -y %s" % 
            (fname_a, fname_b, AUDIO_FILE_NAME),
            shell=True)
        time.sleep(2)
    # Combine audio wave file with video file
    subprocess.call(
        'ffmpeg -i %s -i %s -c:v copy -c:a aac -y %s' % (VIDEO_FILE_NAME, AUDIO_FILE_NAME, OUTPUT_FILE_NAME),
        shell=True)
    print('All processes finished...')
