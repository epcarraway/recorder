# recorder
Python-based screen recorder

This script can be used to record screen captures from a desktop computer as well as audio from speaker outputs and microphones. It accomplishes this concurrently using separate threads and then combines the audio and video files using FFMPEG. FFMPEG is a separate application that can be found at ffmpeg.org.

This script requires pyautogui to capture screen video which are translated into numpy arrays. As an option numpy can use the cursor coordinates from pyautogui to redraw a cursor for demonstrations, as pyautogui captures a screenshot without the cursor. Pyaudio is used to capture audio from the computer and microphone as wave files and can be customized as well. Recording audio from the PC requires "Stereo Mix" to be enabled in Windows. Instructions on how to do this can be found at https://www.howtogeek.com/howto/39532/how-to-enable-stereo-mix-in-windows-7-to-record-audio/
