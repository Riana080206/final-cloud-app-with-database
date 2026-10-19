from django.shortcuts import render, get_object_or_404, redirect
from .models import Course, Enrollment, Question, Choice, Submission

def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    enrollment = Enrollment.objects.get(user=user, course=course)

    if request.method == 'POST':
        selected_choice_ids = []
        for key, value in request.POST.items():
            if key.startswith('choice_'):
                selected_choice_ids.append(int(value))

        submission = Submission.objects.create(enrollment=enrollment)
        submission.choices.set(selected_choice_ids)
        submission.save()

        return redirect('onlinecourse:show_exam_result', course_id=course.id, submission_id=submission.id)

def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)

    selected_ids = list(submission.choices.values_list('id', flat=True))

    total_score = 0
    total_grade = 0

    for lesson in course.lesson_set.all():
        for question in lesson.question_set.all():
            total_grade += question.grade
            if question.is_get_score(selected_ids):
                total_score += question.grade

    grade_percentage = int((total_score / total_grade) * 100) if total_grade > 0 else 0

    context = {
        'course': course,
        'selected_ids': selected_ids,
        'total_score': total_score,
        'total_grade': total_grade,
        'grade_percentage': grade_percentage,
    }
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)
