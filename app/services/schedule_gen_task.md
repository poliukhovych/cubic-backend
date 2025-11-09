### 🚀 Onboarding: Implementing the Schedule Generation Feature

**Context:**
We're implementing the feature to call our external schedule-generating microservice. I've already set up the API endpoint and the basic skeleton for the orchestrator service.

The main challenge is that our database structure does not currently store all the data that the microservice requires. The microservice needs a complex "problem instance" JSON, not just raw data.

A detailed analysis of these gaps is in the `mismatch-analysis.md` file. **Please read that file first.**

**1. Key Architectural Decision (Renaming)**

To avoid confusion, we have agreed to a new naming convention:

* **`ScheduleService` (The new name for `ScheduleLogService`)**
    * **Responsibility:** A simple CRUD service for the `schedules` table (the parent "folder" for a schedule).

* **`ScheduleGenerationService` (The new name for `ScheduleService`)**
    * **Responsibility:** The main **orchestrator**. This high-level service will be injected with 10+ other services. Its job is to fetch data from all of them, build the complex JSON, call the microservice, and save the result.

**2. Your Starting Point**

I have created a new skeleton file that you should use as your "to-do" list:
**`app/services/schedule_generation_service.py`**

This file's `__init__` and `_format_data_for_scheduler` methods outline *everything* that needs to be built and wired together.

**3. Your Implementation Tasks**

To complete the feature, you will need to:

* **Implement New Services:** Create standard CRUD services (Model, Repository, Service, Schema) for the following new tables. These are critical for filling the data gaps:
    * `TeacherAvailabilityService` (to store `available` times)
    * `TeacherPreferenceService` (to store `prefs`)
    * `GroupAvailabilityService` (to store `unavailable` times)
    * `TimeslotService`
    * `GroupCourseService`
    * `TeacherCourseService`
    * `SubgroupConstraintService`

* **Update Existing Models:**
    * **`group_course` table:** Must be modified to add `count_per_week: int` and `frequency: Enum`. This is a **showstopper**; we can't build the `courses` payload without it.
    * **`Timeslot` table:** Must be modified to add a `frequency: Enum("all", "odd", "even")` column.

* **Update Dependency Injection (`core/deps.py`):**
    * Rename the service dependencies based on our new naming plan.
    * Add new provider functions (e.g., `get_group_course_service`) for all the new services you create.
    * Update `get_schedule_generation_service` to inject all 10+ dependencies correctly.

* **Update the API Endpoint (`api/schedules.py`):**
    * Rename the dependency from `get_schedule_service` to `get_schedule_generation_service`.
    * Determine `policy` and `params` source: We need to confirm how the `policy` and `params` data (seen in the example JSON) are provided. The `ScheduleGenerationService` skeleton currently assumes they will be passed into the `generate_and_save_schedule` method. You will need to investigate whether this data should come from the frontend request body, be hard-coded, or fetched from another source, and then implement the logic accordingly.

* **Implement the Orchestrator:**
    * The final (and most complex) step is to fill in the `TODO`s inside `_format_data_for_scheduler`. This is where you'll use all the new services to fetch data and dynamically build the final JSON payloads for teachers, groups, courses (classes), and timeslots, just like we discussed in the gap analysis.

**input.json:**
```json
{
  "instance": {
    "teachers": [
      { "id": "t_kovalenko", "name": "Коваленко О.", "available": ["mon.all.1", "mon.all.2", "mon.all.3", "tue.all.1", "tue.all.2", "wed.all.1"], "prefs": {"preferred_days": ["mon"]} },
      { "id": "t_petrenko", "name": "Петренко І.", "available": ["tue.all.1", "tue.all.2", "tue.all.3", "wed.all.2", "wed.all.3", "thu.all.1", "thu.all.2"], "prefs": {"preferred_days": ["thu"], "avoid_slots": ["tue.all.3"]} },
      { "id": "t_shevchenko", "name": "Шевченко М.", "available": ["mon.all.2", "mon.all.3", "fri.all.1", "fri.all.2"], "prefs": {"preferred_days": ["fri"]} },
      { "id": "t_morozov", "name": "Морозов В.", "available": ["wed.all.1", "wed.all.2", "wed.all.3", "thu.all.1", "thu.all.2", "thu.all.3", "fri.all.3"], "prefs": {} },
      { "id": "t_tkachenko", "name": "Ткаченко Л.", "available": ["mon.all.1", "tue.all.3"], "prefs": {} }
    ],
    "groups": [
      { "id": "g_math_1", "name": "Математика-1", "size": 25 },
      { "id": "g_math_2", "name": "Математика-2", "size": 28 },
      { "id": "g_cs_1", "name": "Комп. науки-1", "size": 30 },
      { "id": "g_cs_1a", "name": "КН-1 (підгр. А)", "size": 15, "parentGroupId": "g_cs_1" },
      { "id": "g_cs_1b", "name": "КН-1 (підгр. Б)", "size": 15, "parentGroupId": "g_cs_1" },
      { "id": "g_hist_1", "name": "Історія-1", "size": 40, "unavailable": ["fri.all.1", "fri.all.2", "fri.all.3"] },
      { "id": "g_phys_1", "name": "Фізика-1", "size": 22, "unavailable": ["fri.all.1", "fri.all.2", "fri.all.3"] }
    ],
    "rooms": [
      { "id": "r101", "name": "Ауд. 101", "capacity": 30 },
      { "id": "r102_lab", "name": "Лаб. 102", "capacity": 15 },
      { "id": "r201", "name": "Ауд. 201", "capacity": 35 },
      { "id": "r300_lec", "name": "Велика лекційна 300", "capacity": 100 }
    ],
    "courses": [
      { "id": "c_calculus", "name": "Вища математика (Лекція)", "groupIds": ["g_math_1", "g_math_2", "g_cs_1"], "teacherId": "t_morozov", "countPerWeek": 1, "frequency": "weekly" },
      { "id": "c_history", "name": "Історія України (Лекція)", "groupIds": ["g_hist_1", "g_phys_1"], "teacherId": "t_shevchenko", "countPerWeek": 1, "frequency": "weekly" },
      { "id": "c_prog_laba", "name": "Програмування (Лаб. А)", "groupIds": ["g_cs_1a"], "teacherId": "t_petrenko", "countPerWeek": 1, "frequency": "even" },
      { "id": "c_prog_labb", "name": "Програмування (Лаб. Б)", "groupIds": ["g_cs_1b"], "teacherId": "t_petrenko", "countPerWeek": 1, "frequency": "odd" },
      { "id": "c_algebra", "name": "Алгебра (Семінар)", "groupIds": ["g_math_1"], "teacherId": "t_kovalenko", "countPerWeek": 2, "frequency": "weekly" },
      { "id": "c_discrete", "name": "Дискретна математика", "groupIds": ["g_cs_1"], "teacherId": "t_tkachenko", "countPerWeek": 1, "frequency": "weekly" },
      { "id": "c_physics", "name": "Фізика (Семінар)", "groupIds": ["g_phys_1"], "teacherId": "t_morozov", "countPerWeek": 1, "frequency": "weekly" }
    ],
    "timeslots": [
        "mon.all.1", "mon.all.2", "mon.all.3",
        "tue.all.1", "tue.all.2", "tue.all.3",
        "wed.all.1", "wed.all.2", "wed.all.3",
        "thu.all.1", "thu.all.2", "thu.all.3",
        "fri.all.1", "fri.all.2", "fri.all.3",
        "tue.even.1", "tue.odd.1"
    ],
    "policy": {
      "soft_weights": {
        "daily_load_balance": 10,
        "windows_penalty": 20,
        "teacher_avoid_slots_penalty": 50,
        "teacher_preferred_days_penalty": 15
      }
    }
  },
  "params": {
    "timeLimitSec": 20
  }
}
```