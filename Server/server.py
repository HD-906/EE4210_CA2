import socket as sock
import os
import urllib.parse

HOST, PORT = '', 12000


def get_content_type(file):
    """
    Determine the content type of a file based on its extension.

    Args:
    file (str): The filename from which to extract the content type.

    Returns:
    str: A MIME type for the file.
    """
    if file.endswith('.html'):
        return 'text/html'
    elif file.endswith('.jpg'):
        return 'image/jpeg'
    elif file.endswith('.ico'):
        return 'image/x-icon'
    return 'application/octet-stream'


def handle_request(request):
    """
    Parse the HTTP request to determine the method and the requested path.

    Args:
    request (str): The raw HTTP request received from the client.

    Returns:
    tuple: Method and path requested, or None if the request is invalid.
    """
    try:
        headers = request.split('\n')
        first_line = headers[0]
        method, path, _ = first_line.split()
        path = urllib.parse.unquote(path[1:])  # remove leading '/'
        if not path:  # path is empty
            path = 'index.html'  # index.html by default
        return method, path
    except ValueError:
        # Return None if the first line is improperly formatted
        return None, None


def construct_response(path):
    """
    Create an HTTP response with appropriate headers and the requested file content, if available.

    Args:
    path (str): The path to the file being requested.

    Returns:
    bytes: The complete HTTP response to be sent to the client.
    """
    if os.path.exists(path):
        with open(path, 'rb') as file:
            body = file.read()
        header = 'HTTP/1.1 200 OK\r\n'
        content_type = get_content_type(path)
        header += f'Content-Type: {content_type}\r\n'
        header += f'Content-Length: {len(body)}\r\n'
        header += '\r\n'
    else:
        body = b'File Not Found'
        header = 'HTTP/1.1 404 Not Found\r\n'
        header += 'Content-Type: text/plain\r\n'
        header += f'Content-Length: {len(body)}\r\n'
        header += '\r\n'

    return header.encode() + body


def main():
    """
    Main function to start the server, accept connections, and handle requests.
    """
    with sock.socket(sock.AF_INET, sock.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen(2)
        print(f'Serving HTTP on port {PORT}...')

        while True:
            connection_socket, addr = server_socket.accept()  # Block and wait for connection

            with connection_socket:
                request = connection_socket.recv(1024).decode()
                if not request:
                    print("None or Empty request received")
                    continue

                print('Received request:')
                print(request)

                method, path = handle_request(request)
                if method is None:
                    connection_socket.sendall(b'HTTP/1.1 400 Bad Request\r\n\r\n')
                    continue

                if method == 'GET':
                    response = construct_response(path)
                    connection_socket.sendall(response)
                else:
                    connection_socket.sendall(b'HTTP/1.1 405 Method Not Allowed\r\n\r\n')


if __name__ == '__main__':
    main()
