from django.db import models

# Create your models here.


class Player(models.Model):
    name = models.CharField(max_length=100)
    team = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.team}"

    class Meta:
        ordering = ["-created_at"]
