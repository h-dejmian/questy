from flask import Flask, render_template, request, redirect, url_for, session
import data_handler
import util
import user_data_handler

app = Flask(__name__)
app.secret_key = b'\xd7S@C\xe00\xf8\x11\xefj\xf1\xbcN\xb1$\xd5'


@app.route("/list")
def list_all_questions():
    question_list = data_handler.get_data_by_type("question")
    if len(request.args) == 0:
        question_list = data_handler.get_data_by_type("question")
        return render_template("list.html", questions=question_list)
    else:
        order_by = request.args.get("order_by")
        order_direction = request.args.get("order_direction")
        question_list = data_handler.get_data_by_type("question", order_by, order_direction)
        return render_template("list.html", questions=question_list)


@app.route("/users")
def list_all_users():
    users = user_data_handler.get_all_users()
    return render_template("user-list.html", users=users)


@app.route('/tags')
def list_all_tags():
    tags = data_handler.get_data_by_type("tag")
    return render_template('tag-list.html', tags=tags)


@app.route("/question/<int:id>")
def view_question_by_id(id):
    question = data_handler.get_record_by_id(id, "question")
    data = util.get_question_related_data(id)
    data_handler.increment_column("question", "view_number", id)

    return render_template("question.html", question=question, answers=data['answers'], comments=data['comments'], tags=data['tags'])


@app.route("/add-question", methods=["GET", "POST"])
def add_question():
    if request.method == 'GET':
        return render_template("add-question.html")
    
    if request.method == 'POST':
        question = []
        question.append(request.form["title"])
        question.append(request.form["question"])

        question_id = data_handler.add_question(question)
        user_id = user_data_handler.get_user_id_by_name(session['user_name'])
        user_data_handler.bind_user_to_resource("question", question_id, user_id)
        
        return redirect(url_for("view_question_by_id", id=question_id))


@app.route("/question/<int:question_id>/add-answer", methods=["GET", "POST"])
def add_answer(question_id):
    if request.method == 'GET':
        return render_template("add-answer.html")
    
    if request.method == 'POST':
        answer = request.form["answer"]

        answer_id = data_handler.add_answer_to_question(question_id, answer)
        user_id = user_data_handler.get_user_id_by_name(session['user_name'])
        user_data_handler.bind_user_to_resource("answer", answer_id, user_id)

        return redirect(url_for("view_question_by_id", id=question_id))


@app.route("/question/<int:question_id>/new-comment", methods=["GET", "POST"])
def add_comment(question_id):
    if request.method == 'GET':
        return render_template("add-comment.html")
    
    if request.method == 'POST':
        comment = request.form["message"]

        comment_id = data_handler.add_comment_to_question(question_id, comment)
        user_id = user_data_handler.get_user_id_by_name(session['user_name'])
        user_data_handler.bind_user_to_resource("comment", comment_id, user_id)

        return redirect(url_for("view_question_by_id", id=question_id))
    

@app.route("/question/<int:id>/add-tag", methods=["GET", "POST"])
def add_tag_to_question(id):
    if request.method == 'GET':
        tags = data_handler.get_data_by_type("tag")
        return render_template("add-tag.html", id=id, tags=tags)
    
    if request.method == 'POST':
        tag = request.form["tag"]
        data_handler.add_tag_to_question(id, tag)

        return redirect(url_for("view_question_by_id", id=id))


@app.route("/question/<int:id>/delete-answer", methods=["GET"])
def delete_answer(id):
    question = data_handler.get_question_by_other_data_id(id, "answer")
    data_handler.delete_data_by_type(id, "answer")
    
    return redirect(url_for("view_question_by_id", id=question['id']))


@app.route("/comments/<int:comment_id>/delete-comment", methods=["GET"])
def delete_comment(comment_id):
    question = data_handler.get_question_by_other_data_id(comment_id, "comment")
    data_handler.delete_data_by_type(comment_id, "comment")
   
    return redirect(url_for("view_question_by_id", id=question['id']))


@app.route("/question/<question_id>/tag/<tag_id>/delete", methods=["GET"])
def delete_tag_from_question(tag_id, question_id):
    question = data_handler.get_question_by_tag_id(tag_id)
    data_handler.delete_tag_from_question(tag_id, question_id)
    
    return redirect(url_for("view_question_by_id", id=question_id))


@app.route("/question/<int:id>/delete-question", methods=["GET"])
def delete_question(id):
    data_handler.delete_question(id)

    question_list = data_handler.get_data_by_type("question")
    return render_template("list.html", questions=question_list)


@app.route("/question/<int:id>/edit-question", methods=["GET", "POST"])
def edit_question(id):
    if request.method == 'GET':
        user_question = data_handler.get_record_by_id(id, "question")

        title = user_question['title']
        question = user_question['message']
    
        return render_template("edit-question.html", question=question, title=title)
    
    if request.method == 'POST':
        user_question = data_handler.get_record_by_id(id, "question")

        user_question['title'] = request.form["title"]
        user_question['message'] = request.form["question"]
        data_handler.edit_question(user_question)

        return redirect(url_for("view_question_by_id", id=user_question['id']))


@app.route("/question/<int:id>/edit-answer", methods=["GET", "POST"])
def edit_answer(id):
    if request.method == 'GET':
        user_answer = data_handler.get_record_by_id(id, "answer")
        message = user_answer['message']
        return render_template("edit-answer.html", message=message)

    if request.method == 'POST':
        user_answer = data_handler.get_record_by_id(id, "answer")

        user_answer['message'] = request.form["message"]
        data_handler.edit_answer(user_answer)
        return redirect(url_for("view_question_by_id", id=user_answer['question_id']))
    
@app.route("/comments/<int:id>/edit-comment", methods=["GET", "POST"])
def edit_comment(id):
    if request.method == 'GET':
        user_comment = data_handler.get_record_by_id(id, "comment")
        message = user_comment['message']
        return render_template("edit-comment.html", message=message)

    if request.method == 'POST':
        user_comment = data_handler.get_record_by_id(id, "comment")

        user_comment['message'] = request.form["message"]
        data_handler.edit_comment(user_comment)
        data_handler.increment_column("comment", "edited_count", id)

        return redirect(url_for("view_question_by_id", id=user_comment['question_id']))


@app.route("/question/<int:id>/vote-up", methods=["GET"])
def vote_up_question(id):
    data_handler.vote_on_resource(id, "question", "+")
    user_data_handler.evaluate_reputation("question", id, "+")

    return list_all_questions()


@app.route("/question/<int:id>/vote-down", methods=["GET"])
def vote_down_question(id):
    data_handler.vote_on_resource(id, "question", "-")
    user_data_handler.evaluate_reputation("question", id, "-")

    return list_all_questions()


@app.route("/answer/<int:id>/vote-up", methods=["GET"])
def vote_up_answer(id):
    answer = data_handler.get_record_by_id(id, "answer")
    data_handler.vote_on_resource(id, "answer", "+")
    user_data_handler.evaluate_reputation("answer", id, "+")

    return view_question_by_id(answer['question_id'])


@app.route("/answer/<int:id>/vote-down", methods=["GET"])
def vote_down_answer(id):
    answer = data_handler.get_record_by_id(id, "answer")
    data_handler.vote_on_resource(id, "answer", "-")
    user_data_handler.evaluate_reputation("answer", id, "-")

    return view_question_by_id(answer['question_id'])


@app.route("/registration", methods=["GET", "POST"])
def register_user():
    if request.method == "POST":
        user_name = request.form['user_name']
        password = user_data_handler.hash_password(request.form['password'])
        user_data_handler.register_user(user_name, password)

        return redirect(url_for('main_page'))  
    else:    
        return render_template("registration.html")
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST':
       
        is_user_registered = user_data_handler.is_user_registered(request.form['user_name'])
        if is_user_registered:
            hashed_password = user_data_handler.get_user_hash_password(request.form['user_name'])
            passwrod_valid = user_data_handler.verify_password(request.form['password'], hashed_password)

            if passwrod_valid:
                session['user_name'] = request.form['user_name']
                session.permanent = True
                return redirect(url_for('main_page'))
            else:
                message = 'Wrong password'
        else:
            message = 'Wrong user'

    return render_template('login.html', message=message)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('user_name', None)
    return redirect(url_for('main_page'))


@app.route("/")
def main_page():
    questions = data_handler.get_five_latest_questions()
    return render_template("index.html", questions=questions)


@app.route("/bonus-questions")
def bonus_questions():
    return render_template('bonus_questions.html', questions=SAMPLE_QUESTIONS)


if __name__ == "__main__":
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
    )
