from enum import Enum


class ContactType(str, Enum):
    email = "email"
    phone = "phone"
    github = "github"
    linkedin = "linkedin"
    website = "website"
    twitter = "twitter"
