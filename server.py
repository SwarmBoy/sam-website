import asyncio
import websockets
import json
import sounddevice as sd
import numpy as np
import pandas as pd
import flask
from flask_cors import CORS
import threading


DEBUG = True    
MAPPING = {
    0: 0,
    1: 1,
    2: 3,
    3: 7,
    4: 6,
    5: 2
}

df = pd.DataFrame({
})

# Global variable for amplitudes
amplitude_array = [0, 0, 0, 0, 0, 0]

frequency = 170      # Frequency of the sine wave in Hz
sample_rate = 48000   # Sample rate in Hz
phase = 0.0           # Phase accumulator for the sine wave
phase_increment = (2 * np.pi * frequency) / sample_rate

def connect():
    # Attempt to find a device with at least 8 output channels
    device_id = None
    for i, device in enumerate(sd.query_devices()):
        if device['max_output_channels'] >= 8:
            device_id = i
            break
    if device_id is None:
        raise RuntimeError("No suitable output device found with at least 8 channels.")

    sd.default.device = (None, device_id)
    print(f"Selected audio output device with output channels: {sd.query_devices(device_id)['max_output_channels']}")
    print(sd.default.device)

def audio_callback(outdata, frames, time, status):
    global phase, amplitude_array

    if status:
        print("Stream status:", status)

    # Create a time index for this block
    t = (np.arange(frames) + phase) * phase_increment
    # Update phase for the next callback
    phase += frames

    # Create a multi-channel buffer initialized to zeros
    out = np.zeros((frames, sd.query_devices(sd.default.device[1])['max_output_channels']), dtype=np.float32)

    # Generate the sine wave and scale by amplitude for each channel
    sine_wave = np.sin(t)
    for i in range(len(amplitude_array)):
        out[:, MAPPING[i]] = sine_wave * amplitude_array[i]

    outdata[:] = out

async def handler(websocket):
    global amplitude_array, df
    async for message in websocket:
        data = json.loads(message)
        print("Received data:", data)
        # Update the global amplitude array
        amplitude_array = data["amplitudes"]
        timestamp = data["timestamp"]

        # Update the global dataframe
        new_data = pd.DataFrame([{
            "timestamp": timestamp,
            "amplitudes": amplitude_array
        }])
        df = pd.concat([df, new_data], ignore_index=True)
        df = df[df["timestamp"] > timestamp - 10000]


async def main():
    #launch a new thread for the HTTP server
    print("Starting Flask server on port 5000")
    threading.Thread(target=lambda: app.run(port=5000)).start()

    async with websockets.serve(handler, "localhost", 8000):
        print("WebSocket server listening on ws://localhost:8000")
        await asyncio.Future()  # run forever

app = flask.Flask(__name__)
CORS(app)

@app.route('/data', methods=['GET'])
def data():
    global df
    return df.to_json(orient='records')


if __name__ == "__main__": 
    if not DEBUG:
        connect()  
        with sd.OutputStream(samplerate=sample_rate,
                            channels=sd.query_devices(sd.default.device[1])['max_output_channels'],
                            callback=audio_callback,
                            blocksize=1024):
            asyncio.run(main())
    else:
        print("Running in debug mode. No audio output will be generated.")
        asyncio.run(main())
