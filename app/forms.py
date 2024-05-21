import datetime
import time

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate, login
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import activate
from app.models import Profile, Answer, Tag, Question


class LoginForm(forms.Form):

    username = forms.CharField(label="Username")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")

    def clean_password(self):
        activate("ru")
        validate_password(self.cleaned_data['password'])
        return self.cleaned_data.get('password')

    def clean_username(self):
        activate("ru")
        username = self.cleaned_data.get("username")
        username = username.strip()

        if (len(username)) < 6:
            raise ValidationError("Username must be longer than 6 characters")

        return self.cleaned_data.get('username')
    def clean(self):
        activate("ru")
        user = User.objects.filter(username=self.cleaned_data.get("username"))
        if not user.exists():
            raise ValidationError({"username": ["User doesn't exist"]})

        user = user[0]
        if not user.check_password(self.cleaned_data.get("password")):
            raise ValidationError({"password": ["Password is wrong"]})

        return self.cleaned_data


class RegistrationForm(forms.Form):
    username = forms.CharField(min_length=6, max_length=30, label="Input your username")
    email = forms.EmailField(widget=forms.EmailInput, label="Input your email address")
    nickname = forms.CharField(min_length=4, max_length=30, label="Input your nickname")
    password = forms.CharField(widget=forms.PasswordInput, label="Input password")
    repeat_password = forms.CharField(widget=forms.PasswordInput, label="Repeat password")

    def clean_password(self):
        activate("ru")
        validate_password(self.cleaned_data['password'])
        return self.cleaned_data.get('password')

    def clean_username(self):
        activate("ru")
        username = self.cleaned_data.get("username")
        username = username.strip()

        if (len(username)) < 6:
            raise ValidationError("Username must be longer than 6 characters")

        if User.objects.filter(username=self.cleaned_data['username']).exists():
            raise ValidationError("This username already taken")

        return self.cleaned_data.get('username')

    def clean_email(self):
        activate("ru")
        validate_email(self.cleaned_data['email'])

        if User.objects.filter(email=self.cleaned_data['email']).exists():
            raise ValidationError("This email already taken")

        return self.cleaned_data.get('email')

    def clean_nickname(self):
        activate("ru")
        nickname = self.cleaned_data.get("nickname")
        nickname = nickname.strip()

        if (len(nickname)) < 4:
            raise ValidationError("Nickname must be longer than 6 characters")

        if Profile.objects.filter(nickname=nickname).exists():
            raise ValidationError("This nickname already taken")

        return self.cleaned_data.get("nickname").strip()

    def clean_avatar(self):
        activate("ru")
        return self.cleaned_data.get("avatar")

    def clean(self):
        activate("ru")
        super().clean()

        if self.cleaned_data.get('password') is None or self.cleaned_data.get('repeat_password') is None:
            return self.cleaned_data

        if validate_password(self.cleaned_data.get('password')) is not None:
            return self.cleaned_data

        if self.cleaned_data.get('avatar') is None:
            return self.cleaned_data

        if self.cleaned_data.get('password') != self.cleaned_data.get('repeat_password'):
            raise ValidationError({"password": "Mismatch passwords",
                                   "repeat_password": "Mismatch passwords"})

        return self.cleaned_data

    def save(self):
        username = self.cleaned_data['username'].strip()
        email = self.cleaned_data['email'].strip()
        password = self.cleaned_data['password'].strip()
        nickname = self.cleaned_data['nickname'].strip()

        ts = datetime.datetime.now()

        user = User.objects.create_user(username=username, email=email, password=password)
        # TODO: Resolve avatar mock
        Profile.objects.create(user=user, nickname=nickname, avatar=f"{ts}.jpg")
        user.save()

        return user


class AskingForm(forms.Form):
    title = forms.CharField(min_length=8, max_length=250, label="Header")
    text = forms.CharField(min_length=20, widget=forms.Textarea, label="Your question")
    tags = forms.CharField(help_text="Input tags inline one by one separate with comma", label="Tags")

    def clean_title(self):
        title = self.cleaned_data.get("title")
        title = title.strip()

        if (len(title)) < 8:
            raise ValidationError("Header can't be shortener than 8 characters")

        return title

    def clean_text(self):
        text = self.cleaned_data.get("text")
        text = text.strip()

        if (len(text)) < 20:
            raise ValidationError("Question can't be shortener than 20 characters")

        return text

    def clean_tags(self):
        tags = self.cleaned_data.get("tags")
        tags = tags.split(',')
        tags = [tag.strip() for tag in tags]

        if len(tags) == 0:
            raise ValidationError("In your question must be at least one tag")

        if len(tags) > 3:
            raise ValidationError("In your question must be less than 3 tags")

        for tag in tags:
            if len(tag) == 0:
                raise ValidationError("Tag can't be empty string")

            for char in tag:
                if ord(char) < 65 or (90 < ord(char) < 97) or (ord(char) > 122):
                    raise ValidationError(f"Your tags can't contains specific character like '{char}'")

        return self.cleaned_data.get("tags")

    def save(self, user=None):
        title = self.cleaned_data['title']
        text = self.cleaned_data['text']
        tags = self.cleaned_data['tags'].strip()
        tags_objects = []

        for tag in tags.split(','):
            cur_tag = tag.strip()
            objects = Tag.objects.all().filter(name=cur_tag)

            if len(objects) > 0:
                tags_objects.append(objects[0])
            else:
                tags_objects.append(Tag.objects.create(tag_title=cur_tag))

        new_question = Question.objects.create(title=title, text=text, user=user)
        new_question.tags.set(tags_objects)
        new_question.save()

        return new_question


class ProfileForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    activate("ru")
    email = forms.EmailField(label="Email")
    nickname = forms.CharField(min_length=6, max_length=30, label="Nickname")
    avatar = forms.ImageField(required=False, widget=forms.FileInput(), label="Avatar")

    def clean_nickname(self):
        activate("ru")
        nickname = self.cleaned_data.get("nickname")
        nickname = nickname.strip()

        if (len(nickname)) < 6:
            raise ValidationError("Nickname must be at least 6 characters long")
        return nickname

    def clean_email(self):
        activate("ru")
        validate_email(self.cleaned_data['email'])
        return self.cleaned_data.get('email')

    def clean(self):
        activate("ru")
        super().clean()
        email = self.cleaned_data['email']
        nickname = self.cleaned_data['nickname']

        if User.objects.filter(email=email).exists():
            if User.objects.filter(email=email)[0] != self.user:
                raise ValidationError("This email is already taken")

        if Profile.objects.filter(nickname=nickname).exists():
            if Profile.objects.filter(nickname=nickname)[0].user != self.user:
                raise ValidationError("This username is already taken")

    def save(self):
        activate("ru")
        user_profile = self.user.profile
        self.user.email = self.cleaned_data.get('email')
        user_profile.nickname = self.cleaned_data.get('nickname')

        if self.cleaned_data.get('avatar'):
            user_profile.avatar = self.cleaned_data.get('avatar')

        self.user.save()
        user_profile.save()


class AnswerForm(forms.Form):
    text = forms.CharField(min_length=10, widget=forms.Textarea, label="Your answer")

    def clean_text(self):
        text = self.cleaned_data.get("text")
        text = text.strip()

        if (len(text)) < 10:
            raise ValidationError("Answer must be at least 10 characters long")

        return text

    def save(self, question, user):
        text = self.cleaned_data.get('text').strip()
        answer = Answer.objects.create(question=question, text=text, user=user)
        question.answers_count = len(Answer.objects.filter(question=question))

        answer.save()
        question.save()

        return answer