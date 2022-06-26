import logging


def handle_exception(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.log(logging.ERROR, f'"{e}" in {func.__name__}')

    return wrapper


def a_handle_exception(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logging.log(logging.ERROR, f'"{e}" in {func.__name__}')

    return wrapper
