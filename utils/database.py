from pymongo import MongoClient  # type: ignore
from config.config import Config
from datetime import datetime, timezone
from bson import ObjectId  # type: ignore  

class MongoDB:
    def __init__(self):
        try:
            if not Config.MONGODB_URI:
                raise ValueError("MongoDB URI is missing in the config.")

            self.client = MongoClient(Config.MONGODB_URI)
            self.db = self.client.get_database(Config.DB_NAME) if self.client else None

            if self.db is not None:
                print("✅ Connected to MongoDB")
            else:
                print("❌ Failed to connect to MongoDB")
        except Exception as e:
            self.db = None
            print(f"❌ Error connecting to MongoDB: {e}")

    def get_database(self):
        return self.db

    def create_user(self, user_data):
        if self.db is None:
            print("⚠️ Database connection not established!")
            return None

        try:
            users = self.db.users
            user_data['created_at'] = datetime.now(timezone.utc)

            # Normalize role input
            if "role" in user_data:
                user_data["role"] = user_data["role"].strip().lower().replace(" ", "_")

            # Initialize user fields
            user_data['health_records'] = []
            user_data['research_history'] = []
            user_data['wellness_data'] = []
            user_data['symptom_history'] = []

            valid_roles = {"doctor", "researcher", "patient"}
            if "role" not in user_data or user_data["role"] not in valid_roles:
                print(f"❌ Invalid role: {user_data.get('role', 'None')}")
                return None

            result = users.insert_one(user_data)
            print(f"✅ User {user_data['email']} registered successfully with role {user_data['role']}")
            return result
        except Exception as e:
            print(f"❌ Error creating user: {e}")
            return None


    def get_user(self, email):
        if self.db is None:
            print("⚠️ Database connection not established!")
            return None
        return self.db.users.find_one({"email": email})

    def update_health_record(self, user_id, record):
        if self.db is None:
            print("⚠️ Database connection not established!")
            return None
        try:
            record['timestamp'] = datetime.now(timezone.utc)
            return self.db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$push": {"health_records": record}}
            )
        except Exception as e:
            print(f"❌ Error updating health record: {e}")
            return None

    def save_research_analysis(self, user_id, analysis):
        if self.db is None:
            print("⚠️ Database connection not established!")
            return None
        try:
            analysis['timestamp'] = datetime.now(timezone.utc)
            return self.db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$push": {"research_history": analysis}}
            )
        except Exception as e:
            print(f"❌ Error saving research analysis: {e}")
            return None

    def save_wellness_data(self, user_id, data):
        if self.db is None:
            print("⚠️ Database connection not established!")
            return None
        try:
            data['timestamp'] = datetime.now(timezone.utc)
            return self.db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$push": {"wellness_data": data}}
            )
        except Exception as e:
            print(f"❌ Error saving wellness data: {e}")
            return None

    def delete_wellness_data(self, user_id):
        try:
            result = self.db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"wellness_data": []}}
            )
            print(f"Deleted wellness data for user {user_id}")
            return result.modified_count > 0
        except Exception as e:
            print(f"Error deleting wellness data for user {user_id}: {e}")
            return False

    def save_symptom_analysis(self, user_id, analysis_data):
        if self.db is None:
            print("⚠️ Database connection not established!")
            return None
        try:
            analysis_record = {
                "timestamp": datetime.now(timezone.utc),
                "analysis_data": analysis_data,
                "type": "symptom_analysis"
            }
            return self.db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$push": {"symptom_history": analysis_record}}
            )
        except Exception as e:
            print(f"❌ Error saving symptom analysis: {e}")
            return None

    def save_symptom_history(self, user_id, history_data):
        if self.db is None:
            print("⚠️ Database connection not established!")
            return None
        try:
            return self.db["symptom_history"].insert_one({
                "user_id": user_id,
                **history_data
            })
        except Exception as e:
            print(f"❌ Error saving symptom history: {e}")
            return None

    def get_symptom_history(self, user_id):
        if self.db is None:
            print("⚠️ Database connection not established!")
            return []
        try:
            return list(self.db["symptom_history"].find({"user_id": user_id}))
        except Exception as e:
            print(f"❌ Error retrieving symptom history: {e}")
            return []

    def get_user_health_history(self, user_id):
        if self.db is None:
            print("⚠️ Database connection not established!")
            return None
        user = self.db.users.find_one({"_id": ObjectId(user_id)})
        return user.get('health_records', []) if user else []

    def get_user_research_history(self, user_id):
        if self.db is None:
            print("⚠️ Database connection not established!")
            return None
        user = self.db.users.find_one({"_id": ObjectId(user_id)})
        return user.get('research_history', []) if user else []

    def get_user_wellness_data(self, user_id):
        if self.db is None:
            print("⚠️ Database connection not established!")
            return None
        user = self.db.users.find_one({"_id": ObjectId(user_id)})
        return user.get('wellness_data', []) if user else []

    def delete_user_and_data(self, user_id):
        try:
            self.db["users"].delete_one({"_id": ObjectId(user_id)})
            self.db["symptom_history"].delete_many({"user_id": user_id})
            self.db["wellness"].delete_many({"user_id": user_id})
            print(f"✅ Deleted user and related data for {user_id}")
            return True
        except Exception as e:
            print(f"❌ Error deleting user and data: {e}")
            return False
