# Shane Tully
# 09.18.11
# Magnetic card check-in application for Penn State ACM

# All application-wide constants

# Behavoiral constants
VERSION = "3.0-beta"

DEFAULT_HOST = "acm.psu.edu"
DEFAULT_USER = "points"
DEFAULT_DATABASE = "points"
DEFAULT_TABLE = "points_spring_12"
DEFAULT_POINTS = 50
ALLOW_CHECKIN_WITHIN_HOUR = 1

# TextUtil constants
BACK = 10

# Generic return codes
SUCCESS = 0
FAILURE = -1

# Login errors
BAD_PASSWD = 2

# Card swipe errors
ERROR_READING_CARD = 11

# Database errors
CARD_NOT_IN_DB = 3
BAD_CHECKIN_TIME = 4
FUTURE_CHECKIN_TIME = 5
SQL_ERROR = 6
NO_RESULTS = 7
