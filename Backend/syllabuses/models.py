import uuid

from django.conf import settings
from django.db import models


class Syllabus(models.Model):
    STATUS_DRAFT = 'draft'
    STATUS_READY = 'ready'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_READY, 'Ready'),
    ]
    PDF_STATUS_NOT_GENERATED = 'not_generated'
    PDF_STATUS_PROCESSING = 'processing'
    PDF_STATUS_GENERATED = 'generated'
    PDF_STATUS_FAILED = 'failed'
    PDF_STATUS_CHOICES = [
        (PDF_STATUS_NOT_GENERATED, 'Not generated'),
        (PDF_STATUS_PROCESSING, 'Processing'),
        (PDF_STATUS_GENERATED, 'Generated'),
        (PDF_STATUS_FAILED, 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='syllabuses')
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    completion = models.PositiveSmallIntegerField(default=0)
    courseDescription = models.TextField(blank=True, default='')
    courseGoal = models.TextField(blank=True, default='')
    teachingPhilosophy = models.TextField(blank=True, default='')
    pdf_file = models.FileField(upload_to='syllabuses/pdfs/', null=True, blank=True)
    pdf_status = models.CharField(
        max_length=16,
        choices=PDF_STATUS_CHOICES,
        default=PDF_STATUS_NOT_GENERATED,
    )
    pdf_generated_at = models.DateTimeField(null=True, blank=True)
    pdf_error = models.TextField(blank=True, default='')
    pdf_task_id = models.CharField(max_length=255, blank=True, default='')
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)


class SyllabusTitleInfo(models.Model):
    syllabus = models.OneToOneField(Syllabus, on_delete=models.CASCADE, related_name='titleInfo')
    codeAndName = models.CharField(max_length=255, blank=True, default='')
    credits = models.CharField(max_length=32, blank=True, default='')
    totalHours = models.CharField(max_length=32, blank=True, default='')
    classroomHours = models.CharField(max_length=32, blank=True, default='')
    independentWorkHours = models.CharField(max_length=32, blank=True, default='')
    prerequisites = models.TextField(blank=True, default='')
    levelOfTraining = models.CharField(max_length=255, blank=True, default='')
    semester = models.CharField(max_length=255, blank=True, default='')
    educationalProgram = models.CharField(max_length=255, blank=True, default='')
    languageOfEducation = models.CharField(max_length=64, blank=True, default='')
    proficiencyLevel = models.CharField(max_length=255, blank=True, default='')
    formatOfTraining = models.CharField(max_length=255, blank=True, default='')
    instructorName = models.CharField(max_length=255, blank=True, default='')
    instructorDegree = models.CharField(max_length=255, blank=True, default='')
    instructorEmail = models.EmailField(blank=True, default='')
    instructorContacts = models.TextField(blank=True, default='')
    timeAndPlace = models.TextField(blank=True, default='')


class ClassScheduleRow(models.Model):
    syllabus = models.ForeignKey(Syllabus, on_delete=models.CASCADE, related_name='classSchedule')
    order = models.PositiveIntegerField(default=1)
    week = models.CharField(max_length=64, blank=True, default='')
    topic = models.TextField(blank=True, default='')
    format = models.TextField(blank=True, default='')
    task = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['order']


class LearningOutcomeRow(models.Model):
    syllabus = models.ForeignKey(Syllabus, on_delete=models.CASCADE, related_name='learningOutcomes')
    order = models.PositiveIntegerField(default=1)
    courseLearningOutcome = models.TextField(blank=True, default='')
    programLearningOutcome = models.TextField(blank=True, default='')
    code = models.CharField(max_length=32, blank=True, default='')
    description = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['order']


class ThematicPlanRow(models.Model):
    syllabus = models.ForeignKey(Syllabus, on_delete=models.CASCADE, related_name='thematicPlan')
    order = models.PositiveIntegerField(default=1)
    week = models.CharField(max_length=64, blank=True, default='')
    topicModule = models.TextField(blank=True, default='')
    courseOutcome = models.TextField(blank=True, default='')
    questions = models.TextField(blank=True, default='')
    tasks = models.TextField(blank=True, default='')
    literature = models.TextField(blank=True, default='')
    gradeStructure = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['order']


class AssessmentRow(models.Model):
    syllabus = models.ForeignKey(Syllabus, on_delete=models.CASCADE, related_name='assessmentSystem')
    order = models.PositiveIntegerField(default=1)
    topicModule = models.TextField(blank=True, default='')
    maxPercent = models.CharField(max_length=32, blank=True, default='')
    maxWeight = models.CharField(max_length=32, blank=True, default='')
    finalPoints = models.CharField(max_length=32, blank=True, default='')

    class Meta:
        ordering = ['order']


class LiteratureItem(models.Model):
    TYPE_REQUIRED = 'required'
    TYPE_ADDITIONAL = 'additional'
    TYPE_INTERNET = 'internet'
    TYPE_CHOICES = [
        (TYPE_REQUIRED, 'Required'),
        (TYPE_ADDITIONAL, 'Additional'),
        (TYPE_INTERNET, 'Internet'),
    ]

    syllabus = models.ForeignKey(Syllabus, on_delete=models.CASCADE, related_name='literatureItems')
    type = models.CharField(max_length=32, choices=TYPE_CHOICES)
    order = models.PositiveIntegerField(default=1)
    text = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['type', 'order']


class CoursePolicy(models.Model):
    syllabus = models.OneToOneField(Syllabus, on_delete=models.CASCADE, related_name='coursePolicy')
    masteringDiscipline = models.TextField(blank=True, default='')
    allowed = models.TextField(blank=True, default='')
    notAllowed = models.TextField(blank=True, default='')
    examEthics = models.TextField(blank=True, default='')
    informationCommunication = models.TextField(blank=True, default='')


class SignatureBlock(models.Model):
    syllabus = models.OneToOneField(Syllabus, on_delete=models.CASCADE, related_name='signatures')
    preparedByName = models.CharField(max_length=255, blank=True, default='')
    preparedByPosition = models.CharField(max_length=255, blank=True, default='')
    preparedByDate = models.CharField(max_length=64, blank=True, default='')
    signatureImage = models.TextField(blank=True, default='')
    stampImage = models.TextField(blank=True, default='')
