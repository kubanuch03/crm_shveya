from ..models import UserSalary
from app_productions.models import WorkLog
from app_accounting.models import UserSalary
from app_global.models import PackagingSettings, UtugSettings, TailorSettings
from logger import logger

class Payment():
    def __init__(self):
        pass

    def get_rate_for_action(self, action_name):
        """Возвращает ставку за единицу для указанного действия."""
        queryset = None
        if action_name == "PACKING":
            queryset = PackagingSettings.objects.first()
        elif action_name == "TAILOR":
            queryset = TailorSettings.objects.first()
        elif action_name == "SEWING":
            queryset = UtugSettings.objects.first()

        if queryset and hasattr(queryset, 'per_unit'):
            return queryset.per_unit
        else:
            logger.warning(f"Ставка для действия '{action_name}' не найдена или не имеет атрибута 'per_unit'.")
            return 0 # Возвращаем 0, если ставка не найдена, чтобы избежать ошибок

    def calculate_earnings_for_specific_logs(self, work_logs_queryset, action_name):
        """
        Рассчитывает общий заработок для переданного набора WorkLog.
        Предполагается, что у каждого WorkLog есть stage, по которому можно определить action.
        """
        total_cash = 0
        for log in work_logs_queryset:
            

            amount_per_unit = self.get_rate_for_action(action_name)

            if hasattr(log, 'quantity_processed') and log.quantity_processed is not None:
                total_cash += log.quantity_processed * amount_per_unit
            else:
                logger.debug(f"Предупреждение: WorkLog ID {log.pk} не имеет quantity_processed или оно None.")
        
        logger.info(f"Рассчитанный общий заработок для предоставленных логов: {total_cash}")
        return total_cash