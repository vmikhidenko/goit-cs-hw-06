import socket
import os
import json

HOST = '0.0.0.0'
PORT = 3000

def handle_client_connection(client_socket):
    request_data = client_socket.recv(2048).decode('utf-8', errors='replace')
    lines = request_data.split('\r\n')
    if len(lines) > 0 and ' ' in lines[0]:
        method, path, _ = lines[0].split(' ')
    else:
        method = 'GET'
        path = '/'

    if method == 'GET':
        if path == '/':
            response = serve_file('templates/index.html', 'text/html')
        elif path == '/message.html':
            response = serve_file('templates/message.html', 'text/html')
        elif path == '/style.css':
            response = serve_file('static/style.css', 'text/css')
        elif path == '/logo.png':
            response = serve_file('static/logo.png', 'image/png', binary=True)
        else:
            response = serve_file('templates/error.html', 'text/html', status_code='404 Not Found')
    elif method == 'POST' and path == '/message':
        # Зчитуємо заголовки
        content_length = 0
        for line in lines:
            if line.startswith('Content-Length:'):
                content_length = int(line.split(': ')[1])
                break
        
        # Витягуємо body (дані форми)
        # body відокремлюється від заголовків порожнім рядком \r\n\r\n
        if '\r\n\r\n' in request_data:
            body = request_data.split('\r\n\r\n', 1)[1]
        else:
            body = ''

        # Якщо body могло бути не повністю прочитано
        # можна в разі потреби дочитати:
        body_bytes_read = len(body.encode('utf-8'))
        if body_bytes_read < content_length:
            body += client_socket.recv(content_length - body_bytes_read).decode('utf-8', errors='replace')

        data_dict = parse_form_data(body)
        # Надсилаємо дані на socket-сервер
        send_to_socket_server(data_dict)

        # Повертаємо відповідь
        response = http_response("<h1>Message received!</h1><a href='/'>Go back</a>", 'text/html')
    else:
        response = serve_file('templates/error.html', 'text/html', status_code='404 Not Found')

    client_socket.sendall(response)
    client_socket.close()


def serve_file(filepath, content_type, status_code='200 OK', binary=False):
    if not os.path.exists(filepath):
        return http_response("<h1>404 Not Found</h1>", 'text/html', '404 Not Found')
    mode = 'rb' if binary else 'r'
    with open(filepath, mode) as f:
        data = f.read()
    return http_response(data, content_type, status_code, binary=binary)


def http_response(body, content_type, status_code='200 OK', binary=False):
    if binary:
        header = f"HTTP/1.1 {status_code}\r\nContent-Type: {content_type}\r\n\r\n"
        if isinstance(body, str):
            body = body.encode('utf-8')
        return header.encode('utf-8') + body
    else:
        return f"HTTP/1.1 {status_code}\r\nContent-Type: {content_type}\r\n\r\n{body}".encode('utf-8')


def parse_form_data(body):
    # form-data: username=...&message=...
    pairs = body.split('&')
    data_dict = {}
    for pair in pairs:
        if '=' in pair:
            key, value = pair.split('=', 1)
            # Декодуємо URL-енкодінг
            key = decode_url(key)
            value = decode_url(value)
            data_dict[key] = value
    return data_dict


def decode_url(value):
    # Спрощене декодування, якщо потрібно - можна використати urllib.parse.unquote
    return value.replace('+', ' ')


def send_to_socket_server(data):
    # Надсилаємо дані через TCP на socket-сервер
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Оскільки socket_server запускається в тому ж контейнері, використаємо localhost
    sock.connect(('localhost', 5000))
    sock.sendall(json.dumps(data).encode('utf-8'))
    sock.close()


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"HTTP server running on {HOST}:{PORT}")
    while True:
        client_sock, address = server_socket.accept()
        handle_client_connection(client_sock)


if __name__ == '__main__':
    main()
