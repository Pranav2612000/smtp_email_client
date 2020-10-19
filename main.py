#Version 2 - Mailboxes #import modules
 
from Tkinter import *
import os
import socket
import base64
import ssl
import inbox2

from email.base64mime import body_encode as encode_base64
CRLF = "\r\n"

global username, password
global login_screen
global username_login_entry
global password_login_entry
global file_smtp #file1
global file_imap #fileI
#global sock1, sock2, sockI, sockII
global sock_smtp, sock_smtp_ssl, sock_imap, sock_imap_ssl
global pend_tag
global ms
ms = set() 
def message_smtp():
    global file_smtp
    """
    pend_tag = {"a"}
    resp = []
    lineI = fileI.readline(8193)
    print lineI
    tag = lineI.split(" ")[0]
    print tag
    while(tag == "*"):
        lineI = fileI.readline(8193)
        tag = lineI.split(" ")[0]
        print tag
        print(lineI)
    """
    rep = ""
    while True:
        line1 = file_smtp.readline()
        print line1
        rep = rep + line1
        #if tag in pend_tag:
        if line1[3:4] != "-": 
            break
    return line1.split(" ")[0], rep

def send_command_smtp(sock, cmd):
    """Send command to the SMTP/IMAP server"""
    cmd = cmd.encode('ascii')
    sock.sendall(cmd)
    rcode, rstatus = message_smtp()
    return rcode, rstatus

def send_command_imap(sock, cmd):
    global pend_tag
    """Send command to the SMTP/IMAP server"""
    cmd = cmd.encode('ascii')
    sock.sendall(cmd)
    rcode, rstatus = message_imap()
    return rcode, rstatus

def smtp_connect():
    global file_smtp, sock_smtp, sock_smtp_ssl
    #SMTP Verification

    ssl_context = ssl._create_stdlib_context(certfile = None, keyfile = None)

    sock_smtp = socket.create_connection(("smtp.gmail.com", 465), socket._GLOBAL_DEFAULT_TIMEOUT, None)
    sock_smtp_ssl = ssl_context.wrap_socket(sock_smtp, server_hostname = "smtp.gmail.com")
    file_smtp = sock_smtp_ssl.makefile('rb')
    rcode,rstatus = message_smtp()

def smtp_ehlo():
    #Code to use HELO if EHLO doesnt work to be added
    global file_smtp, sock_smtp_ssl
    fqdn = socket.getfqdn()
    if '.' in fqdn:
        local_hostname = fqdn
    else:
         # We can't find an fqdn hostname, so use a domain literal
        addr = '127.0.0.1'
        try:
            addr = socket.gethostbyname(socket.gethostname())
        except socket.gaierror:
            pass
        local_hostname = '[%s]' % addr
    s = '%s %s%s' % ('EHLO', local_hostname, CRLF)
    #s = s.encode('ascii')
    #sock2.sendall(s)
    #rcode, rstatus = message_smtp()
    rcode, rstatus = send_command_smtp(sock_smtp_ssl, s)
    print("EHLO STATUS:" + rcode + rstatus)

def smtp_login():
    global file_smtp, sock_smtp_ssl, username, password
    #userstr = username_verify.get()
    # userstr = "pranav2000joglekar@gmail.com"
    #username = userstr
    print("username")
    print(username)
    user64 = encode_base64(username.encode('ascii'), eol='')
    #passstr = password_verify.get()
    # passstr = "<your-password>"
    #password = passstr
    print(password)
    pass64 = encode_base64(password.encode('ascii'), eol='')
    auths = '%s %s%s' % ("AUTH", "LOGIN" + " " + user64, CRLF)
    rcode, rstatus = send_command_smtp(sock_smtp_ssl, auths)

    passs = '%s%s' % (pass64, CRLF)
    rcode, rstatus = send_command_smtp(sock_smtp_ssl, passs)
    print(rcode)

    return int(rcode)
 
def smtp_auth() :
    #Error Cases to be handled
    smtp_connect()
    smtp_ehlo()

    auth_code = smtp_login()
    if auth_code == 235 :
        return 1 

def message_imap():
    #Operation with tags to be added
    global file_imap, pend_tag
    rep = ""
    while True:
        lineI = file_imap.readline()
        print lineI
        rep = rep + lineI
        tag = lineI.split(" ")[0]
        if tag in pend_tag:
            break
    status = lineI.split(" ")[1]
    return status, rep

def choose_inbox():
    global sock_imap_ssl, pend_tag
    pend_tag = {"a"}
    cmd = '%s %s %s%s' % ("a","SELECT","INBOX", CRLF)
    cmd = cmd.encode('ascii')
    sock_imap_ssl.sendall(cmd)
    #print lineI
    message_imap()

def fetch_mail():
#GET Email
#message with id - 13126 used for test case.
#a FETCH 13127 BODY[]
    global sock_imap_ssl
    pend_tag = {"a"}
    cmd = '%s %s %s %s%s' % ("a", "FETCH", "13126", "BODY[]", CRLF)
    cmd = cmd.encode('ascii')
    sock_imap_ssl.sendall(cmd)
    mail_content = get_mail(pend_tag)

def get_mail(pend_tag):
    global file_imap, lineI
    #all lines except first and last
    mail = [] 
    lineI = file_imap.readline()
    while True:
        lineI = file_imap.readline()
        mail.append(lineI)
        tag = lineI.split(" ")[0]
        if tag in pend_tag:
            break
    
    mail.pop()
    #print(mail.pop())
    #print("______________________________")
    return mail

def imap_connect():
    global file_imap, sock_imap, sock_imap_ssl, pend_tag
    host = "imap.gmail.com"
    #port = 143
    port = 993
    ssl_context = ssl._create_stdlib_context(certfile = None, keyfile = None)
    pend_tag = {"a"}
    sock_imap = socket.create_connection((host, port))
    sock_imap_ssl = ssl_context.wrap_socket(sock_imap, server_hostname = host)
    #fileI = sockI.makefile('rb')
    file_imap = sock_imap_ssl.makefile('rb')
    print "reading"

def imap_capability():
    global file_imap, sock_imap, pend_tag
    cmd = '%s%s' % ("a CAPABILITY", CRLF)
    cmd = cmd.encode('ascii')
    #sock_imap_ssl.sendall(cmd)
    rcode, rstatus = send_command_imap(sock_imap_ssl, cmd)

def imap_login():
    global file_imap, sock_imap, sock_imap_ssl, pend_tag, username, password
    # user = "pranav2000joglekar@gmail.com"
    #user = username_verify.get()
    print("username I")
    print(username)
    # pas = "<your-password>"
    #pas = password_verify.get()
    #print(password)
    # LOGIN
    cmd = '%s %s %s %s%s' % ("a","LOGIN",username,password, CRLF)
    print("login")
    auth_resp,status = send_command_imap(sock_imap_ssl, cmd)
    return auth_resp

def imap_auth():
    global file_imap, sock_imap, sock_imap_ssl, pend_tag
    #CONNECT
    imap_connect()
    #CAPABILITY TEST
    imap_capability()
    #LOGIN
    auth_resp = imap_login()
    if(auth_resp == "OK"):
        return 1

# login 
def getMailboxNames():
    global sock_imap_ssl, pend_tag, current_mbox, ms
    pend_tag = {"a"}
    cmd = '%s %s %s %s%s' %('a', 'LIST', '""', '*', CRLF)
    cmd = cmd.encode('ascii')
    #print(cmd)
    rcode, rstatus = send_command_imap(sock_imap_ssl, cmd)
    print("Mailbox")
    rstatus = rstatus.split("\r\n")
    rstatus.pop()
    rstatus.pop()
    print(rstatus[0])
    for line in rstatus:
        print(line)
        inboxName = line.split('"')[-2]
        flags = line.split("(")
        flags = flags[1].split(")")
        flags = flags[0].split("\\")
        flags = flags[1:]
        print(flags)
        for i in range(len(flags)):
            flags[i] = flags[i].strip()
        #inboxName = inboxName[1:-1]
        if 'Noselect' not in flags:
            ms.add(inboxName)
        print(inboxName)
 
def login():
    main_screen.destroy()
    global login_screen
    #login_screen = Toplevel(main_screen)
    login_screen = Tk()
    login_screen.title("Login")
    login_screen.geometry("300x250")
    center(login_screen)
    Label(login_screen, text="Please enter details below to login").pack()
    Label(login_screen, text="").pack()
 
    global username_verify
    global password_verify
 
    username_verify = StringVar()
    password_verify = StringVar()
 
    global username_login_entry
    global password_login_entry
 
    Label(login_screen, text="Username * ").pack()
    username_login_entry = Entry(login_screen, textvariable=username_verify)
    username_login_entry.pack()
    Label(login_screen, text="").pack()
    Label(login_screen, text="Password * ").pack()
    password_login_entry = Entry(login_screen, textvariable=password_verify, show= '*')
    password_login_entry.pack()
    Label(login_screen, text="").pack()
    Button(login_screen, text="Login", width=10, height=1, command = login_verify).pack()
    #main_screen.destroy()
    login_screen.mainloop()   
 
# After login
 
def login_verify():
    global username, password
    testing = 0
    username = username_verify.get()
    password = password_verify.get()
    print("username I")
    print(username)
    print(password)
    if testing:
        username = '<your-email>'
        password = '<your-password>'
        login_success()
        return
    #SMTP Verification
    smtp_auth_successful = smtp_auth()
    #IMAP Verification
    imap_auth_successful = imap_auth()

    if(smtp_auth_successful and imap_auth_successful):
        login_success()
    else:
        password_not_recognised()

# login success
 
def login_success():
    global login_success_screen, username, password
    print("Working-")
    print(username)
    print(password)
    #Delete the old windows
    login_screen.destroy()

    getMailboxNames()
    #Display Inbox Window
    rootWin = inbox2.makemainwindow(inbox2.container(ms), sock_smtp_ssl, file_smtp, sock_imap_ssl, file_imap, username)    # or makemainwindow()
    rootWin.mainloop()
    #login_success_screen = Toplevel(rootWin)
    #To test if these features
    #choose_inbox()
    #fetch_mail()
 
#login failure
 
def password_not_recognised():
    global password_not_recog_screen
    password_not_recog_screen = Toplevel(login_screen)
    password_not_recog_screen.title("Failure")
    password_not_recog_screen.geometry("150x100")
    Label(password_not_recog_screen, text="Invalid Credentials").pack()
    Button(password_not_recog_screen, text="OK", command=delete_password_not_recognised).pack()
 
# user not found
 
def user_not_found():
    global user_not_found_screen
    user_not_found_screen = Toplevel(login_screen)
    user_not_found_screen.title("Error")
    user_not_found_screen.geometry("150x100")
    Label(user_not_found_screen, text="User Not Found").pack()
    Button(user_not_found_screen, text="OK", command=delete_user_not_found_screen).pack()
 
# Deleting popups
 
def delete_login_success_screen():
    login_success_screen.destroy()
 
def delete_password_not_recognised():
    password_not_recog_screen.destroy()
 
 
def delete_user_not_found_screen():
    user_not_found_screen.destroy()
 
 
#Center the windows
def center(win):
    #win.withdraw()
    win.attributes('-alpha', 0.0)
    win.update_idletasks()
    width = win.winfo_width()
    #height = win.winfo_height()
    #x = (win.winfo_screenwidth() // 2) - (width // 2)
    #y = (win.winfo_screenheight() // 2) - (height // 2)
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.attributes('-alpha', 1.0)
    win.deiconify()
    #win.geometry('+{}+{}'.format(width, height, x, y))

# Main window
 
def main_account_screen():
    global main_screen
    main_screen = Tk()
    main_screen.geometry("300x150")
    center(main_screen)
    main_screen.title("Account Login")
    a =  Button(text="Login", height="2", width="30", command = login)#.pack()
    a.place(relx = 0.5, rely = 0.5, anchor = CENTER) 
    Label(text="").pack()
    main_screen.mainloop()
main_account_screen()
