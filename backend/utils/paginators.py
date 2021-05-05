def paginate_questions(request, selection):
    QUESTIONS_PER_PAGE = 10
    body = request.get_json()
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in selection]
    return questions[start:end]