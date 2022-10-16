from django.core.validators import RegexValidator

not_me_in_username_validator = RegexValidator(
    regex=r"^(?![Mm][Ee]$)^[\w.@+-]+$",
    message="Нельзя указывать Me/mE/ME/me в качестве логина",
)
