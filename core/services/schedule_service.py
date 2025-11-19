# core/services/schedule_service.py
from __future__ import annotations

import logging
from datetime import date, datetime
from typing import List, Optional

from core.models.schedule import (
    BaseScheduleTemplate,
    TrainingInstance,
    ScheduleChangeLog,
)
from core.repositories.schedule_repo import (
    BaseScheduleTemplateRepo,
    TrainingInstanceRepo,
    ScheduleChangeLogRepo,
)

logger = logging.getLogger(__name__)


class ScheduleService:
    """
    Управление расписанием:
    - построение актуального расписания
    - создание/изменение/отмена занятий
    - ведение журнала действий
    """

    def __init__(
        self,
        base_repo: BaseScheduleTemplateRepo,
        inst_repo: TrainingInstanceRepo,
        log_repo: ScheduleChangeLogRepo,
    ):
        self.base_repo = base_repo
        self.inst_repo = inst_repo
        self.log_repo = log_repo

    # =====================================================================
    #                           ЧТЕНИЕ РАСПИСАНИЯ
    # =====================================================================

    def get_instances_for_date(self, d: date) -> List[TrainingInstance]:
        """Возвращает занятия на дату — то, что есть в базе."""
        return self.inst_repo.get_by_date(d)

    def build_daily_schedule(self, d: date) -> List[TrainingInstance]:
        """
        Собрать актуальное расписание на день:
        1. Берём недельные шаблоны (для этого weekday)
        2. Создаём TrainingInstance (если его ещё нет)
        3. Применяем «наложенные» изменения: переносы, отмены, добавления
        NOTE:
            Мы НЕ храним изменения отдельно — только инстансы.
            TrainingInstance — это уже финальная форма.
            Логи влияют только на историю.
        """
        logger.info("Building schedule for %s", d)

        # 1. Берём то, что уже есть (ручные, переносы, отмены)
        instances = self.inst_repo.get_by_date(d)
        has_instances = {i.source_template_id for i in instances if i.source_template_id}

        # 2. Подтягиваем weekly templates, если их нет в instances
        base_templates = self.base_repo.get_active()

        for t in base_templates:
            if t.weekday != d.weekday():
                continue

            if t.id not in has_instances:
                inst = TrainingInstance.from_template(t, d)
                inst.id = self.inst_repo.add(inst)
                instances.append(inst)

        # Сортировка
        instances.sort(key=lambda x: x.start_time)

        return instances

    # =====================================================================
    #                         ЛОГИРОВАНИЕ ИЗМЕНЕНИЙ
    # =====================================================================

    def _log(
        self,
        training_id: int,
        admin_user_id: int,
        change_type: str,
        old_value: dict | None,
        new_value: dict | None,
    ):
        log_entry = ScheduleChangeLog(
            id=None,
            training_id=training_id,
            admin_user_id=admin_user_id,
            change_type=change_type,
            old_value=old_value,
            new_value=new_value,
            timestamp=datetime.now(),
        )
        self.log_repo.add(log_entry)

    # =====================================================================
    #                        УПРАВЛЕНИЕ ЗАНЯТИЯМИ
    # =====================================================================

    def cancel(self, inst_id: int, admin_id: int, reason: str = ""):
        """Отменить занятие."""
        inst = self.inst_repo.get_by_id(inst_id)
        if not inst:
            raise ValueError("TrainingInstance not found")

        old = inst.__dict__.copy()

        inst.status = "canceled"
        inst.comment = reason
        self.inst_repo.update(inst)

        self._log(
            training_id=inst_id,
            admin_user_id=admin_id,
            change_type="canceled",
            old_value=old,
            new_value=inst.__dict__.copy(),
        )

    def add_extra(
        self,
        d: date,
        start_time,
        duration: int,
        trainer_id: int,
        place: str,
        training_type: str,
        admin_id: int,
        comment: str = "",
    ) -> TrainingInstance:
        """Добавить дополнительное одноразовое занятие."""
        inst = TrainingInstance(
            id=None,
            date=d,
            start_time=start_time,
            duration_minutes=duration,
            trainer_id=trainer_id,
            place=place,
            training_type=training_type,
            source_template_id=None,
            status="extra",
            comment=comment,
        )

        inst.id = self.inst_repo.add(inst)

        self._log(
            training_id=inst.id,
            admin_user_id=admin_id,
            change_type="added",
            old_value=None,
            new_value=inst.__dict__.copy(),
        )

        return inst

    def move(
        self,
        inst_id: int,
        *,
        new_time,
        new_duration: int,
        new_trainer: int,
        new_place: str,
        admin_id: int,
        comment: str = "",
    ) -> TrainingInstance:
        """Перенос существующего занятия (создаёт moved-копию)."""
        inst = self.inst_repo.get_by_id(inst_id)
        if not inst:
            raise ValueError("TrainingInstance not found")

        old = inst.__dict__.copy()

        # Создаём новый instance
        new_inst = inst.moved_copy(
            new_time=new_time,
            new_duration=new_duration,
            new_trainer=new_trainer,
            new_place=new_place,
        )
        new_inst.comment = comment

        new_inst.id = self.inst_repo.add(new_inst)

        # А исходное делаем canceled
        inst.status = "moved"
        self.inst_repo.update(inst)

        self._log(
            training_id=new_inst.id,
            admin_user_id=admin_id,
            change_type="moved",
            old_value=old,
            new_value=new_inst.__dict__.copy(),
        )

        return new_inst

    def change_trainer(self, inst_id: int, trainer_id: int, admin_id: int):
        inst = self.inst_repo.get_by_id(inst_id)
        if not inst:
            raise ValueError("TrainingInstance not found")

        old = inst.__dict__.copy()

        inst.trainer_id = trainer_id
        self.inst_repo.update(inst)

        self._log(
            training_id=inst_id,
            admin_user_id=admin_id,
            change_type="trainer_changed",
            old_value=old,
            new_value=inst.__dict__.copy(),
        )

    def change_time(self, inst_id: int, new_time, new_duration: int, admin_id: int):
        inst = self.inst_repo.get_by_id(inst_id)
        if not inst:
            raise ValueError("TrainingInstance not found")

        old = inst.__dict__.copy()

        inst.start_time = new_time
        inst.duration_minutes = new_duration

        self.inst_repo.update(inst)

        self._log(
            training_id=inst_id,
            admin_user_id=admin_id,
            change_type="time_changed",
            old_value=old,
            new_value=inst.__dict__.copy(),
        )
