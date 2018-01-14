"""
 HTTP Server Shell
 Author: adi bleyer
 basic http server code
"""
import socket
import os

DEFEALT_FILE = '/index.html'
HTTP_VERSION = 'HTTP/1.1'
DEFAULT_URL = "D:\\adi\\Documents\\python\\HTTP_server\\webroot\\"
REQUEST_CODE = 'GET'
QUEUE_SIZE = 10
MOVED_REQUEST = '302 MOVED TEMPORARILY'
BAD_REQUEST = '400 BAD REQUEST'
NOT_FOUND = '404 NOT FOUND'
VALID_REQUEST = '200 OK'
UNIQUE_URI = {'/forbidden': '403 FORBIDDEN', '/moved': MOVED_REQUEST,
              '/error': '500 INTERNAL SERVER ERROR'}

IP = '0.0.0.0'
PORT = 80
MAX_PACKET = 1
IS_TIMEOUT = True  # False cancel the timeout, for telnet debug
SOCKET_TIMEOUT = 0.5
FILE_TYPES_HEADER = {'html': 'text/html;charset=utf-8', 'jpg': 'image/jpeg',
                     'css': 'text/css', 'js': 'text/javascript; charset=UTF-8',
                     'txt': 'text/plain', 'ico': "image/x-icon",
                     'gif': 'image/jpeg', 'png': 'image/png'}
END_LINE_CHAR = '\r\n'
ENF_FILED_CHAR = ' '
ENT_HTTP_CHARS = '\r\n\r\n'
TYPE_HEADER = 'Content-Type:'
LENGTH_HEADER = 'Content-Length:'
LOCATION_HEADER = 'Location:/'


def recv_http(client_socket):
    """
    recv an http request
    :client_socket: the client socket
    :return: return the http request that received from the client
    """
    request = client_socket.recv(MAX_PACKET)
    while ENT_HTTP_CHARS not in request:
        request += client_socket.recv(MAX_PACKET)
    return request


def get_file_data(file_name):
    """
    Get data from file
    :param file_name: the name of the file
    :return: the file data in a string
    """
    text = ''
    with open(file_name, 'rb') as handel:
        text += handel.read()
    return text


def handle_client_request(resource):
    """
    get the http valid request
    Check the required resource, generate proper HTTP response and send
    to client
    :param resource: the required resource
    :return: http request ready to send
    """
    data = ""
    http_header = HTTP_VERSION + ENF_FILED_CHAR
    is_valid, path = resource
    if not is_valid:
        http_header += path + END_LINE_CHAR
    else:
        file_type = path.split('.')[-1]
        http_header += VALID_REQUEST + END_LINE_CHAR
        http_header += TYPE_HEADER + FILE_TYPES_HEADER.get(file_type)
        http_header += END_LINE_CHAR
        data = get_file_data(resource[1])
        http_header += LENGTH_HEADER + str(len(data))
    http_header += ENT_HTTP_CHARS
    http_response = http_header + data
    return http_response


def valid_URI(uri):
    """
    check if the uri is valid and change the uri to legal path
    :uri: the URI
    :return: tuple of (TRUE/FALSE,path/error type)
    """
    if uri == '/':
        return True, DEFAULT_URL + DEFEALT_FILE[1:]
    elif uri in UNIQUE_URI:
        return False, UNIQUE_URI.get(uri)
    else:
        uri = uri.replace('/', '\\')
        return True, DEFAULT_URL + uri[1:]


def validate_http_request(request):
    """
    Check if request is a valid HTTP request and returns TRUE / FALSE and
    the extra data
    :param request: the request which was received from the client
    :return: a tuple of (True/False - depending if the request is valid,
    the requested resource ).
    if true add to the requested resource a path to the wanted file.
    """
    fileds = request.split(END_LINE_CHAR)
    fileds[0] = fileds[0].split(ENF_FILED_CHAR)
    request_line = fileds[0][:]
    is_valid, path = valid_URI(request_line[1])
    if not is_valid:
        return False, path
    elif not fileds.pop() == '':
        return False, BAD_REQUEST
    elif not request_line[0] == REQUEST_CODE:
        return False, BAD_REQUEST
    elif not os.path.isfile(path):
        return False, NOT_FOUND
    elif not request_line[2] == HTTP_VERSION:
        return False, BAD_REQUEST
    else:
        return True, (VALID_REQUEST, path)


def handle_client(client_socket):
    """
    Handles client requests: verifies client's requests are legal HTTP, calls
    function to handle the requests
    :param client_socket: the socket for the communication with the client
    :return: None
    """
    print 'Client connected'
    while True:
        request = recv_http(client_socket)
        valid_http, resource = validate_http_request(request)
        if valid_http:
            print 'Got a valid HTTP request'
            http_response = handle_client_request(resource)
            err = client_socket.sendall(http_response)
            if err is not None:
                print 'err:'+err
        else:
            print 'Error: Not a valid HTTP request'
            http_response = HTTP_VERSION + ENF_FILED_CHAR + resource
            http_response += END_LINE_CHAR
            if resource == MOVED_REQUEST:
                http_response += LOCATION_HEADER
            http_response += END_LINE_CHAR
            client_socket.sendall(http_response)
    print 'Closing connection'


def main():
    # Open a socket and loop forever while waiting for clients
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((IP, PORT))
        server_socket.listen(QUEUE_SIZE)
        print "Listening for connections on port %d" % PORT

        while True:
            client_socket, client_address = server_socket.accept()
            try:
                print 'New connection received'
                if IS_TIMEOUT:
                    client_socket.settimeout(SOCKET_TIMEOUT)
                handle_client(client_socket)
            except socket.error as err:
                print 'received socket exception - ' + str(err)
            finally:
                client_socket.close()
    except socket.error as err:
        print 'received socket exception - ' + str(err)
    finally:
        server_socket.close()


if __name__ == "__main__":
    assert validate_http_request('GET / HTTP/1.1\r\n\r\n')[0]
    assert not validate_http_request('GEV / HTTP/1.2\r\n\r\n')[0]
    assert not validate_http_request('GET /vv HTTP/1.1\r\n\r\n')[0]
    assert validate_http_request('GET /css\\doremon.css HTTP/1.1'
                                 '\r\nUpgrade-Insecure-Requests: 1\r\n\r\n')[0]
    main()
