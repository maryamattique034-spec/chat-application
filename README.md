# My Chat Project

## Description 
A real-time private chat application using Django, Django channels, and Websockets.
Only authorized users can join private rooms.

## Features 
- Two-user private chats
- JWT authentication
- Message history
- Real-time updates

## Tech Stack
- Python 3.10
- Django 5.x
- Django Channels
- PostgreSQL
- Redis (for Channels layer)

## Setup

1. Clone the repo:
```bash
git clone https://github.com/maryamattique034-spec/chat-application/tree/websocket_chat_modify
cd mysite


2. Create Virtual environment
python -m venv venv
source venv/bin/activate  #Mac/Linux
venv\Scripts\activate    # windows

3. Install dependencies
pip install -r requirements.txt 

4. Create .env file with environment variables(e.g., SECRET_KEY, database settings)

5. Apply migrations:
python manage.py migrate

6. Run Server
python manage.py runserver

7. Access in browser
http://127.0.0.1:8000/chat/<room_name>/





