"""
 HTTP Server Shell
 Author: adi bleyer
 basic http server code
"""
import socket
import os

DEFEALT_FILE = '/index.html'
HTTP_VERSION = 'HTTP/1.1'
DEFAULT_URL = "webroot\\"
REQUEST_CODE = ['GET', 'POST']
GET, POST = REQUEST_CODE
QUEUE_SIZE = 10
MOVED_REQUEST = '302 MOVED TEMPORARILY'
BAD_REQUEST = '400 BAD REQUEST'
NOT_FOUND = '404 NOT FOUND'
VALID_REQUEST = '200 OK'
VALID_PARAM_REQUESTS = ['/calculate-next', '/calculate-area', '/upload']
UNIQUE_URI = {'/forbidden': '403 FORBIDDEN', '/moved': MOVED_REQUEST, '/image': VALID_REQUEST,
              '/error': '500 INTERNAL SERVER ERROR', '/calculate-next': VALID_REQUEST,
              '/calculate-area': VALID_REQUEST, VALID_PARAM_REQUESTS[2]: VALID_REQUEST}

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
END_FILED_CHAR = ' '
ENT_HTTP_CHARS = '\r\n\r\n'
TYPE_HEADER = 'Content-Type:'
LENGTH_HEADER = 'Content-Length:'
LOCATION_HEADER = 'Location:/'

VALID_PARAMS = {'/calculate-next': ['num'], '/calculate-area': ['height', 'width'], '/image': ['image-name']}
UPLOED_URI = 'upload\\'

def get_data(lengh, client_socket):
    """

    :param lengh: the data lengh
    :param client_socket: the socket to get the data from
    :return: the data
    """
    data = client_socket.recv(lengh)
    while len(data) < lengh:
        data += client_socket.recv(1)
    return data


def handel_post(request, client_socket):
    """
    hendel the POST request
    :request: the client request, full and unsplied
    :return: return the responce of False if the request not valid
    """
    length = None
    lines = request.split(END_LINE_CHAR)
    data_start = request.find(ENT_HTTP_CHARS)
    for line in request.split('\r\n'):
        if line.count(':') == 1:
            name, data = line.split(':')
            if name == LENGTH_HEADER[:-1]:
                length = data
    data_end = len(request)
    data_len = int(length)-(data_end-data_start)
    if data_len <= 0:
        return False
    data = get_data(data_len, client_socket)
    uri, param = lines[0].split(' ')[1].split('?')
    param = param.split('=')
    print param
    if not uri == VALID_PARAM_REQUESTS[2]:
        return False
    with open(DEFAULT_URL + UPLOED_URI + param[1], 'wb') as hendel:
        hendel.write(data)
    return VALID_REQUEST





def handel_params(url):
    """
    handel all the params
    :url: the request valid url
    :return: (false/data) if it is nt valid return flse
     and if it is return the number to send(return string)
    """
    print url
    uri, params = url
    params = params.split('&')
    fileds = []
    for param in params:
        fileds.append(param.split("="))
    if not VALID_PARAMS.has_key(uri):
        return False
    for param, filed in zip(VALID_PARAMS.get(uri), fileds):
        if not param == filed[0]:
            return False
    if uri == VALID_PARAM_REQUESTS[0]:
        for filed in fileds:
            if not filed[1].isdigit():
                return False
        return str(int(fileds[0][1])+1)
    elif uri == VALID_PARAM_REQUESTS[1]:
        for filed in fileds:
            if not filed[1].isdigit():
                return False
        return str(float(fileds[0][1]) * float(fileds[1][1])/2)
    elif uri == '/image':
        file_name = DEFAULT_URL + UPLOED_URI + fileds[0][1]
        print file_name
        if not os.path.isfile(file_name):
            return False
        return get_file_data(file_name)
    else:
        return False




def recv_http(client_socket):
    """
    need cange
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


def handel_file_sent(resource):
    """
    get the http valid request
    Check the required resource, generate proper HTTP response and send
    to client
    :param resource: the required resource
    :return: http request ready to send
    """
    data = ""
    http_header = HTTP_VERSION + END_FILED_CHAR
    path = resource
    file_type = path.split('.')[-1]
    http_header += VALID_REQUEST + END_LINE_CHAR
    http_header += TYPE_HEADER + FILE_TYPES_HEADER.get(file_type)
    http_header += END_LINE_CHAR
    data = get_file_data(resource)
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
        return True, UNIQUE_URI.get(uri)
    else:
        uri = uri.replace('/', '\\')
        if os.path.isfile(DEFAULT_URL + uri):
            return True, DEFAULT_URL + uri[1:]
        else:
            return False, NOT_FOUND


def read_request(request):
    """
    Check if request is a valid HTTP request and returns TRUE / FALSE
    :param request: the request which was received from the client
    :return:True/False
    """
    if END_LINE_CHAR not in request or END_FILED_CHAR not in request:
        return False
    fileds = request.split(END_LINE_CHAR)
    fileds[0] = fileds[0].split(END_FILED_CHAR)
    request_line = fileds[0][:]
    print request_line
    if not len(request_line) == 3:
        return False
    elif not fileds.pop() == '':
        return False
    elif not request_line[0] in REQUEST_CODE:
        return False
    elif not request_line[2] == HTTP_VERSION:
        return False
    for line in fileds:
        if line.count(':') == 1:
            name, data = line.split(':')
            data = data.replace(' ','')
            if name == LENGTH_HEADER[:-1]:
                if not data.isdigit():
                    return False
            if name == TYPE_HEADER[:-1]:
                print str(FILE_TYPES_HEADER.values())
                if data not in FILE_TYPES_HEADER.values():
                    print 'not type'
                    print data
                    return False
    return True


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
        print request
        is_valid = read_request(request)
        if is_valid:
            url = request.split('\r\n')[0].split(' ')[1]
            if '?' in url:
                url = url.split('?')
                uri = url[0]
            else:
                uri = url
            is_valid_uri, resource = valid_URI(uri)
        else:
            is_valid_uri = False
            resource = BAD_REQUEST
        if is_valid and is_valid_uri:
            print 'Got a valid HTTP request'
            if request.split('\r\n')[0].split(' ')[0] == 'POST':
                data = handel_post(request, client_socket)
                if data is False:
                    http_response = HTTP_VERSION + END_FILED_CHAR + BAD_REQUEST + END_LINE_CHAR
                    http_response += END_FILED_CHAR
                else:
                    http_response = HTTP_VERSION + END_FILED_CHAR + VALID_REQUEST + END_LINE_CHAR
                    http_response += TYPE_HEADER + 'text/plain' + END_LINE_CHAR

                    http_response += LENGTH_HEADER + str(len(data)) +END_LINE_CHAR
                    http_response += END_LINE_CHAR
                    http_response += data

            elif resource == MOVED_REQUEST:
                http_response = HTTP_VERSION + END_FILED_CHAR + resource + END_LINE_CHAR
                http_response += LOCATION_HEADER + END_LINE_CHAR
                http_response += END_FILED_CHAR
            elif len(url) == 2:
                data = handel_params(url)
                print data
                if data is False:
                    http_response = HTTP_VERSION + END_FILED_CHAR + BAD_REQUEST + END_LINE_CHAR
                    http_response += LOCATION_HEADER + END_LINE_CHAR
                    http_response += END_FILED_CHAR
                else:
                    http_response = HTTP_VERSION + END_FILED_CHAR + VALID_REQUEST + END_LINE_CHAR
                    http_response += TYPE_HEADER + 'text/plain' + END_LINE_CHAR

                    http_response += LENGTH_HEADER + str(len(data)) +END_LINE_CHAR
                    http_response += END_LINE_CHAR
                    http_response += data
            elif os.path.isfile(resource):
                http_response = handel_file_sent(resource)
            else:
                http_response = HTTP_VERSION + END_FILED_CHAR + resource
                http_response += END_LINE_CHAR
                http_response += END_LINE_CHAR
        else:

            print 'Error: Not a valid HTTP request'
            http_response = HTTP_VERSION + END_FILED_CHAR
            if is_valid:
                http_response += NOT_FOUND
            else:
                http_response += BAD_REQUEST
            http_response += END_LINE_CHAR
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
    assert read_request('GET / HTTP/1.1\r\n\r\n')
    assert not read_request('GEV / HTTP/1.2\r\n\r\n')
    assert not valid_URI('/vv')[0]
    assert read_request('GET /css\\doremon.css HTTP/1.1\r\nUpgrade-Insecure-Requests: 1\r\n\r\n')
    main()
