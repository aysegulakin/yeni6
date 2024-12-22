import asyncio
import websockets
import json

# Aktif bağlantıları tutan bir liste
connected_clients = set()

async def signaling_server(websocket, path):
    # Yeni bir bağlantı geldiğinde bu fonksiyon çalışır
    connected_clients.add(websocket)
    print(f"Yeni bağlantı: {websocket.remote_address}")

    try:
        async for message in websocket:
            data = json.loads(message)
            print(f"Mesaj alındı: {data}")

            # Mesajı diğer istemcilere ilet
            # Bu kısmı offer, answer ve iceCandidate mesajlarını yönlendirmek için genişletiyoruz.
            if 'offer' in data:
                # Offer mesajını diğer istemcilere ilet
                await broadcast_message({'offer': data['offer']}, websocket)
            elif 'answer' in data:
                # Answer mesajını diğer istemcilere ilet
                await broadcast_message({'answer': data['answer']}, websocket)
            elif 'iceCandidate' in data:
                # ICE candidate mesajını diğer istemcilere ilet
                await broadcast_message({'iceCandidate': data['iceCandidate']}, websocket)

    except websockets.ConnectionClosed as e:
        print(f"Bağlantı kapatıldı: {websocket.remote_address} ({e})")

    finally:
        connected_clients.remove(websocket)
        print(f"Bağlantı kaldırıldı: {websocket.remote_address}")

async def broadcast_message(message, sender):
    """ Mesajı, sender dışında tüm istemcilere ilet """
    for client in connected_clients:
        if client != sender:
            await client.send(json.dumps(message))

# WebSocket sunucusunu başlat
async def main():
    async with websockets.serve(signaling_server, "0.0.0.0", 8080):
        print("WebSocket sunucusu başlatıldı (Port: 8080)")
        await asyncio.Future()  # Sunucunun sonsuza kadar çalışması için

if __name__ == "__main__":
    asyncio.run(main())
