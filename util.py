import data_handler

def get_question_related_data(question_id):
    answers = data_handler.get_data_by_question_id(question_id, "answer")
    comments = data_handler.get_data_by_question_id(question_id, "comment")
    tags = data_handler.get_all_tags_to_question(question_id)
    return {"answers" : answers, "comments" : comments, "tags" : tags }