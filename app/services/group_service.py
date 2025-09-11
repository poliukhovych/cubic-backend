from typing import List, Optional, Dict, Any


class GroupService:
    def __init__(self):
        self._groups = [
            {
                "id": "g1",
                "name": "КН-41",
                "subgroup": "a",
                "description": "Група комп'ютерних наук, 1 підгрупа",
                "year": 2021,
                "faculty": "Факультет інформаційних технологій"
            },
            {
                "id": "g2",
                "name": "КН-41",
                "subgroup": "b",
                "description": "Група комп'ютерних наук, 2 підгрупа",
                "year": 2021,
                "faculty": "Факультет інформаційних технологій"
            },
            {
                "id": "g3",
                "name": "МТ-42",
                "subgroup": "a",
                "description": "Група математики, 1 підгрупа",
                "year": 2022,
                "faculty": "Факультет математики та статистики"
            },
            {
                "id": "g4",
                "name": "ФЗ-40",
                "subgroup": "a",
                "description": "Група фізики, 1 підгрупа",
                "year": 2020,
                "faculty": "Факультет фізики"
            },
            {
                "id": "g5",
                "name": "КН-43",
                "subgroup": "a",
                "description": "Група комп'ютерних наук, 1 підгрупа",
                "year": 2023,
                "faculty": "Факультет інформаційних технологій"
            }
        ]

    async def get_all_groups(self) -> List[Dict[str, Any]]:
        return self._groups

    async def get_groups_by_teacher_id(self, teacher_id: str) -> List[Dict[str, Any]]:
        teacher_groups_mapping = {
            "t1": ["g1", "g2", "g5"],
            "t2": ["g3"],
            "t3": ["g4"],
            "t4": ["g1", "g2"]
        }
        
        group_ids = teacher_groups_mapping.get(teacher_id, [])
        return [group for group in self._groups if group["id"] in group_ids]

    async def get_group_by_id(self, group_id: str) -> Optional[Dict[str, Any]]:
        for group in self._groups:
            if group["id"] == group_id:
                return group
        return None
