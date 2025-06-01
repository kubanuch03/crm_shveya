# app_accounting/services/user_salary.py
from decimal import Decimal
from django.utils.translation import gettext_lazy as _
# Убедись, что импорты моделей корректны
from app_global.models import PackagingSettings, UtugSettings, TailorSettings, CroiSettings 
# Product больше не нужен здесь, если ставка получается через метод товара
# from app_productions.models import Product 
import logging # Используй твой настроенный logger, если он отличается
logger = logging.getLogger(__name__)

class Payment():
    def __init__(self):
        pass

    def get_rate_for_action(self, action_name: str, product_instance=None) -> Decimal: # product_instance опционален
        """
        Возвращает ставку за единицу для указанного действия.
        Приоритет: индивидуальная ставка товара, затем глобальная.
        :param action_name: Код этапа (например, 'SEWING', 'PACKING').
        :param product_instance: Экземпляр товара (Product), для которого выполняется действие.
        :return: Ставка Decimal или Decimal('0.00'), если не найдена.
        """
        if product_instance and hasattr(product_instance, 'get_individual_rate_for_operation'):
            individual_rate = product_instance.get_individual_rate_for_operation(action_name)
            if individual_rate is not None: # 0.00 - это тоже установленная ставка
                logger.debug(f"Используется индивидуальная ставка {individual_rate} для товара '{product_instance.title}' и действия '{action_name}'")
                return Decimal(str(individual_rate)) # Гарантируем Decimal

        # Если индивидуальная ставка не найдена или не указана (или нет product_instance), ищем глобальную
        global_rate_setting = None
        if action_name == "PACKING":
            global_rate_setting = PackagingSettings.objects.first()
        elif action_name == "SEWING":
            global_rate_setting = TailorSettings.objects.first()
        elif action_name == "UTUG":
            global_rate_setting = UtugSettings.objects.first()
        elif action_name == "CUTTING":
            global_rate_setting = CroiSettings.objects.first()
        # Добавь другие elif для BUTTONS, QC и т.д.
        
        if global_rate_setting and hasattr(global_rate_setting, 'per_unit') and global_rate_setting.per_unit is not None:
            logger.debug(f"Используется глобальная ставка {global_rate_setting.per_unit} для действия '{action_name}' (товар: {product_instance.title if product_instance else 'N/A'})")
            return Decimal(str(global_rate_setting.per_unit)) # Гарантируем Decimal
        
        product_title_for_log = product_instance.title if product_instance else "N/A"
        logger.warning(f"Ставка для действия '{action_name}' (товар: {product_title_for_log}) не найдена (ни индивидуальная, ни глобальная). Возвращена ставка 0.")
        return Decimal('0.00')

    # Метод calculate_earnings_for_specific_logs больше не нужен, так как логика в сигнале