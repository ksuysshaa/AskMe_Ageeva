from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render

TAGS = [
    {
        "id": i,
        "title": f"Tag {i}",
    } for i in range(5)
]

MEMBERS = [
    {
        "id": i,
        "title": f"Member {i}",
    } for i in range(5)
]

QUESTIONS = [
    {
        "id": i,
        "title": f"Question {i}",
        "text": f"This is question number {i}",
        "tag": TAGS[i % 3].get('name'),
        "tagId": i % 3
    } for i in range(100)
]

PER_PAGE = 10

def paginate(objects, request, per_page=PER_PAGE):
    try:
        page_num = int(request.GET.get('page', 1))
        paginator = Paginator(objects, per_page)
        page_obj = paginator.page(page_num)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return page_obj


# Create your views here.


def index(request):
    page_obj = paginate(QUESTIONS, request, PER_PAGE)
    return render(request, 'index.html', {"questions": page_obj, "members": MEMBERS, "tags": TAGS})


def hot(request):
    page_obj = paginate(QUESTIONS, request, PER_PAGE)
    return render(request, 'hot.html', {"questions": page_obj, "members": MEMBERS, "tags":  TAGS})


def question(request, question_id):
    question = QUESTIONS[question_id]
    answers = [
        {
            'id': i,
            'title': f'Answer {i}',
            'content': f'Answer text {i}'
        } for i in range(30)
    ]
    answers_page_obj = paginate(answers, request, PER_PAGE)
    return render(request, 'question.html', {"question": question, "answers": answers_page_obj, "members": MEMBERS, "tags": TAGS})


def ask(request):
    return render(request, 'ask.html', {"questions": QUESTIONS, "members": MEMBERS, "tags": TAGS})


def login(request):
    return render(request, 'login.html', {"members": MEMBERS, "tags": TAGS})


def signup(request):
    return render(request, 'signup.html', {"members": MEMBERS, "tags": TAGS})


def tag(request):
    tag = request.GET.get('tag', 0)
    questions = []
    for i in range(0, len(QUESTIONS)):
        if QUESTIONS[i].get('tag') == TAGS[int(tag)].get('name'):
            questions.append(QUESTIONS[i])
    page_obj = paginate(questions, request, PER_PAGE)
    return render(request, 'tag.html', {"questions": page_obj, 'tag': TAGS[int(tag)], "members": MEMBERS, "tags": TAGS, 'route':  "tags/?tag=" + str(tag), 'symbolRoute': "&"})


def logout(request):
    return render(request, 'login.html', {"members": MEMBERS, "tags": TAGS})


def settings(request):
    return render(request, 'settings.html', {"members": MEMBERS, "tags": TAGS})