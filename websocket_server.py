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
            for client in connected_clients:
                if client != websocket:
                    await client.send(json.dumps(data))

    except websockets.ConnectionClosed as e:
        print(f"Bağlantı kapatıldı: {websocket.remote_address} ({e})")

    finally:
        connected_clients.remove(websocket)
        print(f"Bağlantı kaldırıldı: {websocket.remote_address}")

# WebSocket sunucusunu başlat
async def main():
    async with websockets.serve(signaling_server, "0.0.0.0", 8080):
        print("WebSocket sunucusu başlatıldı (Port: 8080)")
        await asyncio.Future()  # Sunucunun sonsuza kadar çalışması için

if __name__ == "__main__":
    asyncio.run(main())

