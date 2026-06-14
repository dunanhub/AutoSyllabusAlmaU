from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from syllabuses.models import (
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


class Command(BaseCommand):
    help = 'Seed demo syllabus data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset demo syllabus related data before seeding',
        )

    def handle(self, *args, **options):
        reset = options.get('reset', False)
        User = get_user_model()
        user, _ = User.objects.get_or_create(
            email='teacher@almau.edu.kz',
            defaults={'first_name': 'Teacher', 'last_name': 'Demo'}
        )
        user.is_staff = True
        user.is_active = True
        user.set_password('Demo12345')
        user.save()

        syllabus = Syllabus.objects.filter(titleInfo__codeAndName='HIS 1101 — История Казахстана', owner=user).first()
        if (
            syllabus
            and not reset
            and ClassScheduleRow.objects.filter(syllabus=syllabus).exists()
        ):
            self.stdout.write(
                self.style.SUCCESS('Demo syllabus already exists. Skipping seed.')
            )
            return
        if syllabus is None:
            syllabus = Syllabus.objects.create(
                owner=user,
                status=Syllabus.STATUS_READY,
                completion=100,
                courseDescription='Курс “История Казахстана” направлен на формирование целостного понимания исторического развития Казахстана с древнейших времен до современности.',
                courseGoal='Сформировать у студентов историческое мышление и навыки критического анализа источников.',
                teachingPhilosophy='Преподавание строится на диалоге, анализе источников и академической дискуссии.',
            )
        else:
            syllabus.status = Syllabus.STATUS_READY
            syllabus.completion = 100
            syllabus.courseDescription = 'Курс “История Казахстана” направлен на формирование целостного понимания исторического развития Казахстана с древнейших времен до современности.'
            syllabus.courseGoal = 'Сформировать у студентов историческое мышление и навыки критического анализа источников.'
            syllabus.teachingPhilosophy = 'Преподавание строится на диалоге, анализе источников и академической дискуссии.'
            syllabus.save()

        SyllabusTitleInfo.objects.update_or_create(
            syllabus=syllabus,
            defaults={
                'codeAndName': 'HIS 1101 — История Казахстана',
                'credits': '5', 'totalHours': '150', 'classroomHours': '45', 'independentWorkHours': '105',
                'prerequisites': 'Школьный курс истории Казахстана и всемирной истории',
                'levelOfTraining': 'Бакалавриат', 'semester': '1 семестр', 'educationalProgram': 'Все образовательные программы бакалавриата AlmaU',
                'languageOfEducation': 'RU', 'proficiencyLevel': 'Академический русский / базовое понимание исторической терминологии',
                'formatOfTraining': 'Очная / blended learning', 'instructorName': 'Смагулова Айжан Ерлановна',
                'instructorDegree': 'к.и.н., ассоциированный профессор', 'instructorEmail': 'a.smagulova@almau.edu.kz',
                'instructorContacts': 'Консультации: среда 15:00-17:00, LMS Moodle, корпоративная почта', 'timeAndPlace': 'Понедельник 09:00-11:50, аудитория 302'
            }
        )

        if reset:
            ClassScheduleRow.objects.filter(syllabus=syllabus).delete()
            ThematicPlanRow.objects.filter(syllabus=syllabus).delete()
            AssessmentRow.objects.filter(syllabus=syllabus).delete()
            LiteratureItem.objects.filter(syllabus=syllabus).delete()
            LearningOutcomeRow.objects.filter(syllabus=syllabus).delete()

        schedule_rows = [
            ('1', 'Кіріспе. Қазақстан тарихы курсының пәні, мақсаты және дереккөздері', 'Лекция / семинар', 'Силлабуспен танысу, тарихнамалық ұғымдар бойынша қысқаша эссе'),
            ('2', 'Ежелгі Қазақстан: тас дәуірі және қола дәуірі мәдениеттері', 'Лекция / практикум', 'Археологиялық мәдениеттер кестесін толтыру'),
            ('3', 'Сақ, ғұн, үйсін және қаңлы мемлекеттері', 'Семинар / дерекпен жұмыс', 'Дерек үзіндісін талдау және картаға түсіру'),
            ('4', 'Түркі дәуірі және ортағасырлық мемлекеттер', 'Лекция / пікірталас', 'Түркі қағанаттарының саяси құрылымын салыстыру'),
            ('5', 'Қазақ хандығының құрылуы және дамуы', 'Семинар', 'Қазақ хандығының тарихи маңызы бойынша аргументтер дайындау'),
            ('6', 'XVII-XVIII ғғ. қазақ қоғамы және жоңғар шапқыншылығы', 'Лекция / кейс', 'Ақтабан шұбырынды оқиғалары бойынша хронология'),
            ('7', 'Қазақстанның Ресей империясы құрамына кіруі', 'Семинар / дебат', 'Отарлық басқару реформаларын талдау'),
            ('8', 'XIX ғасырдағы ұлт-азаттық қозғалыстар', 'Лекция / семинар', 'Кенесары Қасымұлы қозғалысы бойынша дерек талдау'),
            ('9', 'XX ғасыр басындағы Қазақстан және Алаш қозғалысы', 'Workshop', 'Алаш бағдарламасының негізгі бағыттарын презентациялау'),
            ('10', 'Кеңестік кезең: индустрияландыру, ұжымдастыру және ашаршылық', 'Лекция / құжатпен жұмыс', '1930-жылдардағы әлеуметтік өзгерістер туралы аналитикалық жазба'),
            ('11', 'Екінші дүниежүзілік соғыс жылдарындағы Қазақстан', 'Семинар', 'Тыл еңбегі және майдандағы қазақстандықтар бойынша постер'),
            ('12', 'Соғыстан кейінгі Қазақстан және тың игеру', 'Лекция / талқылау', 'Тың игерудің демографиялық салдарын талдау'),
            ('13', 'Қазақстандағы қайта құру және тәуелсіздікке жол', 'Семинар / пікірталас', 'Желтоқсан оқиғасының тарихи бағасы бойынша эссе'),
            ('14', 'Тәуелсіз Қазақстан: мемлекеттілік және жаңғыру', 'Лекция / кейс', 'Конституциялық реформалар бойынша қысқаша шолу'),
            ('15', 'Қорытындылау. Қазіргі Қазақстанның тарихи жады және ұлттық бірегейлік', 'Презентация / рефлексия', 'Қорытынды жоба және жеке рефлексия'),
        ]
        for order, row in enumerate(schedule_rows, start=1):
            ClassScheduleRow.objects.create(syllabus=syllabus, order=order, week=row[0], topic=row[1], format=row[2], task=row[3])

        for order, row in enumerate(schedule_rows, start=1):
            ThematicPlanRow.objects.create(
                syllabus=syllabus, order=order, week=row[0], topicModule=row[1], courseOutcome=f'PO{(order % 4) + 1}',
                questions='Негізгі тарихи ұғымдар мен кезеңдеу\nСаяси, әлеуметтік және мәдени өзгерістердің себеп-салдары\nДереккөздерді сыни талдау және интерпретация',
                tasks=row[3], literature=f'Негізгі әдебиет: Қазақстан тарихы. 1-5 томдар.\nҚосымша материалдар: апта {order} бойынша LMS-тағы деректер жинағы.',
                gradeStructure='Семинар белсенділігі және тапсырма — 3-5%' if order not in {8, 15} else ('Рубежный контроль 1 — 15%' if order == 8 else 'Қорытынды жоба және презентация — 20%')
            )

        learning_outcomes = [
            ('PO1', 'Объясняет основные этапы исторического развития Казахстана.', 'Демонстрирует системное мышление и академическую грамотность.', 'Периодизация, ключевые события, причинно-следственные связи.'),
            ('PO2', 'Анализирует исторические источники и научные интерпретации.', 'Применяет критическое мышление при работе с информацией.', 'Сравнение источников, выявление позиции автора и контекста.'),
            ('PO3', 'Оценивает роль Казахстана в региональных и глобальных процессах.', 'Понимает социальную ответственность и гражданскую позицию.', 'Историческая память, идентичность, модернизация.'),
            ('PO4', 'Аргументирует собственную позицию по историческим проблемам.', 'Эффективно коммуницирует письменно и устно.', 'Эссе, презентация, академическая дискуссия.'),
        ]
        for order, row in enumerate(learning_outcomes, start=1):
            LearningOutcomeRow.objects.create(syllabus=syllabus, order=order, code=row[0], courseLearningOutcome=row[1], programLearningOutcome=row[2], description=row[3])

        assessment_rows = [
            ('Семинарларға қатысу және белсенділік', '100', '10', '10'),
            ('Апталық жазбаша тапсырмалар', '100', '15', '15'),
            ('Дереккөздерді талдау жұмыстары', '100', '10', '10'),
            ('Карта және хронология тапсырмалары', '100', '5', '5'),
            ('Эссе: Алаш қозғалысының тарихи маңызы', '100', '10', '10'),
            ('Рубежный контроль 1', '100', '15', '15'),
            ('Workshop презентациясы', '100', '5', '5'),
            ('Топтық жоба', '100', '10', '10'),
            ('Рубежный контроль 2', '100', '10', '10'),
            ('Всего за теоретическое обучение', '100', '90', '90'),
            ('Государственный экзамен', '100', '10', '10'),
            ('Всего за курс', '100', '100', '100'),
        ]
        for order, row in enumerate(assessment_rows, start=1):
            AssessmentRow.objects.create(syllabus=syllabus, order=order, topicModule=row[0], maxPercent=row[1], maxWeight=row[2], finalPoints=row[3])

        for order, text in enumerate([
            'История Казахстана: учебник для вузов. В 5 томах. Алматы: Атамұра.',
            'Абусеитова М.Х. История Казахстана и Центральной Азии. Алматы.',
            'Козыбаев М.К. Казахстан на рубеже веков: размышления и поиски.',
        ], start=1):
            LiteratureItem.objects.create(syllabus=syllabus, type=LiteratureItem.TYPE_REQUIRED, order=order, text=text)

        for order, text in enumerate([
            'Омарбеков Т. Голодомор в Казахстане: причины и последствия.',
            'Нурпеисов К. Алаш һәм Алашорда.',
            'Мартин В. Закон империи: Россия и кочевники Центральной Азии.',
        ], start=1):
            LiteratureItem.objects.create(syllabus=syllabus, type=LiteratureItem.TYPE_ADDITIONAL, order=order, text=text)

        for order, text in enumerate([
            'https://e-history.kz — Портал “История Казахстана”',
            'https://archive.president.kz — Архив Президента Республики Казахстан',
            'https://adilet.zan.kz — Информационно-правовая система нормативных актов РК',
        ], start=1):
            LiteratureItem.objects.create(syllabus=syllabus, type=LiteratureItem.TYPE_INTERNET, order=order, text=text)

        CoursePolicy.objects.update_or_create(
            syllabus=syllabus,
            defaults={
                'masteringDiscipline': 'Освоение дисциплины предусматривает регулярное посещение занятий, подготовку к семинарам, выполнение письменных работ, участие в обсуждениях, работу с историческими источниками и защиту итогового проекта.',
                'allowed': 'Допустимо использовать академические базы данных, электронные библиотеки, LMS-материалы, командную работу в рамках заданий и консультации преподавателя.',
                'notAllowed': 'Недопустимы плагиат, списывание, фальсификация источников, сдача чужих работ, некорректное цитирование и нарушение сроков без уважительной причины.',
                'examEthics': 'Во время рубежного и итогового контроля запрещено использовать неразрешенные материалы, средства связи и помощь третьих лиц.',
                'informationCommunication': 'Официальные каналы коммуникации: LMS, корпоративная почта преподавателя и объявления в электронном кабинете.',
            }
        )

        SignatureBlock.objects.update_or_create(
            syllabus=syllabus,
            defaults={
                'preparedByName': 'Смагулова А.Е.',
                'preparedByPosition': 'Ассоциированный профессор Школы общественных наук',
                'preparedByDate': '2026-06-01',
                'signatureImage': '',
                'stampImage': '',
            }
        )

        self.stdout.write(self.style.SUCCESS('Seed data created successfully'))
