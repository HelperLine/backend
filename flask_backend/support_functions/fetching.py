
from flask_backend import zip_codes_collection


def get_adjacent_zip_codes(zip_code):
    # The returned list should include
    #  * all zip codes in a radius of 5km (at most 20 zip codes)
    #  * at least 8 zip codes (some may be more than 5km away)

    raw_adjacency_list = zip_codes_collection.find_one({'zip_code': zip_code}, {'_id': 0, 'adjacent_zip_codes': 1})

    if raw_adjacency_list is None:
        return [zip_code]

    zip_codes = [(record['zip_code'], record['distance']) for record in raw_adjacency_list['adjacent_zip_codes']]

    if len(zip_codes) <= 8:
        return [record[0] for record in zip_code] + [zip_code]

    zip_codes.sort(key=lambda x: x[1])

    # Take at least 8 zip codes
    zip_code_final = zip_codes[0:8]
    zip_codes = zip_codes[8:]

    # Add all the remaining zip codes closer than 5km
    zip_codes = list(filter(lambda x: x[1] < 5, zip_codes))
    zip_code_final += zip_codes

    return [record[0] for record in zip_code_final] + [zip_code]
