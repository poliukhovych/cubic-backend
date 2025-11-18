# Звіт про рефакторинг системи статусів

**Дата:** 2025-11-18  
**Версія:** 1.0  
**Автор:** Backend Team

---

## 📋 Огляд змін

Проведено повний рефакторинг системи статусів для студентів та викладачів. Замість розкиданих по різних місцях полів `confirmed: bool` введено єдину систему статусів з enum-полем `status` з трьома станами: `pending`, `active`, `inactive`.

### Основні зміни:
- ✅ Видалено поле `confirmed: bool` з моделей `Student` та `Teacher`
- ✅ Додано поле `status: str` з можливими значеннями: `"pending"`, `"active"`, `"inactive"`
- ✅ Створено міграцію БД для конвертації існуючих даних
- ✅ Оновлено всі API ендпоінти та схеми
- ✅ Додано нові ендпоінти для активації/деактивації

---

## 🔄 Зміни в API

### 1. Зміни в схемах відповідей

#### `GET /api/admin/students`
**Було:**
```json
{
  "studentId": "uuid",
  "firstName": "string",
  "lastName": "string",
  "patronymic": "string",
  "confirmed": true,  // ❌ Видалено
  "email": "string",
  "groupId": "uuid"
}
```

**Стало:**
```json
{
  "studentId": "uuid",
  "firstName": "string",
  "lastName": "string",
  "patronymic": "string",
  "status": "pending",  // ✅ Новий enum: "pending" | "active" | "inactive"
  "email": "string",
  "groupId": "uuid"
}
```

#### `GET /api/admin/teachers`
Аналогічно до студентів - замість `confirmed: bool` тепер `status: string`.

#### `GET /api/admin/stats`
**Було:**
```json
{
  "studentsTotal": 100,
  "studentsConfirmed": 80,  // ❌ Видалено
  "teachersTotal": 50,
  "teachersConfirmed": 45,  // ❌ Видалено
  "coursesTotal": 20
}
```

**Стало:**
```json
{
  "studentsTotal": 100,
  "studentsActive": 80,  // ✅ Кількість активних студентів
  "teachersTotal": 50,
  "teachersActive": 45,  // ✅ Кількість активних викладачів
  "coursesTotal": 20
}
```

---

### 2. Нові ендпоінти

#### Активація студента
```
PATCH /api/admin/students/{student_id}/activate
Authorization: Bearer <admin_token>
```

**Відповідь:**
```json
{
  "studentId": "uuid",
  "firstName": "string",
  "lastName": "string",
  "patronymic": "string",
  "status": "active",  // Встановлюється в "active"
  "groupId": "uuid",
  "userId": "uuid"
}
```

**Помилки:**
- `404` - студент не знайдено

---

#### Деактивація студента
```
PATCH /api/admin/students/{student_id}/deactivate
Authorization: Bearer <admin_token>
```

**Відповідь:**
```json
{
  "studentId": "uuid",
  "firstName": "string",
  "lastName": "string",
  "patronymic": "string",
  "status": "inactive",  // Встановлюється в "inactive"
  "groupId": "uuid",
  "userId": "uuid"
}
```

**Помилки:**
- `404` - студент не знайдено

---

#### Активація викладача
```
PATCH /api/admin/teachers/{teacher_id}/activate
Authorization: Bearer <admin_token>
```

**Відповідь:**
```json
{
  "teacherId": "uuid",
  "firstName": "string",
  "lastName": "string",
  "patronymic": "string",
  "status": "active",  // Встановлюється в "active"
  "userId": "uuid"
}
```

---

#### Деактивація викладача
```
PATCH /api/admin/teachers/{teacher_id}/deactivate
Authorization: Bearer <admin_token>
```

**Відповідь:**
```json
{
  "teacherId": "uuid",
  "firstName": "string",
  "lastName": "string",
  "patronymic": "string",
  "status": "inactive",  // Встановлюється в "inactive"
  "userId": "uuid"
}
```

---

### 3. Зміни в існуючих ендпоінтах

#### `POST /api/admin/students`
**Було:**
```json
{
  "firstName": "string",
  "lastName": "string",
  "patronymic": "string",
  "confirmed": false,  // ❌ Видалено
  "userId": "uuid",
  "groupId": "uuid"
}
```

**Стало:**
```json
{
  "firstName": "string",
  "lastName": "string",
  "patronymic": "string",
  "status": "pending",  // ✅ За замовчуванням "pending", можна вказати "active" або "inactive"
  "userId": "uuid",
  "groupId": "uuid"
}
```

#### `PUT /api/admin/students/{student_id}`
Аналогічно - замість `confirmed: bool` тепер `status: string`.

---

## 📊 Статуси та їх значення

### Можливі значення `status`:

1. **`"pending"`** - очікує активації
   - Новий студент/викладач після реєстрації
   - За замовчуванням при створенні

2. **`"active"`** - активний
   - Схвалений адміністратором
   - Може використовувати систему повною мірою

3. **`"inactive"`** - неактивний
   - Деактивований адміністратором
   - Обмежений доступ до системи

---

## 🔧 Технічні деталі для інтеграції

### TypeScript типи (рекомендовані)

```typescript
type StudentStatus = "pending" | "active" | "inactive";
type TeacherStatus = "pending" | "active" | "inactive";

interface AdminStudent {
  studentId: string;
  firstName: string;
  lastName: string;
  patronymic?: string;
  status: StudentStatus;  // Замість confirmed: boolean
  email?: string;
  groupId?: string;
}

interface AdminTeacher {
  teacherId: string;
  firstName: string;
  lastName: string;
  patronymic?: string;
  status: TeacherStatus;  // Замість confirmed: boolean
  email?: string;
  userId?: string;
}

interface AdminStats {
  studentsTotal: number;
  studentsActive: number;  // Замість studentsConfirmed
  teachersTotal: number;
  teachersActive: number;  // Замість teachersConfirmed
  coursesTotal: number;
}
```

---

## 🚨 Breaking Changes

### Що потрібно змінити на фронтенді:

1. **Замінити всі перевірки `confirmed` на `status`**
   ```typescript
   // ❌ Було
   if (student.confirmed) { ... }
   
   // ✅ Стало
   if (student.status === "active") { ... }
   ```

2. **Оновити фільтри та пошук**
   ```typescript
   // ❌ Було
   const confirmedStudents = students.filter(s => s.confirmed);
   
   // ✅ Стало
   const activeStudents = students.filter(s => s.status === "active");
   ```

3. **Оновити відображення статусів**
   ```typescript
   // ❌ Було
   {student.confirmed ? "Підтверджено" : "Не підтверджено"}
   
   // ✅ Стало
   {student.status === "active" ? "Активний" : 
    student.status === "pending" ? "Очікує" : "Неактивний"}
   ```

4. **Оновити статистику**
   ```typescript
   // ❌ Було
   stats.studentsConfirmed
   
   // ✅ Стало
   stats.studentsActive
   ```

---

## 📝 Приклади використання нових API

### Активація студента після схвалення реєстрації

```typescript
async function activateStudent(studentId: string) {
  const response = await fetch(
    `/api/admin/students/${studentId}/activate`,
    {
      method: "PATCH",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      }
    }
  );
  
  if (response.ok) {
    const student = await response.json();
    console.log(`Student ${student.studentId} is now ${student.status}`);
  }
}
```

### Деактивація викладача

```typescript
async function deactivateTeacher(teacherId: string) {
  const response = await fetch(
    `/api/admin/teachers/${teacherId}/deactivate`,
    {
      method: "PATCH",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      }
    }
  );
  
  if (response.ok) {
    const teacher = await response.json();
    console.log(`Teacher ${teacher.teacherId} is now ${teacher.status}`);
  }
}
```

### Фільтрація за статусом

```typescript
// Отримати тільки активних студентів
const activeStudents = students.filter(s => s.status === "active");

// Отримати студентів, що очікують активації
const pendingStudents = students.filter(s => s.status === "pending");

// Отримати неактивних студентів
const inactiveStudents = students.filter(s => s.status === "inactive");
```

---

## 📦 Міграція БД

**ВАЖЛИВО:** Перед використанням нових API необхідно запустити міграцію БД:

```bash
cd cubic-backend
alembic upgrade head
```

Міграція автоматично:
- Створить нові enum типи `student_status_enum` та `teacher_status_enum`
- Додасть колонку `status` до таблиць `students` та `teachers`
- Конвертує існуючі дані: `confirmed = TRUE` → `status = 'active'`, `confirmed = FALSE` → `status = 'pending'`
- Видалить стару колонку `confirmed`

---

## ✅ Чеклист для фронтенду

- [ ] Оновити TypeScript типи (видалити `confirmed: boolean`, додати `status: string`)
- [ ] Замінити всі перевірки `confirmed` на перевірки `status === "active"`
- [ ] Оновити компоненти відображення статусів
- [ ] Оновити фільтри та пошук
- [ ] Оновити статистику (використовувати `studentsActive` замість `studentsConfirmed`)
- [ ] Додати UI для нових кнопок активації/деактивації
- [ ] Протестувати всі сценарії з новими статусами
- [ ] Оновити документацію/коментарі в коді

---

## 🔗 Пов'язані файли

### Backend файли, що були змінені:

1. **Моделі БД:**
   - `app/db/models/common_enums.py` - додано `StudentStatus`, `TeacherStatus`
   - `app/db/models/people/student.py` - замінено `confirmed` → `status`
   - `app/db/models/people/teacher.py` - замінено `confirmed` → `status`

2. **Міграції:**
   - `alembic/versions/replace_confirmed_with_status.py` - нова міграція

3. **Схеми:**
   - `app/schemas/admin.py` - оновлено `AdminStudent`, `AdminTeacher`, `AdminStats`
   - `app/schemas/student.py` - оновлено всі схеми студентів
   - `app/schemas/teacher.py` - оновлено всі схеми викладачів

4. **API:**
   - `app/api/admin_people.py` - додано нові ендпоінти activate/deactivate
   - `app/api/admin_registrations.py` - оновлено логіку схвалення
   - `app/api/auth.py` - оновлено створення студентів/викладачів

5. **Repositories:**
   - `app/repositories/students_repository.py` - оновлено методи
   - `app/repositories/teacher_repository.py` - оновлено методи

6. **Services:**
   - `app/services/teacher_service.py` - оновлено методи

---

## 📞 Контакти

Якщо виникнуть питання або проблеми з інтеграцією, звертайтесь до backend команди.

---

**Примітка:** Всі зміни протестовані та готові до використання після запуску міграції БД.

