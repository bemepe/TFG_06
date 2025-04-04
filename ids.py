from bson.objectid import ObjectId
from icecream import ic
from datetime import datetime

id = f"{str(ObjectId())}_{datetime.now().strftime('%d%m%Y-%H%M%S')}"
ic(id)