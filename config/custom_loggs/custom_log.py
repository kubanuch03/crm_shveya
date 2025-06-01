import logging

def setup_logger(name):
    """
    Настроить логгер для каждого модуля, где будет использоваться.
    Имя логгера будет соответствовать имени модуля.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Создаем обработчик вывода в консоль
    ch = logging.StreamHandler()
    
    # Настроим формат для логгера
    formatter = logging.Formatter('%(name)s - %(message)s')
    ch.setFormatter(formatter)
    
    # Добавляем обработчик к логгеру
    logger.addHandler(ch)
    
    return logger