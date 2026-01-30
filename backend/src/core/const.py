from enum import Enum
from datetime import timedelta


class AggregateInterval(str, Enum):
    HOUR  = "hour"
    DAY   = "day"
    MONTH = "month"

class AggregateWindow(str, Enum):
    LAST_24_HOURS  = "last_24_hours"
    LAST_7_DAYS    = "last_7_days"
    LAST_30_DAYS   = "last_30_days"
    LAST_6_MONTHS  = "last_6_months"
    LAST_12_MONTHS = "last_12_months"
    ALL_TIME       = "all_time"

    @property
    def delta(self) -> timedelta | None:
        if self == AggregateWindow.LAST_24_HOURS:
            return timedelta(days=1)
        if self == AggregateWindow.LAST_7_DAYS:
            return timedelta(days=7)
        if self == AggregateWindow.LAST_30_DAYS:
            return timedelta(days=30)
        if self == AggregateWindow.LAST_6_MONTHS:
            return timedelta(days=90)
        if self == AggregateWindow.LAST_12_MONTHS:
            return timedelta(days=365)
        return None

class Gender(str, Enum):
    MALE   = "male"
    FEMALE = "female"
    OTHER  = "other"

class StaffRole(str, Enum):
    SUPERADMIN = "superadmin"
    ADMIN      = "admin"
    EDITOR     = "editor"
    VIEWER     = "viewer"
    MEMBER     = "member"

class Role(str, Enum):
    SUPERADMIN = "superadmin"
    ADMIN      = "admin"
    EDITOR     = "editor"
    VIEWER     = "viewer"
    MEMBER     = "member"
    ENDUSER    = "enduser"

class TokenType(str, Enum):
    ACCESS_TOKEN = 'access'
    INTERMEDIATE_TOKEN = "intermediate"
    EMAIL_CHANGE = "email_change"

class DriverStatus(str, Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'

class UserType(str, Enum):
    DRIVER = "driver"
    CUSTOMER = "customer"

ETH_COUNTRY_CODE = "+251"
