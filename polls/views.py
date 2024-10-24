from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, Http404
from .models import Question


def index(request) -> HttpResponse:
    latest_question_lst = Question.objects.order_by("pub_date")[:5]
    context = {"latest_question_list": latest_question_lst,}
    return render(request, "polls/index.html", context)


def detail(request, question_id) -> HttpResponse:
    question = get_object_or_404(Question, pk=question_id)
    return render(request, "polls/detail.html", {"question": question})


def results(request, question_id) -> HttpResponse:
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)


def vote(request, question_id) -> HttpResponse:
    return HttpResponse("You're voting on question %s." % question_id)