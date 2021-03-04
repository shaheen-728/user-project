import datetime
import hashlib
import uuid
import functools
import logging
import json
from flask import jsonify, abort
from .extensions import g
from .tag.models import Tag, SubTag, TagDomain, Domain
from .user.models import Users
from datetime import timedelta



def convert_list_to_dict(lst, key_name, appendtype ='list'):
    obj = {}
    if appendtype == 'list':
        for i in lst:
            if key_name not in i:
                obj[i[key_name]] = []
            obj[i[key_name]].append(i)
    else:
        for i in lst:
            obj[i[key_name]] = i
        return obj


def hash_password(password):
    salt = "admin"
    one_time_hash = hashlib.sha256(str(salt + password).encode('utf-8')).hexdigest()
    return one_time_hash


def create(create_obj, id=None, created_at=None):
    if not id:
        uuid_id = uuid.uuid4()
        create_obj.id = uuid_id
    else:
        create_obj.id = id
    if not created_at:
        create_obj.created_at = datetime.datetime.now()
    else:
        create_obj.created_at = created_at
    g.session.add(create_obj)
    g.session.commit()


def update(updated_object):
    g.session.merge(updated_object)
    g.session.commit()
    return updated_object


def delete(delete_obj):
    g.session.delete(delete_obj)
    g.session.commit()

def search_api(search_obj, entity):
    return fetch_list(entity, search_obj)


def bad_request(message, status_code):
    response = jsonify({'message': message})
    response.status_code = status_code
    return response


def bulk_create(obj_list, entity):
    list_obj = []
    for each_object in obj_list:
        if entity == Users:
            each_object["password"] = hash_password(each_object["password"])
        create_obj = entity(**each_object)
        uuid_id = uuid.uuid4()
        create_obj.id = uuid_id
        create_obj.created_at = datetime.datetime.now()
        create_obj.created_by = g.user.id if g.get('user') else None
        list_obj.append(create_obj)
    g.session.add_all(list_obj)
    g.session.commit()
    return list_obj


def fetch_list(entity, constraint_list):
    object_list = g.session.query(entity).filter_by(**constraint_list).all()
    json_list = [serialize_to_json(i) for i in object_list]
    return json_list


def fetch(entity, constraint_list):
    obj = g.session.query(entity).filter_by(**constraint_list).first()
    if obj:
        obj = serialize_to_json(obj)
    return obj


def fetch_obj(entity, constraint_list=None):
    """
    Gets the first object from the database.
    :param entity: Basically the table from which data needs to be extracted.
    :param constraint_list: It is actually a dict of the type {"id" :1}
    :return: The object if one is found else none
    """
    obj = g.session.query(entity)
    if constraint_list:
        obj = obj.filter_by(**constraint_list)
    return obj.first()


def fetch_all_obj(entity, constraint_list=None):
    """
    Gets all the objects from the database.
    :param entity: Basically the table from which data needs to be extracted.
    :param constraint_list: It is actually a dict of the type {"name" :"Bitcoin"}
    :return: The serialized objects list.
    """
    object_list = g.session.query(entity)
    if constraint_list:
        object_list = object_list.filter_by(**constraint_list)
    return object_list.all()


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            # if the obj is uuid, we simply return the value of uuid
            return str(obj)
        return json.JSONEncoder.default(self, obj)


def serialize_to_json(entity, many=False, exclude=[]):
    """
    Serialize a entity into json
    :param entity: The entity that needs to be serialized
    :param many: Should be set to True if obj is a collection so that the object
     will be serialized to a list.
    :param exclude: List of fields in marshmallow schema to exclude when dumping.
    :return: serialized entity
    """
    entity_name = entity.__class__.__name__
    entity_serializer = entity_name + 'Schema'
    entity_serializer = globals()[entity_serializer](exclude=exclude)
    return json.loads(entity_serializer.dumps(entity, many=many, cls=UUIDEncoder).data)


def create_logger():
    logger = logging.getLogger("example_logger")
    logger.setLevel(logging.INFO)

    fh = logging.FileHandler("/var/log/projectq.log")

    fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(fmt)
    fh.setFormatter(formatter)

    logger.addHandler(fh)
    return logger


def exception(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        # logger = create_logger()
        return function(*args, **kwargs)
        # try:
        #     pass
        # except Exception as ex:
        #     err = "There was an exception in  "
        #     err += function.__name__
        #     logger.exception(err)
        #     abort(400, {'message': str(ex)})

    return wrapper


def admin_api(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        if g.restricted_endpoint:
            if g.user.user_type != "Admin":
                abort(403)
        return function(*args, **kwargs)
    return wrapper


def get_start_week_datetime(date_time):
    date_obj = date_time.date()
    start_week = date_obj - timedelta(days=date_obj.weekday())
    return start_week


def get_start_month_datetime(date_time):
    date_obj = date_time.date()
    start_month = date_obj - timedelta(date_obj.day-1)
    return start_month


def get_str_from_uuid_column(obj, return_type='list'):
    if return_type == 'set':
        return {str(x[0]) for x in obj}
    return [str(x[0]) for x in obj]


def paginate_query(sql_query, page_no, page_size):
    return sql_query.limit(page_size).offset(
        (page_no - 1) * page_size)


def paginate_list(my_list, page_no, page_size):
    starting_elem = (page_no-1)*page_size
    last_elem = page_no*page_size
    if len(my_list) <= starting_elem:
        return []
    if len(my_list) <= last_elem:
        return list[starting_elem:]
    return list[starting_elem:last_elem]


def convert_tuple_to_key_list_dict(tuple_obj, append = 'list'):
    final_dict = {}
    for curr_entry in tuple_obj:
        if append == 'list':
            if curr_entry[0] not in final_dict:
                final_dict[curr_entry[0]] = []
            final_dict[curr_entry[0]].append(curr_entry[1])
        elif append == 'first':
            if curr_entry[0] not in final_dict:
                final_dict[curr_entry[0]] = curr_entry[1]
    return final_dict


def convert_tuple_to_space_separated_text_dict(tuple_obj):
    final_dict = {}
    for curr_entry in tuple_obj:
        if curr_entry[0] not in final_dict:
            final_dict[curr_entry[0]] = ''
        final_dict[curr_entry[0]] = final_dict[curr_entry[0]] + ' ' + curr_entry[1]
    return final_dict


def add_strings_with_none(str1, str2):
    if str1 is None:
            return str2
    if str2 is None:
        return str1
    return str1 + ' ' + str2


def add_lists_with_none(list1, list2):
    if list1 is None or list1 == ['None']:
        if list2 is None or list2 == ['None']:
            return []
        return list2
    if list2 is None or list2 == ['None']:
        return list1
    return list1 + list2


def dict_array_to_dict_of_value_arrays(my_list, key_col, value_col, none=True):
    new_dict = {}
    for curr_element in my_list:
        if curr_element[key_col] not in new_dict.keys():
            new_dict[curr_element[key_col]] = []
        if curr_element[value_col] == None and none == True:
            continue
        new_dict[curr_element[key_col]].append(curr_element[value_col])
    return new_dict


def get_question_options_util(question_ids):
    option_data = g.session.query(Option.question_id, Option.option_text).filter \
        (Option.question_id.in_(question_ids)).all()
    option_data = [(str(x[0]), x[1]) for x in option_data]
    options_dict = convert_tuple_to_space_separated_text_dict(option_data)
    return options_dict


def test_admin(user_id):
    user_type = fetch_obj(Users, {'id': user_id}).user_type
    return user_type == 'Admin'


def get_domains_by_tags(tag_ids, tag_dict = False):
    if tag_dict:
        tag_domain_query = g.session.query(TagDomain)
    else:
        tag_domain_query = g.session.query(TagDomain.domain_id)
    if tag_ids is not None:
        tag_domain_query = tag_domain_query.filter(TagDomain.tag_id.in_(tag_ids))
    if tag_dict:
        domain_by_tag_dict= {}
        tag_domains = tag_domain_query.all()
        for tag_domain in tag_domains:
            tag_id = str(tag_domain.tag_id)
            if tag_id not in domain_by_tag_dict:
                domain_by_tag_dict[tag_id] = []
            domain_by_tag_dict[tag_id].append(tag_domain.domain_id)
        return domain_by_tag_dict
    domain_ids = [str(x[0]) for x in tag_domain_query.all()]
    domain_list = [serialize_to_json(x) for x in g.session.query(Domain).filter(Domain.id.in_(domain_ids)).all()]
    return domain_list


def group_pairs_list(input_list):
    all_keys = set([x[0] for x in input_list])
    elements_dict = {}
    for curr_key in all_keys:
        elements_dict[str(curr_key)] = []
    for pair in input_list:
        elements_dict[str(pair[0])].append(pair[1])
    return elements_dict