
from flask_backend import admin_accounts_collection
from flask_backend.support_functions import tokening


def add_admin_account(email, password):
    new_admin = {
        'email': email,
        'hashed_password': tokening.hash_password(password),
    }
    admin_accounts_collection.insert_one(new_admin)


if __name__ == '__main__':
    # add_admin_account(ADMIN_EMAIL, ADMIN_PASSWORD)
    pass
