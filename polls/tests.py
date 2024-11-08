from django.http import HttpResponse
from django.urls import reverse
from django.test import TestCase
from django.db import IntegrityError
from .models import Question, Choice
from django.utils import timezone
import datetime


def create_question(question_text, days) -> Question:
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time: datetime.datetime = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self) -> None:
        """
        If no questions exist, an appropriate message is displayed.
        """
        response: HttpResponse = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_past_question(self) -> None:
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        question: Question = create_question(question_text="Past question.", days=-30)
        response: HttpResponse = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_future_question(self) -> None:
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        create_question(question_text="Future question.", days=30)
        response: HttpResponse = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_question_list"], [])

    def test_future_question_and_past_question(self) -> None:
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        question: Question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response: HttpResponse = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question],
        )

    def test_two_past_questions(self) -> None:
        """
        The questions index page may display multiple questions.
        """
        question1: Question = create_question(question_text="Past question 1.", days=-30)
        question2: Question = create_question(question_text="Past question 2.", days=-5)
        response: HttpResponse = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_question_list"],
            [question1, question2],
        )


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self) -> None:
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time: datetime.datetime = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)


    def test_was_published_recently_with_old_question(self) -> None:
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time: datetime.datetime = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)


    def test_was_published_recently_with_recent_question(self) -> None:
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time: datetime.datetime = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text="Future question.", days=5)
        url = reverse("polls:detail", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text="Past Question.", days=-5)
        url = reverse("polls:detail", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)


class QuestionResultsViewTests(TestCase):
    def test_future_question(self):
        """
        The results view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text="Future question.", days=5)
        url = reverse("polls:results", args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The results view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text="Past Question.", days=-5)
        url = reverse("polls:results", args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)


class ChoiceModelTests(TestCase):

    def setUp(self):
        """Set up a sample question and choice for testing."""
        self.question = Question.objects.create(
            question_text="Sample Question?",
            pub_date=timezone.now()
        )
    
    def test_choice_with_positive_votes(self):
        """Creating a choice with positive votes should succeed."""
        choice = Choice.objects.create(
            question=self.question,
            choice_text="Positive votes",
            votes=5
        )
        self.assertEqual(choice.votes, 5, "Votes should be set to the positive value provided.")

    def test_choice_with_zero_votes(self):
        """Creating a choice with zero votes should succeed."""
        choice = Choice.objects.create(
            question=self.question,
            choice_text="Zero votes",
            votes=0
        )
        self.assertEqual(choice.votes, 0, "Votes should allow zero as a non-negative value.")

    def test_choice_with_negative_votes(self):
        """Creating a choice with negative votes should raise an IntegrityError."""
        with self.assertRaises(IntegrityError, msg="A negative vote should raise an IntegrityError due to the constraint."):
            Choice.objects.create(
                question=self.question,
                choice_text="Negative votes",
                votes=-1
            )