import database_common
import time
import bcrypt

def hash_password(plain_text_password):
    hashed_bytes = bcrypt.hashpw(plain_text_password.encode('utf-8'), bcrypt.gensalt())
    return hashed_bytes.decode('utf-8')


def verify_password(plain_text_password, hashed_password):
    hashed_bytes_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_bytes_password)

@database_common.connection_handler
def register_user(cursor, username, password):
    query = f"""
            INSERT INTO users (user_name, user_password, registration_date, reputation)
            values('{username}', '{password}', NOW(), 0)
            """
    cursor.execute(query)


@database_common.connection_handler
def is_user_registered(cursor, user_name):
    query = f"""
            SELECT *
            FROM users
            WHERE user_name = '{user_name}'  
            """
    cursor.execute(query)
    if cursor.fetchone() == None:
        return False
    else:
        return True
    

@database_common.connection_handler
def get_user_id_by_name(cursor, name):
    query = f"""
            SELECT id
            FROM users
            WHERE user_name = '{name}'  
            """
    cursor.execute(query)
    result = cursor.fetchone()
    return result['id']


@database_common.connection_handler
def get_user_id_by_resource(cursor, resource_type, resource_id):
    query = f"""
            SELECT user_id
            FROM {resource_type}
            WHERE id = {resource_id}
            """
    cursor.execute(query)
    result = cursor.fetchone()
    return result['user_id']


@database_common.connection_handler
def bind_user_to_resource(cursor, resource_type, id, user_id):
    query = f"""
            UPDATE {resource_type}
            SET user_id = {user_id}
            WHERE id = {id}
            """
    cursor.execute(query)

    
@database_common.connection_handler
def get_user_hash_password(cursor, user_name):
    query = f"""
            SELECT user_password
            FROM users
            WHERE user_name = '{user_name}'  
            """
    cursor.execute(query)
    result = cursor.fetchone()
    return result['user_password']


@database_common.connection_handler
def get_all_users(cursor):
    query = f"""
            SELECT *
            FROM users 
            """
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def evaluate_reputation(cursor, resource_type, resource_id, sign):
    current_vote_value = get_vote_value(resource_type, resource_id)
    user_id = get_user_id_by_resource(resource_type, resource_id)

    factor = 0
    modify = False

    if resource_type == "question" and current_vote_value == 5 and sign == "+":
        factor = 1
        modify = True
    if resource_type == "question" and current_vote_value == 5 and sign == "-":
        factor = -1
        modify = True
    if resource_type == "answer" and current_vote_value == 10 and sign == "+":
        factor = 1
        modify = True
    if resource_type == "answer" and current_vote_value == 10 and sign == "-":
        factor = -1
        modify = True

    if modify:
        query = f"""
                UPDATE users
                SET reputation = reputation {sign} {factor}
                WHERE id = {user_id}
                """
        cursor.execute(query)


@database_common.connection_handler
def get_vote_value(cursor, resource_type, id):
    query = f"""
            SELECT vote_number
            FROM {resource_type}
            WHERE id = {id}
            """
    cursor.execute(query)
    result = cursor.fetchone()
    return result['vote_number']


