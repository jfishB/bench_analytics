from django.db import models


class Login(models.Model):
    """
    Stores login-related information for users.
    This table tracks login credentials and metadata but does not replace Django’s built-in User model.
    """

    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)

    class Meta:
        db_table = "logins"
        ordering = ["username"]

    def __str__(self):
        return self.username
