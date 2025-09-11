from typing import List, Optional, Dict, Any
import uuid


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

    async def create_group(self, group_data: Dict[str, Any]) -> Dict[str, Any]:
        new_group = {
            "id": str(uuid.uuid4()),
            "name": group_data.get("name"),
            "subgroup": group_data.get("subgroup"),
            "description": group_data.get("description"),
            "year": group_data.get("year"),
            "faculty": group_data.get("faculty")
        }
        self._groups.append(new_group)
        return new_group

    async def delete_group(self, group_id: str) -> bool:
        for i, group in enumerate(self._groups):
            if group["id"] == group_id:
                del self._groups[i]
                return True
        return False
