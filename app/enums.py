from enum import Enum


class Category(str, Enum):
    bug = "bug"
    feature_request = "feature_request"
    support = "support"
    billing = "billing"
    other = "other"


class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Status(str, Enum):
    open = "open"
    resolved = "resolved"
