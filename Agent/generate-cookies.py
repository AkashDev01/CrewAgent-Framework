import os

from dotenv import load_dotenv

load_dotenv('../.env')

import json
from uuid import uuid4


interlocutor_id =  os.environ.get('CLIENT_ID')
session_id = uuid4()

cookies = {
    "interlocutor_id": interlocutor_id,
    "session_id": session_id.__str__()
}

with open('cookies.json', 'w', encoding='utf-8') as f:
    json.dump(json.dumps(cookies), f)