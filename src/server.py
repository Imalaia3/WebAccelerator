"""
WebAccelerator version 0.2.1 (python3)
Author(s): Imalaia3

A Python implementation of a basic HTTP/1.1 WebServer
with limited capabilities. It currently only supports
the following parts of the HTTP/1.1 Standard. Note
that many parts of this code were not checked for
compatability across all browsers and it has been not 
checked for compliance of the HTTP/1.1 specification:
This server supports:

- Static file serving
- Dynamic content through python scripting
- Cookies (through the scripting api)
- Persistent Connections
- GZip data compression

Next Release (if released) will contain:
-Improvments on scripting api

That's it!

Note that as the license file says, all these following documents
are licenced by the GNU General Public Licence v3. More info about
the reuse and redistribution can be found at the LICENCE file.
"""
import headers
import socket,time,os
import threading
import logging
from io import BytesIO
import gzip

USE_LOCAL_FILES = True
logging.basicConfig(level=logging.DEBUG,format='[%(levelname)s] %(asctime)s: %(message)s',datefmt="%d-%m-%Y %H:%M:%S")

#FIXME: Content-Type Populated by file extension only


def _client_handler(conn,addr,pageListeners,fdir):
    conn.settimeout(1) #Too long, causes lag
    while True:
        try:     
            data = conn.recv(1024)
            if not data:
                break



            try:
                dest = headers.parse_request_header(data)[1].split(" ")[1]
                req_data = headers.parse_request_header(data)[0]
                if dest in pageListeners:
                    logging.debug(f'{dest} listener triggered.')
                    pageListeners[dest](headers.ListenerParams(
                        req_data,
                        dest,
                        None,
                        data,
                        conn
                    ))

                elif USE_LOCAL_FILES:
                    if len(dest.split(".")) == 0:
                        dest = dest + ".html"
                    elif dest == "/":
                        dest = "/index.html"
                    if os.path.isfile(fdir+dest):
                        
                        with open(fdir + dest, "rb") as fb:
                            cont = fb.read()
                            fb.close()

                        response = headers.HTTPHeader()
                        
                        if dest.split(".")[-1] not in headers.FILE_EXTENSIONS.keys():
                            logging.warning("A client requested an unsupported file type (.{}). Fallback: text/html".format(dest.split(".")[-1]))
                            response.header["Content-Type"] = headers.CONTENT_TYPES["html"]
                        else:
                            response.header["Content-Type"] = headers.CONTENT_TYPES[headers.FILE_EXTENSIONS[dest.split(".")[-1]]]
                        

                        if "Accept-Encoding" in req_data:
                            if headers.accepts_enc("gzip",req_data["Accept-Encoding"]) or headers.accepts_enc("x-gzip",req_data["Accept-Encoding"]):
                                #print(cont)
                                response.header["Content-Encoding"] = "gzip"
                                cont = gzip_bytes(cont)
                                logging.debug("Compressed file contents with gzip because the request accepts it.")


                        response.header["Connection"] = "keep-alive"
                        response.header["Content-Length"] = len(cont)
                        response.header["Date"] = time.strftime("%a, %d %b %Y %I:%M:%S %Z",time.gmtime()) #FIXME: Implement Globally
                        response.header["Expires"] = time.strftime("%a, %d %b %Y %I:%M:%S %Z",time.gmtime()) #FIXME
                        conn.sendall(response.rformatted().encode()+ cont)


                    else:
                        conn.sendall(headers.generate_code(404))


                else:
                    raise NotImplementedError


            except NotImplementedError as e:
                #FIXME: change Connection:
                logging.critical(e)
                conn.sendall(headers.generate_code(500))
        
        except socket.timeout:
            logging.debug("Client Disconnect")
            break

    conn.close()

class HTTPServer:
    def __init__(self,port=8080,ip='0.0.0.0',file_dir="www") -> None:
        self.port = port
        self.ip = ip
        self.server = None
        self.listeners = {}
        self.www_dir = file_dir

    def set_listener(self,url,method):
        self.listeners[url] = method

    def startup(self):
        self.server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        self.server.bind((self.ip,self.port))
        self.server.listen(1)
        logging.info(f"Bind on port {self.port} success.")

        ### Main Code Loop ###
        while True:
            try:
                conn,addr = self.server.accept()
                logging.info(f"Request @ {time.ctime(time.time())}")
                thread = threading.Thread(target=_client_handler, args=(conn,addr,self.listeners,self.www_dir))
                thread.start()
            except KeyboardInterrupt:
                logging.critical("Server shutting down due to KeyboardInterrupt")
                self.server.shutdown(socket.SHUT_RDWR)
                self.server.close()
                break




#FIXME: Maybe move it
"""
todo:
- Get File
- GZIP bytes
"""
def gzip_bytes(b):
    sio = BytesIO()
    with gzip.GzipFile(fileobj=sio,mode='wb') as gz:
        gz.write(b)

    return sio.getvalue()

def get_file(filename,www_dir="www/"):
    with open(www_dir+filename, 'rb') as f:
        c = f.read()
        f.close()
    return c