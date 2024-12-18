import socket
import json
from datetime import datetime
from pymongo import MongoClient

HOST = '0.0.0.0'
PORT = 5000

def main():
    # Підключення до MongoDB
    client = MongoClient('mongodb://mongo:27017/')
    db = client['messages_db']
    collection = db['messages']

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"Socket server running on {HOST}:{PORT}")

    while True:
        conn, addr = server_socket.accept()
        data = conn.recv(4096)
        if not data:
            conn.close()
            continue
        
        message_dict = json.loads(data.decode('utf-8'))
        # Додати дату отримання повідомлення
        message_dict['date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

        # Записати в MongoDB
        collection.insert_one(message_dict)
        conn.close()

if __name__ == '__main__':
    main()
