"""
This script is used to import example quizzes from a JSON file

@author: 730003140, 730009864, 730020278, 730022096, 730002704, 730019821, 720039505
"""
import os
import json
from django.core.management.base import BaseCommand
from challenges.models import Quiz, Question, Choice


class Command(BaseCommand):
    """
    A management command to import quizzes from a JSON file.
    """
    help = "Import quizzes from a JSON file."

    def handle(self, *args, **options) -> None:
        """
        Handle the command.

        :return: None
        """


        # read the JSON file if it exists
        try:
            with open(os.path.join(
                    os.getcwd(), "challenges", "management", "commands", "quiz_data.json")
                    , "r", encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR("File not found"))
            return

        # Iterate over each quiz in the file and import it
        for quiz_item in data:
            self.__create_quiz(quiz_item)

        self.stdout.write(self.style.SUCCESS("Successfully imported quizzes."))

    def __create_quiz(self, quiz_item) -> None:
        """
        Create a quiz from the given data.

        :param quiz_item: JSON data about the quiz
        :return: None
        """
        # get the quiz data
        title = quiz_item.get("title")
        total_points = quiz_item.get("total_points", 100)
        questions_data = quiz_item.get("questions", [])

        # Create and save the Quiz.
        quiz = Quiz(title=title, total_points=total_points)
        quiz.save()

        # Import questions and their choices for each quiz
        for question_data in questions_data:

            # get the question data and create the question
            question_text = question_data.get("text")
            question = Question(quiz=quiz, text=question_text)
            question.save()

            choices_data = question_data.get("choices", [])
            correct_found = False  # check only one correct answer is provided
            for choice_item in choices_data:
                choice_text = choice_item.get("text")
                is_correct = choice_item.get("is_correct", False)

                # Warn if more than one correct answer is provided.
                if is_correct and correct_found:
                    self.stdout.write(self.style.WARNING(
                        "Multiple correct choices for question - using 1st"
                    ))
                    is_correct = False
                elif is_correct:
                    correct_found = True

                choice = Choice(question=question, text=choice_text, is_correct=is_correct)
                choice.save()
