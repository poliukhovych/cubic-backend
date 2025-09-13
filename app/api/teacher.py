from typing import List
from fastapi import APIRouter, Depends

from app.schemas.schedule import TeacherSchedule
from app.schemas.students import Student
from app.core.deps import get_current_user
from app.schemas.auth import User

router = APIRouter()


def generate_mock_teacher_schedule(teacher_id: str) -> TeacherSchedule:
    IPS11a = {"id": "ips11", "name": "ІПС-11", "subgroup": "a"}
    IPS11b = {"id": "ips11", "name": "ІПС-11", "subgroup": "b"}
    KN21a = {"id": "kn21", "name": "КН-21", "subgroup": "a"}
    KN21b = {"id": "kn21", "name": "КН-21", "subgroup": "b"}
    PM41 = {"id": "pm41", "name": "ПМ-41", "subgroup": None}
    INF42 = {"id": "inf42", "name": "ІНФ-42", "subgroup": None}
    
    pairs = {
        1: {"start": "08:30", "end": "10:05"},
        2: {"start": "10:25", "end": "12:00"},
        3: {"start": "12:10", "end": "13:45"},
        4: {"start": "14:00", "end": "15:35"},
        5: {"start": "15:45", "end": "17:20"},
    }
    
    lessons = [
        {
            "id": "l1",
            "weekday": 1,
            "time": pairs[2],
            "subject": "Медіаконтроль (лаб.)",
            "location": "лаб. 1-02",
            "group": IPS11a,
            "parity": "odd"
        },
        {
            "id": "l2",
            "weekday": 1,
            "time": pairs[2],
            "subject": "Медіаконтроль (лаб.)",
            "location": "лаб. 1-03",
            "group": IPS11b,
            "parity": "even"
        },
        {
            "id": "l3",
            "weekday": 4,
            "time": pairs[1],
            "subject": "Медіаконтроль (лаб.)",
            "location": "ауд. 207",
            "group": IPS11a,
            "parity": "even"
        },
        {
            "id": "l4",
            "weekday": 4,
            "time": pairs[1],
            "subject": "Медіаконтроль (семінар)",
            "location": "ауд. 208",
            "group": IPS11b,
            "parity": "odd"
        },
        {
            "id": "l5",
            "weekday": 3,
            "time": pairs[2],
            "subject": "ООП (лекція)",
            "location": "ауд. 502",
            "group": {"id": "kn21", "name": "КН-21", "subgroup": None},
            "parity": "any"
        },
        {
            "id": "l6",
            "weekday": 3,
            "time": pairs[3],
            "subject": "ООП (практика)",
            "location": "лаб. 2-10",
            "group": KN21a,
            "parity": "any"
        },
        {
            "id": "l7",
            "weekday": 3,
            "time": pairs[3],
            "subject": "ООП (практика)",
            "location": "лаб. 2-11",
            "group": KN21b,
            "parity": "any"
        },
        {
            "id": "l8",
            "weekday": 2,
            "time": pairs[5],
            "subject": "Розробка баз даних (лекція)",
            "location": "ауд. 114",
            "group": PM41,
            "parity": "any"
        },
        {
            "id": "l9",
            "weekday": 4,
            "time": pairs[4],
            "subject": "Розробка баз даних (практикум)",
            "location": "лаб. 3-12",
            "group": PM41,
            "parity": "any"
        },
        {
            "id": "l10",
            "weekday": 5,
            "time": pairs[1],
            "subject": "Теорія алгоритмів (лекція)",
            "location": "ауд. 401",
            "group": INF42,
            "parity": "any"
        },
        {
            "id": "l11",
            "weekday": 7,
            "time": pairs[2],
            "subject": "Теорія алгоритмів (консультація)",
            "location": "ауд. 214",
            "group": INF42,
            "parity": "any"
        }
    ]
    
    return TeacherSchedule(
        teacherId=teacher_id,  
        lessons=lessons
    )


def generate_mock_teacher_students(teacher_id: str) -> List[Student]:
    students = []
    
    ips11a_names = [
        "Петренко Іван Олександрович", "Коваль Олена Михайлівна", "Мельник Андрій Сергійович",
        "Шевченко Марія Ігорівна", "Бондар Володимир Петрович", "Кравчук Наталія Вікторівна",
        "Сидоренко Дмитро Володимирович", "Зінченко Ірина Олександрівна", "Лисенко Ростислав Валерійович",
        "Романюк Ганна Степанівна", "Гончарук Максим Юрійович", "Ткаченко Софія Тарасівна"
    ]
    
    ips11b_names = [
        "Данилюк Артем Леонідович", "Онищенко Валерія Павлівна", "Мороз Павло Романович",
        "Поліщук Оксана Євгенівна", "Чорний Юрій Анатолійович", "Яковенко Катерина Ігорівна",
        "Савченко Ілля Олексійович", "Кириленко Дарина Миколаївна", "Юрченко Владислав Олегович",
        "Руденко Аліна Сергіївна", "Волошин Михайло Андрійович", "Козак Лілія Богданівна"
    ]
    
    kn21a_names = [
        "Авраменко Олександр Сергійович", "Березюк Ольга Володимирівна", "Василенко Денис Петрович",
        "Гаврилюк Марина Вікторівна", "Гордієнко Сергій Олегович", "Демчук Анастасія Ігорівна",
        "Жуков Богдан Валентинович", "Захарченко Владислава Романівна", "Іщенко Тарас Михайлович",
        "Калініченко Єлизавета Олександрівна", "Ковтун Назар Віталійович", "Куценко Олексій Артемович",
        "Луценко Дарія Степанівна"
    ]
    
    kn21b_names = [
        "Мазур Іванна Сергіївна", "Марчук Роман Юрійович", "Нікітін Олексій Леонідович",
        "Опанасенко Олександра Андріївна", "Паламарчук Катерина Богданівна", "Петрук Артем Анатолійович",
        "Рибак Ігор Валерійович", "Семенюк Христина Тарасівна", "Скрипник Владлена Ігорівна",
        "Тимченко Ярослав Віталійович", "Федорчук Микита Олексійович", "Хара Ірина Сергіївна",
        "Цимбал Анна Леонідівна"
    ]
    
    pm41_names = [
        "Абрамчук Віктор Миколайович", "Бабенко Світлана Олександрівна", "Войтенко Андрій Петрович",
        "Гнатюк Олег Вікторович", "Дзюба Марія Романівна", "Єрмаков Максим Олександрович",
        "Журавель Катерина Сергіївна", "Заяць Ірина Віталіївна", "Іваненко Богдан Олегович",
        "Кіліченко Руслан Сергійович", "Левченко Аліса Олександрівна", "Мазепа Михайло Тарасович",
        "Носенко Вікторія Віталіївна", "Овчаренко Степан Юрійович", "Панченко Дмитро Ігорович",
        "Радчук Софія Леонідівна", "Сорока Павло Андрійович", "Титаренко Дарина Олегівна",
        "Усенко Роман Сергійович", "Франко Оксана Михайлівна", "Хоменко Євген Вікторович",
        "Цвєткова Лідія Павлівна"
    ]
    
    inf42_names = [
        "Анікіна Валентина Петрівна", "Білоус Сергій Миколайович", "Варченко Кирило Олександрович",
        "Герасимчук Анастасія Ігорівна", "Дяченко Олег Анатолійович", "Ємець Ілля Вадимович",
        "Журба Тетяна Володимирівна", "Зборовський Андрій Миколайович", "Ісаєва Катерина Олександрівна",
        "Кириченко Назар Миколайович", "Литвин Ірина Степанівна", "Малик Юлія Сергіївна",
        "Нечипоренко Богдан Вікторович", "Острогляд Олександра Тарасівна", "Паламар Артем Валентинович",
        "Рибчинський Микита Ігоревич", "Савчук Марія Олексіївна", "Терещенко Владислав Петрович",
        "Ульянова Єлизавета Сергіївна", "Фоменко Роман Андрійович", "Харченко Ганна Вадимівна"
    ]
    
    for i, name in enumerate(ips11a_names):
        students.append(Student(
            id=f"ips11a_{i+1}",
            name=name,
            email=name.lower().replace(" ", ".").replace("і", "i").replace("є", "e") + "@uni.ua",
            groupId="ips11",
            subgroup="a"
        ))
    
    for i, name in enumerate(ips11b_names):
        students.append(Student(
            id=f"ips11b_{i+1}",
            name=name,
            email=name.lower().replace(" ", ".").replace("і", "i").replace("є", "e") + "@uni.ua",
            groupId="ips11",
            subgroup="b"
        ))
    
    for i, name in enumerate(kn21a_names):
        students.append(Student(
            id=f"kn21a_{i+1}",
            name=name,
            email=name.lower().replace(" ", ".").replace("і", "i").replace("є", "e") + "@uni.ua",
            groupId="kn21",
            subgroup="a"
        ))
    
    for i, name in enumerate(kn21b_names):
        students.append(Student(
            id=f"kn21b_{i+1}",
            name=name,
            email=name.lower().replace(" ", ".").replace("і", "i").replace("є", "e") + "@uni.ua",
            groupId="kn21",
            subgroup="b"
        ))
    
    for i, name in enumerate(pm41_names):
        students.append(Student(
            id=f"pm41_{i+1}",
            name=name,
            email=name.lower().replace(" ", ".").replace("і", "i").replace("є", "e") + "@uni.ua",
            groupId="pm41",
            subgroup=None
        ))
    
    for i, name in enumerate(inf42_names):
        students.append(Student(
            id=f"inf42_{i+1}",
            name=name,
            email=name.lower().replace(" ", ".").replace("і", "i").replace("є", "e") + "@uni.ua",
            groupId="inf42",
            subgroup=None
        ))
    
    return students


@router.get("/schedule/{teacher_id}", response_model=TeacherSchedule)
async def fetch_teacher_schedule(
    teacher_id: str,
    current_user: User = Depends(get_current_user)
):
    return generate_mock_teacher_schedule(teacher_id)


@router.get("/students/{teacher_id}", response_model=List[Student])
async def fetch_my_students(
    teacher_id: str,
    current_user: User = Depends(get_current_user)
):
    return generate_mock_teacher_students(teacher_id)
