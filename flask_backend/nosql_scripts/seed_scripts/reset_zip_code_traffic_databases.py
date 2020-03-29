
from flask_backend import zip_code_helpers_collection, zip_code_callers_collection, zip_code_calls_collection
from flask_backend import zip_codes_collection

import pymongo


def reset_zip_code_traffic_databases():
    
    # 1) empty each collection
    zip_code_helpers_collection.delete_many({})
    zip_code_callers_collection.delete_many({})
    zip_code_calls_collection.delete_many({})
    
    # 2) Get all possible zip_codes
    zip_codes = list(zip_codes_collection.find({}, {"_id": 0, "zip_code": 1}))
    
    # 3) Generate documents to be inserted
    helpers_documents = []
    callers_documents = []
    calls_documents = []

    for zip_code in zip_codes:
        helpers_documents.append({"zip_code": zip_code["zip_code"], "helpers": []})
        callers_documents.append({"zip_code": zip_code["zip_code"], "callers": []})
        calls_documents.append({"zip_code": zip_code["zip_code"], "pending_calls": []})

    # 4) Insert documents
    zip_code_helpers_collection.insert_many(helpers_documents)
    zip_code_callers_collection.insert_many(callers_documents)
    zip_code_calls_collection.insert_many(calls_documents)


def index_zip_code_traffic_databases():
    zip_code_helpers_collection.create_index([('zip_code', pymongo.ASCENDING)], unique=True)
    zip_code_callers_collection.create_index([('zip_code', pymongo.ASCENDING)], unique=True)
    zip_code_calls_collection.create_index([('zip_code', pymongo.ASCENDING)], unique=True)


if __name__ == "__main__":
    reset_zip_code_traffic_databases()
    index_zip_code_traffic_databases()



