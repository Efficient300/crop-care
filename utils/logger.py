import logging


def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    # Проверяем, не был ли логгер уже настроен
    if not logger.handlers:
        # Устанавливаем уровень логирования
        logger.setLevel(logging.INFO)

        # Создаем консольный обработчик
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Настраиваем формат сообщений
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)

        # Добавляем обработчик к логгеру
        logger.addHandler(console_handler)

        # Отключаем распространение логов на родительские логгеры
        logger.propagate = False

    return logger