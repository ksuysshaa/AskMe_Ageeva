from django.core.paginator import Paginator
from django.shortcuts import render

# Create your views here.

QUESTIONS = [
    {
        "id": i,
        "title": f"Question {i}",
        "text": f"This is question number {i}"
    } for i in range(200)
]

def index(request):
    page_num = request.GET.get('page', 1)
    paginator = Paginator(QUESTIONS, 5)
    page_obj = paginator.page(page_num)
    return render(request, 'index.html', {"questions": page_obj})

def hot(request):
    return render(request, 'hot.html', {"questions": QUESTIONS})

def question(request, question_id):
    question = QUESTIONS[question_id]
    answers = [
        {
            'id': i,
            'title': f'Answer {i}',
            'content': f'Long lorem ipsum {i}'
        } for i in range(5)
    ]
    return render(request, 'question.html', {"question": question, "answers": answers})