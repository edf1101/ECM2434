"""
This script is used to import example quizzes from a JSON file
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

    def handle(self, *args, **options):
        """
        Handle the command.
        """

        # Define the base directory and file path for the JSON data.
        file_path = os.path.join(
            os.getcwd(), "challenges", "management", "commands","quiz_data.json"
        )

        # read the JSON file if it exists
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File {file_path} not found"))
            return

        successes = 0
        # Iterate over each quiz in the file and import it
        for quiz_item in data:
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
            successes += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully imported {successes} quiz(zes)."))
