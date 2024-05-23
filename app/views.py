import django
from django.contrib.auth import authenticate, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect

from app.forms import LoginForm, RegistrationForm, AnswerForm, AskingForm
from app.models import Question, Answer, Tag, User, Profile


TAGS = list(Tag.objects.all())
TAGS = TAGS[:10]
USERS = list(User.objects.all())
USERS = USERS[:5]

def get_base_url():
    return 'http://127.0.0.1:8000'

def error_404_view(request, exception):
    return render(request, '404.html', status=404)


def paginate(request, objects, per_page=10):
    paginator = Paginator(objects, per_page)
    page_number = request.GET.get('page')
    try:
        int_page_number = int(page_number)
        if int_page_number <= 0:
            page_number = 1
        elif int_page_number > paginator.num_pages:
            page_number = paginator.num_pages
        else:
            page_number = int_page_number
    except ValueError:
        page_number = 1
    except TypeError:
        page_number = 1
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    new_questions = list(Question.objects.new_questions())
    # print(USERS)
    return render(request, "index.html",
                  {'tags': TAGS, 'members': USERS, 'page_obj': paginate(request, new_questions), 'base': get_base(request), 'questions': new_questions})


def hot(request):
    hot_questions = list(Question.objects.hot_questions())
    return render(request, "hot.html",
                  {'tags': TAGS, 'members': USERS, 'page_obj': paginate(request, hot_questions), 'base': get_base(request)})


def by_tag(request, tag_name):
    tag = Tag.objects.tag_by_name(tag_name)
    questions = list(Question.objects.questions_by_tag(tag))
    return render(request, "tag.html",
                  {'tags': TAGS, 'members': USERS, 'tag': tag,
                   'page_obj': paginate(request, questions), 'base': get_base(request)})

@csrf_protect
def question(request, question_id):
    cur_question = Question.objects.question_by_id(question_id)
    answers = list(Answer.objects.answers_by_question(cur_question))
    page_obj = paginate(request, answers, 3)
    answer_form = AnswerForm()
    if request.method == "POST":
        answer_form = AnswerForm(request.POST)
        print(answer_form)
        print(answer_form.is_valid())
        if answer_form.is_valid():
            answer_form.save(user=request.user, question=cur_question)
            return redirect(f"{request.path}?page=1#last-answer")
    return render(request, 'question.html', {'tags': TAGS, 'members': USERS,
                                             'question': cur_question, 'page_obj': page_obj, 'base': get_base(request),
                                             'form': answer_form})

@csrf_protect
def log_in(request):
    login_form = LoginForm()
    if request.method == "POST":
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            django.contrib.auth.login(request, authenticate(**login_form.cleaned_data))
            return redirect(request.GET.get("continue", "/"))
    return render(request, 'login.html',
                  {'tags': TAGS, 'members': USERS, 'base': get_base(request), 'form': login_form})

@csrf_protect
def signup(request):
    reg_form = RegistrationForm()
    if request.user.is_authenticated:
        return redirect("index")
    if request.method == "POST":
        reg_form = RegistrationForm(request.POST)
        if reg_form.is_valid():
            reg_form.save()
            new_user = authenticate(request=request, username=reg_form.cleaned_data['username'], password=reg_form.cleaned_data['password'])
            django.contrib.auth.login(request, new_user)
            return redirect(request.GET.get("continue", "/"))
    return render(request, 'signup.html',
                  {'tags': TAGS, 'members': USERS, 'base': get_base(request), 'form': reg_form})

@csrf_protect
@login_required(login_url='login', redirect_field_name='continue')
def ask(request):
    ask_form = AskingForm()
    if request.method == "POST":
        ask_form = AskingForm(request.POST)
        print(ask_form.errors)
        if ask_form.is_valid():
            new_question = ask_form.save(user=request.user)
            return redirect(f"{get_base_url()}/question/{new_question.id}/")
    return render(request, 'ask.html',
                  {'tags': TAGS, 'members': USERS, 'base': get_base(request), 'form': ask_form})

@csrf_protect
@login_required(login_url='login', redirect_field_name='continue')
def settings(request):
    profile = Profile.objects.all().filter(user_id=request.user.id).first()
    return render(request, 'settings.html',
                  {'tags': TAGS, 'users': USERS, 'base': get_base(request),
                   'profile': profile})

def end_session(request):
    logout(request)
    if request.GET.get("continue") is None:
        return redirect("index")
    return redirect(request.GET.get("continue"))

def get_base(request):
    if request.user.is_authenticated:
        return 'layouts/base-auth.html'
    return 'layouts/base-not-auth.html'