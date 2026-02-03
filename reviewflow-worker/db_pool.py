from psycopg2.pool import SimpleConnectionPool
from config import settings

_kwargs = {}
if settings.db_url:
    _kwargs["dsn"] = settings.db_url
else:
    _kwargs.update(
        {
            "host": settings.db_host,
            "port": settings.db_port,
            "dbname": settings.db_name,
            "user": settings.db_user,
            "password": settings.db_password,
        }
    )

_pool = SimpleConnectionPool(1, 5, **_kwargs)


def get_conn():
    return _pool.getconn()


def put_conn(conn):
    _pool.putconn(conn)
