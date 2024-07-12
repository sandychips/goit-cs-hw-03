
from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient("mongodb://localhost:27017/")
db = client["task_management"]
collection = db["cats"]

# Додавання прикладного документа
collection.insert_one({
    "name": "barsik",
    "age": 3,
    "features": ["ходить в капці", "дає себе гладити", "рудий"]
})

# Читання всіх записів
def read_all():
    for cat in collection.find():
        print(cat)

# Читання запису за ім'ям
def read_by_name(name):
    cat = collection.find_one({"name": name})
    print(cat)

# Оновлення віку за ім'ям
def update_age_by_name(name, age):
    collection.update_one({"name": name}, {"$set": {"age": age}})

# Додавання нової характеристики
def add_feature_by_name(name, feature):
    collection.update_one({"name": name}, {"$push": {"features": feature}})

# Видалення запису за ім'ям
def delete_by_name(name):
    collection.delete_one({"name": name})

# Видалення всіх записів
def delete_all():
    collection.delete_many({})

# Приклади виклику функцій
if __name__ == "__main__":
    read_all()
    read_by_name("barsik")
    update_age_by_name("barsik", 5)
    add_feature_by_name("barsik", "любит гратися з дітьми")
    delete_by_name("barsik")
    delete_all()
