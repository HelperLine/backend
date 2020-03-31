

def records_to_list(records):
    # in: [{"call_id": "A"}, {"call_id": "B"}]
    # out: ["A", "B"]
    return [record["call_id"] for record in records]


def lists_match(list_1, list_2):
    # duplicate check
    new_list_1 = []
    new_list_2 = []

    # equality check
    for element_1 in list_1:
        if element_1 not in new_list_1:
            new_list_1.append(element_1)

        if element_1 not in list_2:
            return False

    for element_2 in list_2:
        if element_2 not in new_list_2:
            new_list_2.append(element_2)

        if element_2 not in list_1:
            return False

    return (len(list_1) == len(new_list_1)) and (len(list_2) == len(new_list_2))
