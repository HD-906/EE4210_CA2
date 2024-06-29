import socket as sock
import re
from urllib.parse import quote, unquote  # for URL encoding


def send_http_request(host, port, path):
    """
    Send an HTTP GET request and return the response content.

    Args:
        host (str): The server's hostname.
        port (int): The server's port number.
        path (str): The path to the resource being requested.

    Returns:
        bytes: The raw response content.
    """
    # URL-encode the path to handle spaces and other special characters
    # decode first to avoid double encoding
    path = quote(unquote(path))

    with sock.socket(sock.AF_INET, sock.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))
        request = f"GET /{path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
        client_socket.send(request.encode())

        response = bytearray()
        part = client_socket.recv(1024)
        while part:
            response.extend(part)
            part = client_socket.recv(1024)

        return response


def parse_http_response(response):
    """
    Parses the HTTP response to separate headers and body.

    Args:
        response (bytes): The raw HTTP response.

    Returns:
        tuple: headers as str, body as bytes.
    """
    headers, _, body = response.partition(b'\r\n\r\n')
    return headers.decode('windows-1252'), body


def find_jpg_links(html_content):
    """
    Parse HTML to find all .jpg image file references.

    Args:
        html_content (str): HTML content as a string.

    Returns:
        list: A list of filenames found in the HTML content.
    """
    jpg_links = re.findall(r'src="([^"]+\.jpg)"', html_content)  # finds all '.jpg' following 'src=' excluding '"'
    return jpg_links


def main():
    host = 'localhost'
    port = 12000
    path = ''  # 'index.html' by default

    # Request the base HTML file
    print("Requesting HTML file...")
    html_response_bytes = send_http_request(host, port, path)
    html_headers, html_body = parse_http_response(html_response_bytes)
    html_content = html_body.decode('windows-1252')

    # Parse the HTML to find .jpg references
    print("Parsing HTML for .jpg links...")
    jpg_links = find_jpg_links(html_content)

    # Request each .jpg file found
    for link in jpg_links:
        print(f"Requesting image file: {link}")
        image_response_bytes = send_http_request(host, port, link)
        _, image_body = parse_http_response(image_response_bytes)

        filename = link.split('/')[-1]  # Extract filename from URL
        with open(filename, 'wb') as file:
            file.write(image_body)

        print(f"Received {len(image_body)} bytes from {link}")
        if len(image_body) < 100:
            print(f'image Body: {image_body}')


if __name__ == '__main__':
    main()
