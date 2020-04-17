from flask_backend import call_queue, helper_accounts_collection, helper_behavior_collection, calls_collection
from flask_backend.database_scripts.call_scripts import dequeue
from flask_backend.database_scripts.hotline_scripts import enqueue
from flask_backend.support_functions import testing

from datetime import datetime, timedelta
from bson import ObjectId


test_helper = {
    'calls': [],
    'zip_code': '80000'
}

test_calls = {
    'A': {
        'timestamp_received': datetime.now(),
        'helper_id': 0, 'status': 'pending',
        'local': True,
        'zip_code': '80000'},
    'B': {
        'timestamp_received': datetime.now() - timedelta(seconds=32),
        'helper_id': 0, 'status': 'pending',
        'local': False},
    'C': {
        'timestamp_received': datetime.now() - timedelta(seconds=20),
        'helper_id': 0, 'status': 'pending',
        'local': True,
        'zip_code': '80000'},
    'D': {
        'timestamp_received': datetime.now() - timedelta(seconds=100),
        'helper_id': 0, 'status': 'pending',
        'local': False},
    'E': {
        'timestamp_received': datetime.now() - timedelta(seconds=88),
        'helper_id': 0, 'status': 'pending',
        'local': True,
        'zip_code': '80000'
    },
    'F': {
        'timestamp_received': datetime.now() - timedelta(seconds=0),
        'helper_id': 0, 'status': 'pending',
        'local': True,
        'zip_code': '90000'
    },
    'G': {
        'timestamp_received': datetime.now() - timedelta(seconds=40),
        'helper_id': 0, 'status': 'pending',
        'local': True,
        'zip_code': '90000'
    }
}


def check_dequeue_result(test_no, should_be, actual_response):
    if 'call_id' not in actual_response:
        actual = None
    else:
        actual = actual_response['call_id']

    result = {
        'name': f'Test {test_no} (dequeueing result)',
        'result': should_be == actual,
    }

    if should_be != actual:
        result.update({'details': f'{actual} (actual) != {should_be} (should be)'})

    return [result]


def check_helper_queue(test_no, should_be, helper_id):
    actual = helper_accounts_collection.find_one({'_id': ObjectId(helper_id)}, {'_id': 0, 'calls': 1})['calls']

    result = {
        'name': f'Test {test_no} (helper calls list)',
    }

    if testing.lists_match(should_be, actual):
        result.update({'result': True})
    else:
        result.update({
            'result': False,
            'details': f'{actual} != {should_be}'
        })

    return [result]


def check_call_record(test_no, call_id, helper_id):
    call_record = calls_collection.find_one({'_id': ObjectId(call_id)})

    if call_record is None:
        return [{
            'name': f'Test {test_no} (call record)',
            'result': False,
            'details': 'Record does not exist'
        }]

    results = []

    result_1 = {
        'name': f'Test {test_no} (call[\'helper_id\'])',
    }
    if call_record['helper_id'] == helper_id:
        result_1.update({'result': True})
    else:
        result_1.update({
            'result': False,
            'details': f'{call_record["helper_id"]} != {helper_id}'
        })
    results.append(result_1)

    result_2 = {
        'name': f'Test {test_no} (call[\'status\'])',
    }
    if call_record['status'] == 'accepted':
        result_2.update({'result': True})
    else:
        result_2.update({
            'result': False,
            'details': f'{call_record["status"]} != accepted'
        })
    results.append(result_2)

    result_3 = {
        'name': f'Test {test_no} (call[\'timestamp_accepted\'])',
    }
    if 'timestamp_accepted' in call_record:
        result_3.update({'result': True})
    else:
        result_3.update({
            'result': False,
            'details': f'key \'timestamp_accepted\' not in call record.'
        })
    results.append(result_3)

    return results


def check_helper_behavior_record(test_no, call_id, helper_id):
    behavior_record = helper_behavior_collection.find_one(
        {'call_id': ObjectId(call_id), 'helper_id': ObjectId(helper_id)},
        {'_id': 0})

    if behavior_record is None:
        return [{
            'name': f'Test {test_no} (behavior record)',
            'result': False,
            'details': 'Record does not exist'
        }]

    results = []

    result_1 = {
        'name': f'Test {test_no} (behavior[\'helper_id\'])',
    }
    if behavior_record['helper_id'] == helper_id:
        result_1.update({'result': True})
    else:
        result_1.update({
            'result': False,
            'details': f'{behavior_record["helper_id"]} != {helper_id}'
        })
    results.append(result_1)

    result_2 = {
        'name': f'Test {test_no} (behavior[\'call_id\'])',
    }
    if behavior_record['call_id'] == call_id:
        result_2.update({'result': True})
    else:
        result_2.update({
            'result': False,
            'details': f'{behavior_record["call_id"]} != {call_id}'
        })
    results.append(result_2)

    result_3 = {
        'name': f'Test {test_no} (behavior[\'status\'])',
    }
    if behavior_record['action'] == 'accepted':
        result_3.update({'result': True})
    else:
        result_3.update({
            'result': False,
            'details': f'{behavior_record["action"]} != accepted'
        })
    results.append(result_3)

    result_4 = {
        'name': f'Test {test_no} (behavior[\'timestamp\'])',
    }
    if 'timestamp' in behavior_record:
        result_4.update({'result': True})
    else:
        result_4.update({
            'result': False,
            'details': f'key \'timestamp\' not in call record.'
        })
    results.append(result_4)

    return results


def test_dequeue_local():
    timestamp_1 = datetime.now()

    calls_collection.delete_many({})
    call_queue.delete_many({})
    helper_behavior_collection.delete_many({})
    helper_accounts_collection.delete_many({})

    helper_id = helper_accounts_collection.insert_one(test_helper).inserted_id

    A = calls_collection.insert_one(test_calls['A']).inserted_id
    B = calls_collection.insert_one(test_calls['B']).inserted_id
    C = calls_collection.insert_one(test_calls['C']).inserted_id
    D = calls_collection.insert_one(test_calls['D']).inserted_id
    E = calls_collection.insert_one(test_calls['E']).inserted_id
    F = calls_collection.insert_one(test_calls['F']).inserted_id
    G = calls_collection.insert_one(test_calls['G']).inserted_id

    # Should be E -> C -> A (others shall be ignored)

    print('IDS (LOCAL)')
    call_ids = {'A': A, 'B': B, 'C': C, 'D': D, 'E': E, 'F': F, 'G': G}

    for key in call_ids:
        enqueue.enqueue(call_ids[key])
        print(f'call_id_{key} = {call_ids[key]}')

    results = []

    results += testing.check_queues(1, [A, C, G, F, E], [B, D, E, G], [D, E])

    dequeue_1 = dequeue.dequeue(helper_id, only_local_calls=True)
    results += check_dequeue_result(2, E, dequeue_1)
    results += testing.check_queues(3, [A, C, G, F], [B, D, G], [D])
    results += check_helper_queue(4, [E], helper_id)
    results += check_call_record(5, E, helper_id)

    dequeue_2 = dequeue.dequeue(helper_id, only_local_calls=True)
    results += check_dequeue_result(6, C, dequeue_2)
    results += testing.check_queues(7, [A, G, F], [B, D, G], [D])
    results += check_helper_queue(8, [E, C], helper_id)
    results += check_call_record(9, C, helper_id)

    dequeue_3 = dequeue.dequeue(helper_id, only_local_calls=True)
    results += check_dequeue_result(10, A, dequeue_3)
    results += testing.check_queues(11, [G, F], [B, D, G], [D])
    results += check_helper_queue(12, [E, C, A], helper_id)
    results += check_call_record(13, A, helper_id)

    dequeue_4 = dequeue.dequeue(helper_id, only_local_calls=True)
    dequeue_4_result = {
        'name': 'Test 14',
        'result': dequeue_4['status'] == 'currently no call available'
    }
    if not dequeue_4_result['result']:
        dequeue_4_result.update({'details': f'actual status = {dequeue_4}'})
    results += [dequeue_4_result]

    calls_collection.delete_many({})
    call_queue.delete_many({})
    helper_behavior_collection.delete_many({})
    helper_accounts_collection.delete_many({})

    return results


def test_dequeue_global():
    timestamp_1 = datetime.now()

    calls_collection.delete_many({})
    call_queue.delete_many({})
    helper_behavior_collection.delete_many({})
    helper_accounts_collection.delete_many({})

    helper_id = helper_accounts_collection.insert_one(test_helper).inserted_id

    A = calls_collection.insert_one(test_calls['A']).inserted_id
    B = calls_collection.insert_one(test_calls['B']).inserted_id
    C = calls_collection.insert_one(test_calls['C']).inserted_id
    D = calls_collection.insert_one(test_calls['D']).inserted_id
    E = calls_collection.insert_one(test_calls['E']).inserted_id
    F = calls_collection.insert_one(test_calls['F']).inserted_id
    G = calls_collection.insert_one(test_calls['G']).inserted_id

    # Should be D -> B (others shall be ignored)

    print('IDS (GLOBAL)')
    call_ids = {'A': A, 'B': B, 'C': C, 'D': D, 'E': E, 'F': F, 'G': G}

    for key in call_ids:
        enqueue.enqueue(call_ids[key])
        print(f'call_id_{key} = {call_ids[key]}')

    results = []

    results += testing.check_queues(15, [A, C, G, F, E], [B, D, E, G], [D, E])

    dequeue_1 = dequeue.dequeue(helper_id, only_global_calls=True)
    results += check_dequeue_result(16, D, dequeue_1)
    results += testing.check_queues(17, [A, C, G, F, E], [B, E, G], [E])
    results += check_helper_queue(18, [D], helper_id)
    results += check_call_record(19, D, helper_id)

    dequeue_2 = dequeue.dequeue(helper_id, only_global_calls=True)
    results += check_dequeue_result(20, B, dequeue_2)
    results += testing.check_queues(21, [A, C, G, F, E], [E, G], [E])
    results += check_helper_queue(22, [D, B], helper_id)
    results += check_call_record(23, B, helper_id)

    dequeue_3 = dequeue.dequeue(helper_id, only_global_calls=True)
    dequeue_3_result = {
        'name': 'Test 24',
        'result': dequeue_3['status'] == 'currently no call available'
    }
    if not dequeue_3_result['result']:
        dequeue_3_result.update({'details': f'actual status = {dequeue_3}'})
    results += [dequeue_3_result]

    calls_collection.delete_many({})
    call_queue.delete_many({})
    helper_behavior_collection.delete_many({})
    helper_accounts_collection.delete_many({})

    return results


def test_dequeue_everywhere():
    timestamp_1 = datetime.now()

    calls_collection.delete_many({})
    call_queue.delete_many({})
    helper_behavior_collection.delete_many({})
    helper_accounts_collection.delete_many({})

    helper_id = helper_accounts_collection.insert_one(test_helper).inserted_id

    A = calls_collection.insert_one(test_calls['A']).inserted_id
    B = calls_collection.insert_one(test_calls['B']).inserted_id
    C = calls_collection.insert_one(test_calls['C']).inserted_id
    D = calls_collection.insert_one(test_calls['D']).inserted_id
    E = calls_collection.insert_one(test_calls['E']).inserted_id
    F = calls_collection.insert_one(test_calls['F']).inserted_id
    G = calls_collection.insert_one(test_calls['G']).inserted_id

    # Should be D -> E -> C -> A -> G -> B -> F shall be ignored)

    print('IDS (EVERYWHERE)')
    call_ids = {'A': A, 'B': B, 'C': C, 'D': D, 'E': E, 'F': F, 'G': G}

    for key in call_ids:
        enqueue.enqueue(call_ids[key])
        print(f'call_id_{key} = {call_ids[key]}')

    results = []

    results += testing.check_queues(25, [A, C, G, F, E], [B, D, E, G], [D, E])

    '''
    results += check_dequeue_result(2, D, dequeue.dequeue(helper_id))
    results += check_dequeue_result(3, E, dequeue.dequeue(helper_id))
    results += check_dequeue_result(4, C, dequeue.dequeue(helper_id))
    results += check_dequeue_result(5, A, dequeue.dequeue(helper_id))
    results += check_dequeue_result(6, G, dequeue.dequeue(helper_id))
    results += check_dequeue_result(7, B, dequeue.dequeue(helper_id))

    return results
    '''

    dequeue_1 = dequeue.dequeue(helper_id)
    results += check_dequeue_result(26, D, dequeue_1)
    results += testing.check_queues(27, [A, C, G, F, E], [B, E, G], [E])
    results += check_helper_queue(28, [D], helper_id)
    results += check_call_record(29, D, helper_id)

    dequeue_2 = dequeue.dequeue(helper_id)
    results += check_dequeue_result(30, E, dequeue_2)
    results += testing.check_queues(31, [A, C, G, F], [B, G], [])
    results += check_helper_queue(32, [D, E], helper_id)
    results += check_call_record(33, E, helper_id)

    dequeue_3 = dequeue.dequeue(helper_id)
    results += check_dequeue_result(34, C, dequeue_3)
    results += testing.check_queues(35, [A, G, F], [B, G], [])
    results += check_helper_queue(36, [D, E, C], helper_id)
    results += check_call_record(37, C, helper_id)

    dequeue_4 = dequeue.dequeue(helper_id)
    results += check_dequeue_result(38, A, dequeue_4)
    results += testing.check_queues(39, [G, F], [B, G], [])
    results += check_helper_queue(40, [D, E, C, A], helper_id)
    results += check_call_record(41, A, helper_id)

    dequeue_5 = dequeue.dequeue(helper_id)
    results += check_dequeue_result(42, G, dequeue_5)
    results += testing.check_queues(43, [F], [B], [])
    results += check_helper_queue(44, [D, E, C, A, G], helper_id)
    results += check_call_record(45, G, helper_id)

    dequeue_6 = dequeue.dequeue(helper_id)
    results += check_dequeue_result(46, B, dequeue_6)
    results += testing.check_queues(47, [F], [], [])
    results += check_helper_queue(48, [D, E, C, A, G, B], helper_id)
    results += check_call_record(49, B, helper_id)

    dequeue_6 = dequeue.dequeue(helper_id)
    dequeue_6_result = {
        'name': 'Test 50',
        'result': dequeue_6['status'] == 'currently no call available'
    }
    if not dequeue_6_result['result']:
        dequeue_6_result.update({'details': f'actual status = {dequeue_6}'})
    results += [dequeue_6_result]

    calls_collection.delete_many({})
    call_queue.delete_many({})
    helper_behavior_collection.delete_many({})
    helper_accounts_collection.delete_many({})

    return results


if __name__ == '__main__':
    results = test_dequeue_local()
    results += test_dequeue_global()
    results += test_dequeue_everywhere()

    for result in results:
        print(result)
