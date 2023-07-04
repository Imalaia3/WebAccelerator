VERSION = 'HTTP/1.1'
SERVER_STRING = "WebAccelerator/0.2.1"

#FIXME: Add to docs
_PORT = 0
_IP = ''

#Most Common Return Codes
RETURN_CODES = {
    200:"OK",
    404:"Not Found",
    301:"Moved Permanently",
    500:"Internal Server Error",
    307:"Temporary Redirect",
    403:"Forbidden",
    401:"Unauthorized",
    204:"No Content"
}

#Most Common Content-Types
CONTENT_TYPES = {
    "plain":"text/plain",
    "html":"text/html",
    "css":"text/css",
    "png":"image/png",
    "jpeg":"image/jpeg",
    "gif":"image/gif",
    "mpeg":"audio/mpeg",
    "js":"application/javascript",
    "json":"application/json",
    "pdf":"application/pdf",
    "xml":"application/xml",
    "webp":"image/webp",
    "icon": "image/x-icon",
    "mp4":"video/mp4"
}

#extensions to CONTENT_TYPES
FILE_EXTENSIONS = {
    "jpeg": "jpeg",
    "jpg": "jpeg",
    "html": "html",
    "css": "css",
    "js": "js",
    "mp3": "mpeg",
    "json": "json",
    "pdf": "pdf",
    "png": "png",
    "webp": "webp",
    "ico":"icon",
    "mp4": "mp4"
}

class HTTPHeader:
    def __init__(self) -> None:
        self.header = {
            "Server":"WebAccelerator",
            "Content-Type":'',
            "Content-Length": 0,
            "Connection": '',
            "Date": ''
}
        self.return_code = 200
        self.cookies = ""

    def rformatted(self):
        """Return This Header As A String Without A Return Code"""
        out = "{} {} {}\r\n".format(VERSION,self.return_code,RETURN_CODES[self.return_code]) 
        for item in self.header:
            out += item + ": " + str(self.header[item]) + "\r\n"

        return out + self.cookies + "\r\n"

    def set_redirect(self, to_url):
        self.return_code = 307 #Temp redirect
        self.header["Location"] = to_url
    

class ListenerParams:
    def __init__(self,header_keys, raw_dest,vals,raw_data,connection) -> None:
        self.header = header_keys
        self.dest = raw_dest
        self.variables = vals
        self.raw_data = raw_data
        self.conn = connection


def parse_request_header(data):
    clientHeader = {}
    destination = data.split(b'\r\n')[0].decode()
    for entry in data.split(b'\r\n')[1:]:
        if entry == b'':
            break
        clientHeader[entry.decode().split(":")[0]] = entry.decode().split(":")[1]

    return clientHeader,destination



def generate_code(code):
    code_str = RETURN_CODES[code]
    content=f"""<!DOCTYPE html>
<html>
    <head><title>{code} {code_str}</title></head>
    <body>
        <h1>Error {code} {code_str}</h1>
        <address>{SERVER_STRING} running on {_IP}:{_PORT}</address>
    </body>
</html>
"""
    header = HTTPHeader()
    header.header["Content-Type"] = "text/html"
    header.header["Content-Length"] = len(content)
    header.header["Connection"] = "keep-alive"
    return VERSION.encode() + f" {code} {RETURN_CODES[code]}\r\n{header.rformatted()}{content}".encode()



def cookie(name:str,value:str,max_age=60,SameSite="Strict",path="/"):
    return f"Set-Cookie:{name}={value}; Path={path}; Max-Age={max_age}; SameSite={SameSite}\r\n"


def cookies_from_string(string:str):
    cookies = {}
    for cookie in string.split(';'):
        var_name = ''
        var_val  = ''
        met_eq = False
        for c in cookie[1:]:
            if c == "=" and not met_eq:
                met_eq = True
                continue
            if c == ";" or c == "\r":
                break

            if not met_eq:
                var_name += c
                continue
            if met_eq:
                var_val += c
                continue
        
        cookies[var_name] = var_val

    return cookies

    



def accepts_enc(enc_type,string):
    _encs  = string.split(",")
    encs = []
    for enc in _encs:
        encs.append(enc.strip(" "))
    return enc_type in encs