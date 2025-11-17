"""
Django project initialization.
Configure PyMySQL to work as MySQLdb before Django loads.
"""
# Configure PyMySQL for MySQL (must be done BEFORE Django imports MySQL backend)
# This allows Django to use PyMySQL as mysqlclient
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass  # PyMySQL not installed, will use mysqlclient if available

