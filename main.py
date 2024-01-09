from pydub import AudioSegment
import numpy as np
import scipy.fftpack
import datetime
import pyaudio

class BurpDetector:
    def __init__(self, volume_threshold=1000, frequency_range=(100, 3000)):
        self.burp_count = 0
        self.volume_threshold = volume_threshold
        self.frequency_range = frequency_range

    def is_burp(self, audio_data):
        audio_data = audio_data.astype(np.float32)

        # RMS Volume Calculation
        rms_volume = np.sqrt(np.mean(audio_data**2))

        # FFT and Frequency Analysis
        freq_data = scipy.fftpack.fft(audio_data)
        freqs = scipy.fftpack.fftfreq(len(freq_data)) * 44100
        freq_data_abs = np.abs(freq_data)
        freq_distribution = np.sum(freq_data_abs[(freqs >= self.frequency_range[0]) & (freqs <= self.frequency_range[1])])

        # Define these thresholds based on testing and analysis
        some_threshold = 500  # Example value
        min_duration = 0.1   # Example value, in seconds
        max_duration = 1.0   # Example value, in seconds

        is_burp_freq = freq_distribution > some_threshold
        duration = len(audio_data) / 44100  # Assuming 44100 Hz sampling rate
        is_correct_duration = min_duration <= duration <= max_duration

        return rms_volume > self.volume_threshold and is_burp_freq and is_correct_duration

    
    def log_burp(self):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("burp_log.txt", "a") as file:
            file.write(f"Burp detected at {timestamp}, Total count: {self.burp_count}\n")

    def process_audio_data(self, audio_data):
        try:
            if self.is_burp(audio_data):
                self.burp_count += 1
                self.log_burp()
                print(f"Burp detected! Total count: {self.burp_count}")
        except ValueError as e:
            print(e)

    def start_listening(self):
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        CHUNK = 1024

        audio = pyaudio.PyAudio()
        stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

        try:
            print("Listening for burps...")
            while True:
                data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
                self.process_audio_data(data)
        except KeyboardInterrupt:
            print("\nStopping...")
            stream.stop_stream()
            stream.close()
            audio.terminate()
            print(f"Total number of burps detected: {self.burp_count}")
        except Exception as e:
            print(f"An error occurred: {e}")

    def process_file(self, file_path):
        try:
            audio = AudioSegment.from_mp3(file_path)
            audio = audio.set_channels(1).set_frame_rate(44100).set_sample_width(2)
            audio_data = np.array(audio.get_array_of_samples())
            chunk_size = 1024

            for i in range(0, len(audio_data), chunk_size):
                chunk_data = audio_data[i:i+chunk_size]
                if len(chunk_data) == chunk_size:
                    self.process_audio_data(chunk_data)
        except Exception as e:
            print(f"Error processing file: {e}")

# Usage
detector = BurpDetector()
detector.process_file("burp.mp3")
detector.start_listening() 