
from flask_backend import helper_accounts_collection, status
from bson import ObjectId
from datetime import datetime


def set_online(helper_id,
               filter_type_local=None, filter_type_global=None,
               filter_language_german=None, filter_language_english=None):

    if None in [filter_type_local, filter_type_global, filter_language_german, filter_language_english]:
        return status("All filters must be set")

    helper = helper_accounts_collection.find_one({"_id": ObjectId(helper_id)})

    if helper["phone_number"] == "" or not helper["phone_number_verified"] or not helper["phone_number_confirmed"]:
        return status("Phone number not confirmed")

    helper_update = {
        'filter_type_local': filter_type_local,
        'filter_type_global': filter_type_global,
        'filter_language_german': filter_language_german,
        'filter_language_english': filter_language_english,

        'online': True,
        'last_switched_online': datetime.now(),
    }
    helper_accounts_collection.update_one({"_id": ObjectId(helper_id)}, {"$set": helper_update})


def set_offline(helper_id):
    helper_update = {
        'online': False,
    }
    helper_accounts_collection.update_one({"_id": ObjectId(helper_id)}, {"$set": helper_update})
