#Version 2 - Mailboxes #import modules
from Tkinter import *
from tkFileDialog  import asksaveasfilename, SaveAs
from tkMessageBox  import showinfo, showerror, askyesno
from textEditor import TextEditorComponentMinimal
from email.parser import Parser
from email.base64mime import body_encode as encode_base64
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders
import Tkconstants
import mimetypes
import tkFileDialog
import re
import os
import socket
import ssl
import rfc822, StringIO, string, sys
import datetime
import thread                        # run with gui blocking    
import browser

CRLF = "\r\n"
threadExitVar = 0                        # used to signal child thread exit
host = "imap.gmail.com"
port = 993
# user = "pranav2000joglekar@gmail.com"
# pas = "Pranav2000"
global sock_smtp_ssl, file_smtp, sock_imap_ssl, file_imap, pend_tag, username, password, current_mbox, path, listBox, msg_no, attachement, att_data
att_data = ''
pend_tag = {"a"}
msgList       = []                       # list of retrieved emails text
listBox       = None                     # main window's scrolled msg list 


#GUI CODE STARTS HERE
def addAttachement():
    global attachement, att_data
    print('help works')
    attachement = tkFileDialog.askopenfilename(initialdir = "/", title = "Select Files", filetypes = (("jpeg files","*.jpg"), ("mp3 files", "*.mp3"), ("text files","*.txt"),("all files","*.*")))
    print(attachement)
    fp = open(attachement, 'rb')
    att_data = MIMEBase('application', 'octet-stream')
    att_data.set_payload((fp).read())
    encoders.encode_base64(att_data)
    att_data.add_header('Content-Disposition', "attachment; filename= %s" % attachement)
    """
    ctype, encoding = mimetypes.guess_type(attachement)
    maintype, subtype = ctype.split('/', 1)
    if maintype == 'image':
        fp = open(attachement, 'rb')
        att_data = MIMEImage(fp.read(), _subtype = subtype)
        fp.close()
    if maintype == 'audio':
        fp = open(attachement, 'rb')
        att_data = MIMEAudio(fp.read(), _subtype = subtype)
        fp.close()
    if maintype == 'text':
        fp = open(attachement, 'rb')
        att_data = MIMEText(fp.read(), _subtype = subtype)
        fp.close()
    else:
        fp = open(attachement, 'rb')
        att_data = MIMEBase(maintype, subtype) 
        att_data.set_payload(fp.read())
        fp.close()
    """

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
            stat = lineI.split(" ")[1]
            if stat == "OK" or stat == "BAD" or stat == "NO":
                break
    status = lineI.split(" ")[1]
    return status, rep

def send_command_imap(sock, cmd):
    global pend_tag
    """Send command to the SMTP/IMAP server"""
    cmd = cmd.encode('ascii')
    sock.sendall(cmd)
    rcode, rstatus = message_imap()
    return rcode, rstatus


def onViewFormatMail():
    # view selected message
    global username, msg_no, msgList, listBox
    msgnum = selectedMsg()
    if not (1 <= msgnum <= len(msgList)):
        showerror('MailClient', 'No message selected')
    else:
        parser = Parser()

        email = parser.parsestr(msgList[msgnum-1][0])
        """
        print("email --")
        print(email)
        print("email --")
        """

        body = ""
        if email.is_multipart():
            for part in email.walk():
                if part.is_multipart():
                    for subpart in part.get_payload():
                        if subpart.is_multipart():
                            for subsubpart in subpart.get_payload():
                                body = body + str(subsubpart.get_payload(decode=True)) + '\n'
                            #    print("body: " + body)
                        else:
                            body = body + str(subpart.get_payload(decode=True)) + '\n'
                            #print("body: " + body)
                else:
                    body = body + str(part.get_payload(decode=True)) + '\n'
                    #print("body: " + body)
        else:
            body = body + str(email.get_payload(decode=True)) + '\n'
            #print("body: " + body)

        body = str(body).decode('unicode-escape')
        open("email.html", "w").close() 
        f=open("email.html","w+")
        whole_msg = body.encode('utf-8')
        text_msg = whole_msg.split('html>')
        for i in range(len(text_msg)):
            #if i % 2 == 0:
                # = '</br'.join(text_msg.split('\n')
            text1_msg = text_msg[i].split('<html')
            text1_msg[0] = text1_msg[0].replace('\n', '</br>')
            text_msg[i] = ''.join(text1_msg)
                #text_msg[i] = text_msg[i].replace('\n', '</br>')
        #f.write('</br>'.join(body.encode('utf-8').split('\n')))
        #print(body.encode('utf-8'))
        #f.write(body.encode('utf-8'))
        f.write(''.join(text_msg))
        #print('written')
        f.close()
        
        msgnum = selectedMsg()
        msgnum = int(msg_no) + int(len(msgList)) - int(msgnum) + 1
        addFlag(msgnum, "Seen")
        os.remove(os.path.join(username,str(msgnum) + "s.txt"))
        with open(os.path.join(username, str(msgnum) + "s.txt"), 'w+') as f:
            f.write('1')
        noOfLoops = int(listBox.size()/40)
        msgList = []
        fillIndex(msgList)
        msg_no = 0
        for i in range(noOfLoops):
            onLoadMail()
        if email.get('To') is None:
            hdrs = rfc822.Message(StringIO.StringIO(msgList[msgnum - 1][0]))
            editmail('View #%d' %  msgnum,
                    hdrs['From'],
                    username,
                    hdrs['Subject'],
                    body,
                    hdrs['Date']
                )

        else:
            editmail('View #%d' %  msgnum,
                    email.get('From'),
                    email.get('To'),
                    email.get('Subject'),
                    body,
                    email.get('Date')
                )

        


def fillIndex(msgList):
    global current_mbox
    # fill all of main listbox
    listBox.delete(0, END)
    count = 1
    for msg in msgList:
        # print msg
        hdrs = rfc822.Message(StringIO.StringIO(msg[0]))
        # print hdrs
        msginfo = '%02d' % count
        for key in ('Subject', 'From', 'Date'):
            if hdrs.has_key(key): msginfo = msginfo + ' | ' + hdrs[key][:30]
        listBox.insert(END, msginfo)
    #    print(msg[1])
        #print("curr" + current_mbox.get())
        if msg[1] == 1 and current_mbox.get() != '[Gmail]/Sent Mail':
            listBox.itemconfig(count - 1, {'bg':'white'})
        if msg[1] == 0 and current_mbox.get() != '[Gmail]/Sent Mail':
            listBox.itemconfig(count - 1, {'bg':'red'})
        count = count+1
    listBox.see(END)         # show most recent mail=last line 


def selectedMsg():
    # get msg selected in main listbox
    # print listBox.curselection()
    if listBox.curselection() == ():
        return 0                                     
    else:                                            
        return eval(listBox.curselection()[0]) + 1   


def waitForThreadExit(win):
    import time
    global threadExitVar          
    delay = 0.0                   
    while not threadExitVar:
        win.update()              
        time.sleep(delay)         
    threadExitVar = 0             


def busyInfoBoxWait(message):
    

    popup = Toplevel()
    popup.title('Please Wait')
    popup.protocol('WM_DELETE_WINDOW', lambda:0)       # ignore deletes    
    center(popup)
    label = Label(popup, text=message+'...')
    label.config(height=10, width=40, cursor='watch')  # busy cursor
    label.pack()
    popup.focus_set()                                  # grab application
    popup.grab_set()                                   # wait for thread exit
    waitForThreadExit(popup)                           # gui alive during wait
    # print 'thread exit caught'
    popup.destroy() 


def loadMailThread(current_mbox_name):
    #load mail while main thread handles gui events
    global msgList, threadExitVar, username, password, file_imap, sock_imap_ssl, current_mbox, msg_no
    # print 'load start'
    # errInfo = ''
    # try:
    #     nextnum = len(msgList) + 1
    #     newmail = MailClient.loadmessages(mailserver, mailuser, mailpswd, nextnum)
    #     msgList = msgList + newmail
    # except:
    #     exc_type, exc_value = sys.exc_info()[:2]                # thread exc
    #     errInfo = '\n' + str(exc_type) + '\n' + str(exc_value)
    # print 'load exit'

    #mails = useless()

    #Select the desired inbox whose mails are to be displayed
    print("msg_no" + str(msg_no))
    if msg_no == 0:
        rcode, rstatus = choose_inbox(current_mbox_name)

        print("rcode" + str(rcode))
        print("rstatus" + str(rstatus))
        #Get the msg_no and uid of the last mail 
        msg_no = int(rstatus.split("\n")[3].split(" ")[1])

        uid = int(rstatus.split("\n")[5].split("]")[0].split(" ")[3])

    


    #Fetch the latest mails
    mails = fetch_mails() 
    for i in mails:
        mail = i[0]
        new_mail = [x.rstrip() for x in mail]
        emailText = '\n'.join(new_mail)
        msgList.append([emailText, i[1]])
    threadExitVar = 1   # signal main thread

def onLoadMail():
    getMailboxNames()
    global current_mbox, msg_no
    current_mbox_name = current_mbox.get()
    if current_mbox_name == "SentBox":
        current_mbox_name = '"[Gmail]/Sent Mail"'
    thread.start_new_thread(loadMailThread, (current_mbox_name,))
    busyInfoBoxWait('Retrieving mail')  

    # if errInfo:
    #     global mailpswd            # zap pswd so can reinput
    #     mailpswd = None
    #     showerror('MailClient', 'Error loading mail\n' + errInfo)

    #Fill the display
    fillIndex(msgList)


def decorate(rootWin):
    # window manager stuff for main window  
    rootWin.title('Mail Client')
    rootWin.protocol('WM_DELETE_WINDOW', onQuitMail)

def delete_login_success_screen():
    login_success_screen.destroy()

def makemainwindow(parent=None, sock_s = None, file_s = None, sock_i = None, file_i = None, usr = None):
    # make the main window - by default shows inbox
    global rootWin, listBox, allModeVar, username, password, login_success_screen, sock_smtp_ssl, file_smtp, sock_imap_ssl, file_imap, path,listBox, msg_no
    sock_smtp_ssl = sock_s
    file_smtp = file_s
    sock_imap_ssl = sock_i
    file_imap = file_i
    username = usr
    print("Inbox-")
    if parent:
        rootWin = Frame(parent)             # attach to a parent
        rootWin.pack(expand=YES, fill=BOTH)
    else:       
        rootWin = Tk()                      # assume I'm standalone
        decorate(rootWin)

    #Create Username Email folder if does not exist
    pathf = os.getcwd()
    print("The current working directory is %s" % pathf)
    
    if not os.path.exists(username):
        os.mkdir(username)
    
    path = os.path.join(pathf,username)
    
    print(path)

    # add main buttons at bottom
    frame1 = Frame(rootWin)
    frame1.pack(side=BOTTOM, fill=X)
    allModeVar = IntVar()
    #Checkbutton(frame1, text="All", variable=allModeVar).pack(side=RIGHT)
    actions = [ ('View',  onViewFormatMail),
                ('Mark Read/UnRead',  onMarkMail),  ('Delete',   onDeleteMail),
              ('Reply', onReplyMail), 
                ('Fwd',   onFwdMail)]
    y = Button(frame1, text = '                                      Compose                                         ', command=onWriteMail, bg='steelblue', fg='white', relief=RIDGE).pack(side=LEFT, fill=X)
    for (title, callback) in actions:
        Button(frame1, text=title, command=callback).pack(side=LEFT, fill=X)

    # add main listbox and scrollbar
    frame2  = Frame(rootWin)
    vscroll = Scrollbar(frame2)
    fontsz  = (sys.platform[:3] == 'win' and 11) or 12
    listBox = Listbox(frame2, bg='white', font=('courier', fontsz))
    
    # crosslink listbox and scrollbar
    vscroll.config(command=move, relief=SUNKEN)
    listBox.config(yscrollcommand=vscroll.set, relief=SUNKEN, selectmode=SINGLE)
    listBox.bind('<Double-1>', lambda event: onViewFormatMail())
    frame2.pack(side=TOP, expand=YES, fill=BOTH)
    vscroll.pack(side=RIGHT, fill=BOTH)
    listBox.pack(side=LEFT, expand=YES, fill=BOTH)

    """
    #Make and Display the Login Successful Window
    login_success_screen = Toplevel(rootWin)
    login_success_screen.title("Success")
    login_success_screen.geometry("150x100")
    Label(login_success_screen, text="Login Success").pack()
    Button(login_success_screen, text="OK", command=delete_login_success_screen).pack()
    center(login_success_screen)
    """
    msg_no = 0
    onLoadMail()
    return rootWin

def move(X1, X2):
    global listBox
    #print("X1 - " + str(X1) +" X2-" + str(X2))
    listBox.yview(X1, X2)
    if float(X2) > 0.95:
        print("Loading previous mails")
        onLoadMail()

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

def editmail(mode, From, To='', Subj='', origtext='', Date=''):
    global attachement
    # create a new mail edit/view window
    cc = ''
    bcc = ''
    win = Toplevel()
    win.title('MailClient - '+ mode)
    win.iconname('MailClient')
    viewOnly = (mode[:4] == 'View')

    # header entry fields
    frm =  Frame(win); frm.pack( side=TOP,   fill=X)
    lfrm = Frame(frm); lfrm.pack(side=LEFT,  expand=NO,  fill=BOTH)
    mfrm = Frame(frm); mfrm.pack(side=LEFT,  expand=NO,  fill=NONE)
    rfrm = Frame(frm); rfrm.pack(side=RIGHT, expand=YES, fill=BOTH)
    hdrs = []
    for (label, start) in [('To:',   To),           # order matters on send
                           ('Cc', cc),
                           ('Bcc', bcc),
                           ('Date:',   Date), 
                           ('Subj:', Subj)]:
        lab = Label(mfrm, text=label, justify=LEFT)
        ent = Entry(rfrm)
        lab.pack(side=TOP, expand=YES, fill=X)
        ent.pack(side=TOP, expand=YES, fill=X)
        #print(start)
        ent.insert('0', start)
        hdrs.append(ent)

    # send, cancel buttons (need new editor)
    #editor = TextEditorComponentMinimal(win)
    if viewOnly:
    #if False:
        for (label, callback) in [('Cancel', win.destroy), ('RAW Viewer', onViewRawMail)]:
            b = Button(lfrm, text=label, command=callback)
            b.config(bg='white', relief=RIDGE, bd=2)
            b.pack(side=TOP, expand=YES, fill=BOTH)
        app = browser.MainFrame(win,"file:///" + (os.path.join(os.getcwd(),"email.html")))
        browser.cef.Initialize()
        app.mainloop()
        browser.cef.Shutdown()
        #b = Button(lfrm, text="HTML Viewer", command=htmlviewer)
        #b.config(bg='white', relief=RIDGE, bd=2)
        #b.pack(side=TOP, expand=YES, fill=BOTH)
    else:
        #editor = None
        menubar = Frame(win, relief=RAISED, bd=2)
        menubar.pack(side=BOTTOM, fill=X)
        Button(menubar, text    = 'Add Attachement', 
                        relief  = FLAT, 
                        command = addAttachement).pack(side=BOTTOM)
        Label(menubar, text=attachement).pack(side=LEFT)
        editor = TextEditorComponentMinimal(win)
        sendit = (lambda w=win, e=editor, h=hdrs: send_mail(w, e, h))
        for (label, callback) in [('Cancel', win.destroy), ('Send', sendit)]:
            if not (viewOnly and label == 'Send'): 
                b = Button(lfrm, text=label, command=callback)
                b.config(bg='white', relief=RIDGE, bd=2)
                b.pack(side=TOP, expand=YES, fill=BOTH)
        editor.pack(side=BOTTOM)                         # may be multiple editors
        editor.setAllText(origtext)

        

    # body text editor: pack last=clip first
    """
    editor.pack(side=BOTTOM)                         # may be multiple editors
    editor.setAllText(origtext)
    if viewOnly:
        editor.freeze()
    """


def send_mail(win, editr, hdrs):
    global username, att_data
    print(win)
    print(editr.getAllText())
    print(hdrs)
    for i in hdrs:
        print(i.get())
    e_to = hdrs[0].get()
    e_Ccs = hdrs[1].get().split(",")
    e_Bccs = hdrs[2].get().split(",")
    #e_from = hdrs[0].get()
    e_time = hdrs[3].get()
    e_subject = hdrs[4].get()
    e_msg = editr.getAllText()

    #Create a new MIMEText Object with message
    if att_data != '':
        msg = MIMEMultipart(e_msg)
    else:
        msg = MIMEText(e_msg)
    # Look after Bcc and CC splitting

    s = '%s %s<%s>%s' % ('MAIL','FROM:','pranav2000joglekar@gmail.com', CRLF)
    print(s)
    s = s.encode('ascii')
    #sock2.sendall(s)
    #mmessage(file1)
    rcode, rstatus = send_command_smtp(sock_smtp_ssl, s)


    #Rcpt
    s = '%s %s<%s>%s' % ('RCPT','TO:',e_to, CRLF)
    print(s)
    s = s.encode('ascii')
    #sock2.sendall(s)
    #mmessage(file1)
    rcode, rstatus = send_command_smtp(sock_smtp_ssl, s)
    for e_Bcc in e_Bccs:
        s = '%s %s<%s>%s' % ('RCPT','TO:',e_Bcc, CRLF)
        print(s)
        s = s.encode('ascii')
        #sock2.sendall(s)
        #mmessage(file1)
        rcode, rstatus = send_command_smtp(sock_smtp_ssl, s)

    #Data

    s = '%s%s' % ('DATA',CRLF)
    s = s.encode('ascii')
    #sock2.sendall(s)
    #mmessage(file1)
    rcode, rstatus = send_command_smtp(sock_smtp_ssl, s)

    msg['Subject'] = e_subject
    msg['To'] = e_to
    msg['From'] = username

    if att_data != '':
        msg.attach(att_data)
        att_data = ''
    for e_Cc in e_Ccs:
        e_Cc = e_Cc.strip()
        msg['Cc'] = e_Cc
    """
    for e_Bcc in e_Bccs:
        e_Bcc = e_Bcc.strip()
        msg['Bcc'] = e_Bcc
    """

    #message_sent = "From: %s\r\n" % "pranav2000joglekar@gmail.com"+"To: %s\r\n" % "pranav2000joglekar@gmail.com" + "Subject: %s\r\n" % "GoodNight"+"\r\n"+"GoodNight" 

    #message_sent = "Subject: %s\r\n" % e_subject + "\r\n" + e_msg

    #s = '%s%s%s%s' % (message_sent,CRLF, ".", CRLF)

    s = '%s%s%s%s' % (msg.as_string(),CRLF, ".", CRLF)
    s = s.encode('ascii')
    #sock2.sendall(s)
    #mmessage(file1)
    rcode, rstatus = send_command_smtp(sock_smtp_ssl, s)
    if(int(rcode) == 250):
        #Add a new window if time permits
        print("Mail Sent")
        #Delete the window
        win.destroy()
    
def onWriteMail():
    # compose new email
    global username
    now = str(datetime.datetime.now())
    editmail('Write', From=username, Date=now)
    
def htmlviewer():
    root = Toplevel()
    app = browser.MainFrame(root,"file:///" + (os.path.join(os.getcwd(),"email.html")))
    browser.cef.Initialize()
    app.mainloop()
    browser.cef.Shutdown()
    # import webbrowser
    # webbrowser.open("email.html")

def container(ms = None):
    global current_mbox, mailboxes, attachement
    #34
    #Inbox, sentbox, compose menu bar
    mailboxes = ms
     #title = Menu(root)
    rootWin = Tk()
    rootWin.geometry("800x500")
    attachement = 'file:'
    """
    title = Menu(rootWin)
    rootWin.config(menu = title)
    submenu = Menu(title, tearoff = 0)
    title.add_cascade(label = "Boxes", menu = submenu)
    #root.config(menu = title)
    title.config(bg='white', fg='black', relief=RIDGE)
    # title.config(command=showhelp)
    #title.pack(fill=X)
    #title.add_cascade(label = "Boxes", menu = submenu)
    submenu.add_command(label = "Inbox", command = dummyfunction)
    submenu.add_command(label = "Sentbox", command = sentboxwindow)
    #submenu.add_separator()
    #submenu.add_command(label = "Exit", command = dummyfunction)
    
    
    compose = Menu(title, tearoff = 0)
    title.add_cascade(label = "Compose", menu = compose)
    compose.config(bg='white', fg='black', relief=RIDGE)
    #compose.pack(fill=X)
    #list.add_cascade(label = "Compose", menu = Compose)
    compose.add_command(label = "Compose email", command = onWriteMail)
    """
    #submenu.add_separator()
    #submenu.add_command(label = "Exit", command = dummyfunction)
    # use attachment to add help button
    # this is a bit easier with classes
    current_mbox = StringVar(rootWin)
    #mailboxes = {'INBOX','SentBox'}
    current_mbox.set('INBOX')
    #print("container" + current_mbox.get())
    #tag = Button(rootWin, text='Inbox')
    tag = OptionMenu(rootWin, current_mbox, *mailboxes)
    tag.config(bg='steelblue', fg='white', relief=RIDGE)
    # title.config(command=showhelp)
    tag.pack(fill=X)
    current_mbox.trace('w', change_mailbox)
    decorate(rootWin)
    center(rootWin)
    return rootWin

def change_mailbox(*args):
    global current_mbox, file_imap, sock_imap_ssl, msgList, msg_no
    print("cm" + str(current_mbox.get()))

    #Clear the file_imap variable
    file_imap.close()
    file_imap = sock_imap_ssl.makefile('rb')
    #file_imap.seek(0, os.SEEK_END)
    #Clear Current Screen
    msgList = []
    msg_no = 0
    fillIndex(msgList)
    #Add Loading Screen
    onLoadMail()

    #Fetch Mails

    #Display Mails

def sentboxwindow(parent=None):
    # make the main window - by default shows inbox
    global rootWin, listBox, allModeVar
    #rootWin.protocol('WM_DELETE_WINDOW', lambda:0)
    if parent:
        rootWin = Frame(parent)             # attach to a parent
        rootWin.pack(expand=YES, fill=BOTH)
    else:       
        rootWin = Tk()                      # assume I'm standalone
        decorate(rootWin)

    rootWin = Tk()
    title = Menu(rootWin)
    rootWin.config(menu = title)
    submenu = Menu(title, tearoff = 0)
    title.add_cascade(label = "Boxes", menu = submenu)
    #root.config(menu = title)
    title.config(bg='white', fg='black', relief=RIDGE)
    # title.config(command=showhelp)
    #title.pack(fill=X)
    #title.add_cascade(label = "Boxes", menu = submenu)
    submenu.add_command(label = "Inbox", command = makemainwindow)
    submenu.add_command(label = "Sentbox", command = dummyfunction)
    #submenu.add_separator()
    #submenu.add_command(label = "Exit", command = dummyfunction)
    
    
    compose = Menu(title, tearoff = 0)
    title.add_cascade(label = "Compose", menu = compose)
    compose.config(bg='white', fg='black', relief=RIDGE)
    #compose.pack(fill=X)
    #list.add_cascade(label = "Compose", menu = Compose)
    compose.add_command(label = "Compose email", command = onWriteMail)
    #submenu.add_separator()
    #submenu.add_command(label = "Exit", command = dummyfunction)
    # use attachment to add help button
    # this is a bit easier with classes
    tag = Button(rootWin, text='SentBox')
    tag.config(bg='steelblue', fg='white', relief=RIDGE)
    # title.config(command=showhelp)
    tag.pack(fill=X)
    #decorate(rootWin)
    

    # add main buttons at bottom
    frame1 = Frame(rootWin)
    frame1.pack(side=BOTTOM, fill=X)
    allModeVar = IntVar()
    Checkbutton(frame1, text="All", variable=allModeVar).pack(side=RIGHT)
    actions = [ ('Load',  onLoadMail),  ('View',  onViewFormatMail),
                ('Save',  onSaveMail),  ('Del',   onDeleteMail),
                ('Write', onWriteMail), ('Reply', onReplyMail), 
                ('Fwd',   onFwdMail),   ('Quit',  onQuitMail) ]
    for (title, callback) in actions:
        Button(frame1, text=title, command=callback).pack(side=LEFT, fill=X)

    # add main listbox and scrollbar
    frame2  = Frame(rootWin)
    vscroll = Scrollbar(frame2)
    fontsz  = (sys.platform[:3] == 'win' and 12) or 15
    listBox = Listbox(frame2, bg='white', font=('courier', fontsz))
    
    # crosslink listbox and scrollbar
    vscroll.config(command=listBox.yview, relief=SUNKEN)
    listBox.config(yscrollcommand=vscroll.set, relief=SUNKEN, selectmode=SINGLE)
    listBox.bind('<Double-1>', lambda event: onViewRawMail())
    frame2.pack(side=TOP, expand=YES, fill=BOTH)

    vscroll.pack(side=RIGHT, fill=BOTH)
    listBox.pack(side=LEFT, expand=YES, fill=BOTH)
    #rootWin = makemainwindow(container_sentbox())
    #return rootWin
    decorate(rootWin)
    return rootWin


def container_sentbox():
    #Inbox, sentbox, compose menu bar
     #title = Menu(root)
    rootWin = Tk()
    title = Menu(rootWin)
    rootWin.config(menu = title)
    submenu = Menu(title, tearoff = 0)
    title.add_cascade(label = "Boxes", menu = submenu)
    #root.config(menu = title)
    title.config(bg='white', fg='black', relief=RIDGE)
    # title.config(command=showhelp)
    #title.pack(fill=X)
    #title.add_cascade(label = "Boxes", menu = submenu)
    submenu.add_command(label = "Inbox", command = makemainwindow)
    submenu.add_command(label = "Sentbox", command = dummyfunction)
    #submenu.add_separator()
    #submenu.add_command(label = "Exit", command = dummyfunction)
    
    
    compose = Menu(title, tearoff = 0)
    title.add_cascade(label = "Compose", menu = compose)
    compose.config(bg='white', fg='black', relief=RIDGE)
    #compose.pack(fill=X)
    #list.add_cascade(label = "Compose", menu = Compose)
    compose.add_command(label = "Compose email", command = onWriteMail)
    #submenu.add_separator()
    #submenu.add_command(label = "Exit", command = dummyfunction)
    # use attachment to add help button
    # this is a bit easier with classes
    tag = Button(rootWin, text='SentBox')
    tag.config(bg='steelblue', fg='white', relief=RIDGE)
    # title.config(command=showhelp)
    tag.pack(fill=X)
    #decorate(rootWin)
    return rootWin
    
def dummyfunction():
    print("You are already here!")


def selectedMsg():
    # get msg selected in main listbox
    # print listBox.curselection()
    if listBox.curselection() == ():
        return 0                                     # empty tuple:no selection
    else:                                            # else zero-based index
        return listBox.curselection()[0] + 1   # in a 1-item tuple of str

def getMailboxNames():
    global sock_imap_ssl, pend_tag, current_mbox, mailboxes
    pend_tag = {"a"}
    cmd = '%s %s %s %s%s' %('a', 'LIST', '""', '*', CRLF)
    cmd = cmd.encode('ascii')
    #print(cmd)
    rcode, rstatus = send_command_imap(sock_imap_ssl, cmd)
    print("Mailbox")
    rstatus = rstatus.split("\r\n")
    rstatus.pop()
    rstatus.pop()
    #print(rstatus[0])
    for line in rstatus:
    #    print(line)
        inboxName = line.split('"')[-2]
        flags = line.split("(")
        flags = flags[1].split(")")
        flags = flags[0].split("\\")
        flags = flags[1:]
    #    print(flags)
        for i in range(len(flags)):
            flags[i] = flags[i].strip()
        #inboxName = inboxName[1:-1]
        if 'Noselect' not in flags:
            mailboxes.add(inboxName)
        print(inboxName)

#Function to choose inbox whose mails are to be displayed
def choose_inbox(current_mbox_name):
    global sock_imap_ssl, pend_tag, current_mbox
    pend_tag = {"a"}
    #print("ci" + str(current_mbox_name))
    cmd = '%s %s "%s"%s' % ("a","SELECT",current_mbox_name, CRLF)
    print(cmd)
    #print("SEl success")
    cmd = cmd.encode('ascii')
    rcode, rstatus = send_command_imap(sock_imap_ssl, cmd) 
    #sock_imap_ssl.sendall(cmd)
    #print lineI
    #rcode, rstatus = message_imap()
    #print("Sel rep - rcode: " + str(rcode) + " rstatus: " + str(rstatus))
    return rcode, rstatus

def addFlag(msgno, flag):
    global sock_imap_ssl, pend_tag, current_mbox
    s = "%s %s %s %s (\%s)%s" % ("a", "STORE", msgno, "+FLAGS", flag, CRLF)
    print(s)
    s = s.encode('ascii')
    rcode, rstatus = send_command_imap(sock_imap_ssl, s)
   # print(rcode)
   # print(rstatus)

def fetch_mails():
#GET Email
#message with id - 13126 used for test case.
#a FETCH 13127 BODY[]
    global sock_imap_ssl, msg_no
    mails = []
    pend_tag = {"a"}
    for i in range(msg_no, msg_no - 40, -1):
        current_seen = 0
        """
        #Check if the message is seen or not
        cmd = "%s %s %s %s%s" % ('a', 'FETCH', str(i), 'FLAGS', CRLF)
        rcode, rstatus = send_command_imap(sock_imap_ssl, cmd)
        print(rstatus)
        flags = rstatus.split("\n")[0]
        flags = flags.split("(")[2]
        flags = flags[:-3]
        flags = flags.split("\\")
        for flag in flags:
            flag = flag.strip()
        print(flags)
        if 'Seen' in flags:
            current_seen = 1
        """
        path_u = os.path.join(path,str(i) + ".txt")

        path_seen = os.path.join(path,str(i) + "s.txt")


        if i == 0:
            #Alerting about end of messages
            break;
        if(os.path.exists(path_u)):
            #email Already downloaded
            with open(path_u, 'r') as f:
                mail = f.readlines()
                for item in mail:
                    item.rstrip()
                    item = item + "\r\n"
            #mail = [xstrip() for x in mail]
            with open(path_seen, 'r') as f:
                current_seen = f.readline()
                current_seen = int(current_seen)

        #Else-
        else:
            cmd = "%s %s %s %s%s" % ('a', 'FETCH', str(i), 'FLAGS', CRLF)
            rcode, rstatus = send_command_imap(sock_imap_ssl, cmd)
            print(rstatus)
            flags = rstatus.split("\n")[0]
            flags = flags.split("(")[2]
            flags = flags[:-3]
            flags = flags.split("\\")
            for flag in flags:
                flag = flag.strip()
            print(flags)
            if 'Seen' in flags:
                print(str(i))
                print("yes")
                current_seen = 1


            cmd = '%s %s %s %s%s' % ("a", "FETCH", str(i), "BODY[]", CRLF)
            cmd = cmd.encode('ascii')
            sock_imap_ssl.sendall(cmd)
            mail = get_mail()
            #Check if the message is seen or not
            if current_seen == 0:
                cmd = '%s %s %s %s %s%s' % ('a', 'STORE', str(i), '-FLAGS', '(\Seen)', CRLF)
                rcode, rstatus = send_command_imap(sock_imap_ssl, cmd)
                print("removing seen" + rstatus)
            f = open(path_u, "w+")
#            f.write(mail)
            with open(path_u, 'w+') as f:
                for item in mail:
                    print(item)
                    #item.rstrip()
                    item = item[:-2]
                    print(item)
                    f.write("%s\n" % item)
                print(mail)
            with open(path_seen, 'w+') as f:
                if current_seen == 1:
                    f.write('1')
                else:
                    f.write('0')

                #f.write("%s" % str(current_seen))

        """
        cmd = '%s %s %s %s%s' % ("a", "FETCH", str(i), "BODY[]", CRLF)
        cmd = cmd.encode('ascii')
        sock_imap_ssl.sendall(cmd)
        mail = get_mail()
        """
        """
        print("-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
        print(mail)
        print("-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
        """
        """
        if mail[0][:12] == 'Delivered-To':
            mails.append(mail)
        elif mail[0][:11] == 'Return-Path':
            mails.append(mail)
        """
        mails.append([mail, current_seen])
    msg_no = msg_no - 40
    return mails

def get_mail():
    #global fileI, fileII, sockI, sockII
    global file_imap, sock_imap_ssl, pend_tag
    mail = [] 
    lineI = file_imap.readline()
    while True:
        lineI = file_imap.readline()
        mail.append(lineI)
        tag = lineI.split(" ")[0]
        if tag in pend_tag:
            stat = lineI.split(" ")[1]
            if stat == "OK" or stat == "BAD" or stat == "NO":
                mail.pop()
                break
    #print("___________________________________________________________________________________________________________________________________________")
    #print(mail)
    #print("___________________________________________________________________________________________________________________________________________")
    return mail

# use objects that retain prior directory for the next
# select, instead of simple asksaveasfilename() dialog

saveOneDialog = saveAllDialog = None

def onViewRawMail():
    # view selected message - raw mail text with header lines
    msgnum = selectedMsg()
    if not (1 <= msgnum <= len(msgList)):
        showerror('MailClient', 'No message selected')
    else:
        text = msgList[msgnum-1][0]                # put in ScrolledText
        from ScrolledText import ScrolledText
        window  = Toplevel()
        window.title('MailClient raw message viewer #' + str(msgnum))
        browser = ScrolledText(window)
        browser.insert('0.0', text)
        browser.pack(expand=YES, fill=BOTH)


def onSaveMail():
    pass
def onMarkMail():
    global msgList, msg_no, sock_imap_ssl, username, listBox
    msgnum = selectedMsg()
    noOfLoops = int(listBox.size()/40)
    #msgnumlast = int(listBox[-1][-1]) + 1
    msgnum = int(msg_no) + int(len(msgList)) - int(msgnum) + 1
    cmd = "%s %s %s %s%s" % ('a', 'FETCH', str(msgnum), 'FLAGS', CRLF)
    rcode, rstatus = send_command_imap(sock_imap_ssl, cmd)
    print(rstatus)
    flags = rstatus.split("\n")[0]
    flags = flags.split("(")[2]
    flags = flags[:-3]
    flags = flags.split("\\")
    for flag in flags:
        flag = flag.strip()
    print(flags)
    if 'Seen' in flags:
        #Remove Seen and mark as unread
        cmd = '%s %s %s %s %s%s' % ('a', 'STORE', str(msgnum), '-FLAGS', '(\Seen)', CRLF)
        rcode, rstatus = send_command_imap(sock_imap_ssl, cmd)
        print('i' + rstatus)

        #Change in File
        os.remove(os.path.join(username,str(msgnum) + "s.txt"))
        with open(os.path.join(username, str(msgnum) + "s.txt"), 'w+') as f:
            f.write('0')
            print(00)

    else:
        #Add Seen and mark as read
        cmd = '%s %s %s %s %s%s' % ('a', 'STORE', str(msgnum), '+FLAGS', '(\Seen)', CRLF)
        rcode, rstatus = send_command_imap(sock_imap_ssl, cmd)
        print('i' + rstatus)
        os.remove(os.path.join(username,str(msgnum) + "s.txt"))
        with open(os.path.join(username, str(msgnum) + "s.txt"), 'w+') as f:
            f.write('1')
            print(11)
    #REloading
    msgList = []
    fillIndex(msgList)
    msg_no = 0
    print(len(msgList))
    print("Updated")
    #print(msgnumlast)
    #msgList = msgList[:-39]
    for i in range(noOfLoops):
        onLoadMail()

def onDeleteMail():
    global msgList, msg_no, sock_imap_ssl, username, listBox
    msgnum = selectedMsg()
    #msgnumlast = int(listBox[-1][-1]) + 1
    msgnum = int(msg_no) + int(len(msgList)) - int(msgnum) + 1
    print("deleting " + str(msgnum))
    addFlag(msgnum, "Deleted")
    cmd = "%s %s%s" % ("a", "EXPUNGE", CRLF)
    rcode, rstatus = send_command_imap(sock_imap_ssl, cmd)
    print(rcode)
    print(rstatus)
    os.remove(username + "/" + str(msgnum) +".txt")
    os.remove(username + "/" + str(msgnum) +"s.txt")
    msg_no = msg_no + 39 
    for i in range(int(msgnum), msg_no + 1):
        #msgList.pop()
        os.rename(username + "/" + str(int(i) + 1) + ".txt", username + "/" + str(i) + ".txt")
        os.rename(username + "/" + str(int(i) + 1) + "s.txt", username + "/" + str(i) + "s.txt")
    noOfLoops = int(listBox.size()/40)
    msgList = []
    fillIndex(msgList)
    msg_no = 0
    print(len(msgList))
    print("Deleted")
    #print(msgnumlast)
    #msgList = msgList[:-39]
    for i in range(noOfLoops):
        onLoadMail()


def onReplyMail ():
    msgnum = selectedMsg()
    hdrs = rfc822.Message(StringIO.StringIO(msgList[msgnum - 1][0]))
    now = str(datetime.datetime.now())   
    editmail('Write', From=username, To=hdrs['From'], Date=now, Subj='Re: '+hdrs['Subject'])

def onFwdMail():
    msgnum = selectedMsg()
    hdrs = rfc822.Message(StringIO.StringIO(msgList[msgnum - 1][0]))
    now = str(datetime.datetime.now())
    parser = Parser()
    email = parser.parsestr(msgList[msgnum-1][0])
    body = ""
    if email.is_multipart():
        for part in email.walk():
            if part.is_multipart():
                for subpart in part.get_payload():
                    if subpart.is_multipart():
                        for subsubpart in subpart.get_payload():
                            body = body + str(subsubpart.get_payload(decode=True)) + '\n'
                    else:
                        body = body + str(subpart.get_payload(decode=True)) + '\n'
            else:
                body = body + str(part.get_payload(decode=True)) + '\n'
    else:
        body = body + str(email.get_payload(decode=True)) + '\n'

    body = str(body).decode('unicode-escape')
    fwdtext = "---------- Forwarded message ---------\nFrom: <" + hdrs['From'] + ">\nDate: " + hdrs['Date'] + "\nSubject: " + hdrs['Subject'] + "\nTo: <" + email.get('To') + ">\nCc: <" + "cc?" + ">\n\n"
    editmail('Write', From=username, Date=now, Subj="Fwd: " + hdrs['Subject'], origtext=fwdtext+body)

def onQuitMail():
    if askyesno('MailClient', 'Surely Quit?'):
        exit()
def mail_extractor():
    pass

if __name__ == '__main__':
    # run stand-alone or attach
    rootWin = makemainwindow(container())    # or makemainwindow()
    rootWin.mainloop()
