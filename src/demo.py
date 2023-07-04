import server,headers #Critical Files
import time,random

myServer = server.HTTPServer() #Init class with default values



"""
Return time as plain text.
we use 'params: headers.ListenerParams' in order
to let the IDE know how to handle autocomplete. 
"""
def get_time(params: headers.ListenerParams):
    body = time.ctime(time.time()) #Formatted Time


    resp_header = headers.HTTPHeader() #Create an HTTP Header
    resp_header.header["Date"] = time.strftime("%a, %d %b %Y %I:%M:%S %Z",time.gmtime()) #Set time as the standards say
    resp_header.header["Expires"] = 0 # Disables Caching (should use Cache-Control)
    resp_header.header["Content-Type"] = headers.CONTENT_TYPES["plain"] #plain text mode
    resp_header.header["Content-Length"] = len(body) #Length of the body

    params.conn.sendall(resp_header.rformatted().encode()+body.encode()) #Send the response, with header and body as bytes appended to eachother



"""
Return the user agent as plain text
"""
def get_agent(params: headers.ListenerParams):
    body = "Your User Agent is: " + params.header["User-Agent"] #Grab the user agent from the request headers

    resp_header = headers.HTTPHeader() #Create an HTTP Header
    resp_header.header["Date"] = time.strftime("%a, %d %b %Y %I:%M:%S %Z",time.gmtime()) #Set time as the standards say
    resp_header.header["Expires"] = 0 # Disables Caching (should use Cache-Control)
    resp_header.header["Content-Type"] = headers.CONTENT_TYPES["plain"] #plain text mode
    resp_header.header["Content-Length"] = len(body) #Length of the body


    params.conn.sendall(resp_header.rformatted().encode()+body.encode()) #Send the response, with header and body as bytes appended to eachother


"""
Cookie-based authentication demo.
This combines apis, html and dynamic pages
all into one cool thing
"""
def api_set_cookie(params: headers.ListenerParams):
    
    
    resp_header = headers.HTTPHeader()
    resp_header.header["Content-Length"] = 0 #Set Content-Length to 0
    
    #Not Optimal
    if "Cookie" not in params.header: #if no cookies
        resp_header.cookies = headers.cookie("AuthID",random.randrange(0,9999),max_age=3600) #set a random value to a cookie that lasts 1 hour
    elif "AuthID" not in headers.cookies_from_string(params.header["Cookie"]): #if cookies but no AuthID 
        resp_header.cookies = headers.cookie("AuthID",random.randrange(0,9999),max_age=3600) #set a random value to a cookie that lasts 1 hour

    resp_header.set_redirect("/login")
    params.conn.sendall(resp_header.rformatted().encode())


#Authentication Check
def welcome(params:headers.ListenerParams):
    username = "You are not authenticated!"
    try:
        if "AuthID" in headers.cookies_from_string(params.header["Cookie"]):
            username = "Welcome back,"+headers.cookies_from_string(params.header["Cookie"])["AuthID"] #Get Authentication ID
    except KeyError: #If AuthID doesn;t exist or Cookie doesn't exist, KeyError is thrown telling us no authentication
        pass

    #HTML
    body = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Login</title>
</head>
<body>
    <h1>{}</h1>
    <button onclick="window.location.href='/api'">
        Click To Authenticate
    </button>
</body>
</html>
""".format(username) #add a string


    resp_header = headers.HTTPHeader() #Create an HTTP Header
    resp_header.header["Date"] = time.strftime("%a, %d %b %Y %I:%M:%S %Z",time.gmtime()) #Set time as the standards say
    resp_header.header["Expires"] = 0 # Disables Caching (should use Cache-Control)
    resp_header.header["Content-Type"] = headers.CONTENT_TYPES["html"] #plain text mode
    resp_header.header["Content-Length"] = len(body) #Length of the body

    params.conn.sendall(resp_header.rformatted().encode()+body.encode()) #Send the response, with header and body as bytes appended to eachother


myServer.set_listener("/time",get_time) #point /time to get_time()
myServer.set_listener("/agent",get_agent) #point /agent to get_agent()
myServer.set_listener("/api",api_set_cookie) #point /api to api_set_cooke()
myServer.set_listener("/login",welcome) #point /login to welcome()


#This will let the status code generator know about the ip and port of this server
headers._IP = myServer.ip
headers._PORT = myServer.port

myServer.startup() #Start Server