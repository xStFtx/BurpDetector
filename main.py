import pyaudio
import numpy as np

class BurpDetector:
    def __init__(self):
        self.burp_count = 0
        self.volume_threshold = 1000  # Set a threshold for volume to detect burps

    def is_burp(self, audio_data):
        """Basic detection logic based on volume threshold."""
        return np.max(audio_data) > self.volume_threshold

    def start_listening(self):
        """Starts listening on the microphone and detects burps."""
        # Parameters for audio stream
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        CHUNK = 1024

        # Initialize PyAudio
        audio = pyaudio.PyAudio()

        # Open stream
        stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

        try:
            print("Listening for burps...")
            while True:
                # Read audio stream
                data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)

                # Check for burp
                if self.is_burp(data):
                    self.burp_count += 1
                    print(f"Burp detected! Total count: {self.burp_count}")
        except KeyboardInterrupt:
            # Stop and close the stream and PyAudio
            print("\nStopping...")
            stream.stop_stream()
            stream.close()
            audio.terminate()
            print(f"Total number of burps detected: {self.burp_count}")

# Create a BurpDetector instance and start listening
detector = BurpDetector()
detector.start_listening()
