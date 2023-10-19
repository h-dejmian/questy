import database_common
import time
import user_data_handler


@database_common.connection_handler
def get_data_by_type(cursor, type, order_by="submission_time", order_direction="asc"):
    if type == "tag":
        query = """
            SELECT * 
            FROM tag
            """
    else:
        query = f"""
                SELECT * 
                FROM {type}
                ORDER BY {order_by} {order_direction}
                """
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_five_latest_questions(cursor):
    query = """
            SELECT * 
            FROM question
            ORDER BY submission_time desc
            LIMIT 5
            """
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_data_by_question_id(cursor, question_id, type):
    query = f"""
            SELECT * 
            FROM {type}
            WHERE question_id = {question_id}
            """
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_all_tags_to_question(cursor, question_id):
    query = f"""
            SELECT tag.id, name 
            FROM tag
            JOIN question_tag AS qt ON tag.id = qt.tag_id
            JOIN question AS q ON qt.question_id = q.id
            WHERE q.id = {question_id}
            """
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_record_by_id(cursor, id, type):
    query = f"""
            SELECT * 
            FROM {type}
            WHERE id = {id}
            """
    cursor.execute(query)
    return cursor.fetchone()


@database_common.connection_handler
def get_question_by_other_data_id(cursor, data_id, type):
    query = f"""
            SELECT * 
            FROM question
            WHERE id = (SELECT question_id FROM {type} WHERE id = {data_id})
            """
    cursor.execute(query)
    return cursor.fetchone()


@database_common.connection_handler
def get_question_by_tag_id(cursor, tag_id):
    query = f"""
            SELECT q.id, q.submission_time, q.view_number, q.vote_number, q.title, q.message, q.image 
            FROM question_tag AS qt 
            JOIN question AS q ON qt.question_id = q.id
            WHERE qt.tag_id = {tag_id}
            """
    cursor.execute(query)
    return cursor.fetchone()


@database_common.connection_handler
def add_question(cursor, question):
    query = f"""
            INSERT INTO question (submission_time, view_number, vote_number, title, message)
	values(NOW(), 0, 0, '{question[0]}', '{question[1]}')
            """
    cursor.execute(query)

    query = f"""
            SELECT id FROM question WHERE title = '{question[0]}' AND message = '{question[1]}'
            """
    cursor.execute(query)
    result = cursor.fetchone()

    return result['id']



@database_common.connection_handler
def add_answer_to_question(cursor, question_id, answer):
    query = f"""
            INSERT INTO answer (submission_time, vote_number, question_id, message)
	values(NOW(), 0, {question_id}, '{answer}')
            """
    cursor.execute(query)

    query = f"""
            SELECT id 
            FROM answer
            WHERE question_id = {question_id} AND message = '{answer}'
            """
    cursor.execute(query)
    result = cursor.fetchone()
    return result['id']


@database_common.connection_handler
def add_comment_to_question(cursor, question_id, comment):
    query = f"""
            INSERT INTO comment (question_id, answer_id, message, submission_time, edited_count)
	values({question_id}, NULL, '{comment}', NOW(), 0)
            """
    cursor.execute(query)

    query = f"""
            SELECT id 
            FROM comment
            WHERE question_id = {question_id} AND message = '{comment}'
            """
    cursor.execute(query)
    result = cursor.fetchone()
    return result['id']


@database_common.connection_handler
def add_tag_to_question(cursor, question_id, tag_name):
    cursor.execute(f"SELECT * FROM tag WHERE name = '{tag_name}'")
    tag = cursor.fetchone()

    if tag == None:
        tag = create_new_tag(tag_name)

    query = f"""
            SELECT * FROM question_tag WHERE question_id = {question_id} AND tag_id = {tag['id']}
            """
    cursor.execute(query)
    result = cursor.fetchone()

    if result != None:
        return None
   
    query = f"""
            INSERT INTO question_tag(question_id, tag_id)
            values({question_id}, {tag['id']} )
            """
    cursor.execute(query)
    increment_column("tag", "marked_questions", tag['id'])


@database_common.connection_handler
def create_new_tag(cursor, tag_name):
    query = f"""
            INSERT INTO tag(name)
            values('{tag_name}')
            """
    cursor.execute(query)
    cursor.execute(f"SELECT * FROM tag WHERE name = '{tag_name}'")
    return cursor.fetchone()


@database_common.connection_handler
def delete_data_by_type(cursor, id, type):
    query = f"""
            DELETE  
            FROM {type}
            WHERE id = {id}
            """
    cursor.execute(query)


@database_common.connection_handler
def delete_tag_from_question(cursor, tag_id, question_id):
    query = f"""
            DELETE  
            FROM question_tag
            WHERE tag_id = {tag_id} AND question_id = {question_id}
            """
    cursor.execute(query)
    increment_column("tag", "marked_questions", tag_id, "-")


@database_common.connection_handler
def delete_question(cursor, question_id):
    columns_to_del = ["answer", "question_tag", "comment"]

    for col in columns_to_del:
        query = f"""
            DELETE 
            FROM "{col}"
            WHERE question_id = {question_id}
            """
        cursor.execute(query)

    query = f"""
            DELETE 
            FROM question
            WHERE id = {question_id}
            """
    cursor.execute(query)


@database_common.connection_handler
def edit_question(cursor, question):
    query = f"""
            UPDATE question 
            SET title = '{question['title']}', message = '{question['message']}'
            WHERE id = {question['id']}
            """
    cursor.execute(query)


@database_common.connection_handler
def edit_answer(cursor, answer):
    query = f"""
            UPDATE answer 
            SET message = '{answer['message']}'
            WHERE id = {answer['id']}
            """
    cursor.execute(query)


@database_common.connection_handler
def edit_comment(cursor, comment):
    query = f"""
            UPDATE comment 
            SET message = '{comment['message']}'
            WHERE id = {comment['id']}
            """
    cursor.execute(query)


@database_common.connection_handler
def increment_column(cursor, table, column, id, sign="+"):
    query = f"""
            UPDATE {table}
            SET {column} = {column} {sign} 1
            WHERE id = {id}
            """
    cursor.execute(query)


@database_common.connection_handler
def vote_on_resource(cursor, id, type, sign):
    data = get_record_by_id(id, type)

    if sign == "+":
        factor = 1
    else:
        factor = -1
    
    query = f"""
            UPDATE {type} 
            SET vote_number = '{data['vote_number']}' + {factor}
            WHERE id = {id}
            """
    cursor.execute(query)







