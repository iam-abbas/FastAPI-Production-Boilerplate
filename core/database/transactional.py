from functools import wraps

from core.database import session


class Transactional:
    def __call__(self, func):
        @wraps(func)
        async def _transactional(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                await session.commit()
            except Exception as exception:
                await session.rollback()
                raise exception

            return result

        return _transactional
