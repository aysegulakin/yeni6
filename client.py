import asyncio
import websockets
import json
import pyaudio
from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack
from aiortc.contrib.media import MediaPlayer, MediaRecorder
from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack, RTCIceCandidate


# WebSocket sunucusu adresi
SIGNALING_SERVER_URL = "ws://localhost:8000/ws"

# Ses ayarları
audio_format = pyaudio.paInt16
channels = 1
rate = 16000
chunk = 1024

# WebRTC bağlantısı için gerekli konfigürasyon
configuration = {
    "iceServers": [{"urls": "stun:stun.l.google.com:19302"}]
}

# RTCPeerConnection ve WebSocket bağlantısını başlat
pc = RTCPeerConnection(configuration)

# WebSocket üzerinden mesaj gönderme
async def send_message(websocket, message):
    await websocket.send(json.dumps(message))

# Gelen mesajları işleme ve WebRTC oturumu başlatma
async def signaling_handler():
    async with websockets.connect(SIGNALING_SERVER_URL) as websocket:
        print("WebSocket sunucusuna bağlandı.")
        
        # WebRTC oturumu oluştur
        @pc.on("icecandidate")
        async def on_icecandidate(event):
            if event.candidate:
                await send_message(websocket, {"ice": event.candidate.to_dict()})

        @pc.on("track")
        def on_track(track):
            print("Uzak ses akışı alındı.")
            recorder = MediaRecorder("output.wav")
            recorder.addTrack(track)
            recorder.start()

        # Teklif oluştur ve sunucuya gönder
        await start_audio_stream()
        offer = await pc.createOffer()
        await pc.setLocalDescription(offer)
        await send_message(websocket, {"sdp": pc.localDescription.to_dict()})

        # WebSocket üzerinden gelen mesajları işleyin
        async for message in websocket:
            data = json.loads(message)
            if "sdp" in data:
                await pc.setRemoteDescription(RTCSessionDescription(**data["sdp"]))
                if data["sdp"]["type"] == "offer":
                    answer = await pc.createAnswer()
                    await pc.setLocalDescription(answer)
                    await send_message(websocket, {"sdp": pc.localDescription.to_dict()})
            elif "ice" in data:
                candidate = RTCIceCandidate(**data["ice"])
                await pc.addIceCandidate(candidate)

# Ses akışını başlat
async def start_audio_stream():
    player = MediaPlayer("default")
    pc.addTrack(player.audio)

# Ana fonksiyon
async def main():
    await signaling_handler()

# Asenkron döngüyü çalıştır
asyncio.run(main())
