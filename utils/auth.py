import bcrypt  # type: ignore
import jwt  # type: ignore
from datetime import datetime, timedelta
from config.config import Config
from utils.database import MongoDB

class Auth:
    def __init__(self):
        self.db = MongoDB()
    
    @staticmethod
    def hashed_password(password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt).decode()  # Store as a string

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed_password.encode() if isinstance(hashed_password, str) else hashed_password)
    
    def check_password(self, password, hashed_password):
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password)
    
    def generate_token(self, user_id):
        payload = {
            'user_id': str(user_id),
            'exp': datetime.utcnow() + timedelta(days=1)
        }
        return jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')
    
    def verify_token(self, token):
        try:
            payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
            return payload['user_id']
        except:
            return None
    
    def register_user(self, name, email, password, age, role):
        if self.db.get_user(email):
            return False, "Email already registered"

        role = role.lower().strip()  # Normalize role input
        role_mapping = {
            "doctor": "doctor",
            "researcher": "researcher",
            "patient": "patient"
        }

        if role not in role_mapping:
            print(f"❌ Invalid role received: {role}")  # Debugging
            return False, "Invalid role selected"

        normalized_role = role_mapping[role]  # Convert to expected format

        hashed_password = self.hashed_password(password)
        user_data = {
            "name": name,
            "email": email,
            "password": hashed_password,
            "age": age,
            "role": normalized_role
        }

        result = self.db.create_user(user_data)
        if result is None:
            return False, "User registration failed due to a database error."

        return True, str(result.inserted_id)



    
    def login_user(self, email, password):
        user = self.db.get_user(email)
        if not user:
            return False, "User not found"
        
        if not self.check_password(password, user['password']):
            return False, "Invalid password"
        
        token = self.generate_token(user['_id'])
        
        return True, {
            "token": token,
            "user": {
                "name": user['name'],
                "email": user['email'],
                "role": user['role']
            }
        }


# ✅ Added the missing function below
def check_authentication(email, password):
    db = MongoDB()  # ✅ Initialize MongoDB instance
    user = db.get_user(email)  

    if not user:
        return None  # User doesn't exist

    if not Auth.verify_password(password, user["password"]):
        return None  # Incorrect password

    user["_id"] = str(user["_id"])  # Convert ObjectId to string
    return user
