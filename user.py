import pandas as pd
from app.mongodb_util import init_mongo
import os

# User class for CSV generation
class User:
    def __init__(self):
        self.collection = init_mongo()
    # Creates and stores the CSV file in the given path
    def save_to_csv(self):
        path = os.path.join("data", "survey_data.csv")
        os.makedirs(os.path.dirname(path), exist_ok=True)

        data = list(self.collection.find({}, {'_id': 0}))
        flat_data = []
        for entry in data:
            record = {
                'age': entry['age'],
                'gender': entry['gender'],
                'total_income': entry['total_income']
            }
            record.update(entry['expenses'])
            flat_data.append(record)
        df = pd.DataFrame(flat_data)
        df.to_csv(path, index=False)
        print(f"Data exported to {path}")
    
if __name__ == '__main__':
    user = User()
    # Export data
    user.save_to_csv()
