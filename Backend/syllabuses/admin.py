from django.contrib import admin

from .models import (
    AssessmentRow,
    ClassScheduleRow,
    CoursePolicy,
    LearningOutcomeRow,
    LiteratureItem,
    SignatureBlock,
    Syllabus,
    SyllabusTitleInfo,
    ThematicPlanRow,
)

admin.site.register(Syllabus)
admin.site.register(SyllabusTitleInfo)
admin.site.register(ClassScheduleRow)
admin.site.register(LearningOutcomeRow)
admin.site.register(ThematicPlanRow)
admin.site.register(AssessmentRow)
admin.site.register(LiteratureItem)
admin.site.register(CoursePolicy)
admin.site.register(SignatureBlock)
