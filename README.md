# Email Client
A simple email client in python which uses sockets to connect to SMTP and IMAP servers to send and receive emails(containing attachements)

## Features:
The email client enables one to:
1. Compose an email. (Cc, Bcc functionality available)
2. View Inbox and SentBox emails. (Most recent 40 emails can be viewed)
3. Reply to, forward, delete emails.
4. View Raw emails
5. Mark emails as Read and Unread
6. Load previous emails on scrolling to bottom
7. Attachment functionality (Only “.jpeg” attachments achieved)

## Installation
OS Dependencies: python2, TkInter.    
Python2 Dependencies: Cefpython.  
Run
`pip install -r requirements.txt` 
to install the dependencies automatically

## Troubleshooting:
If you don’t have TkInter installed, run ​ sudo​ ​ apt-get install python-tk
If your pip defaults to python3, then run ​ python2 -m​ ​ pip install -r requirements.txt

## Usage:
Follow the steps as mentioned on: https://support.google.com/mail/answer/7126229?hl=en to enable IMAP. Followed by this, you will receive an email asking confirmation for the same.
Run the program as `python2 working.py` to start sending mails.
