from django.db import models
from authentication.models import User

class ClientNote(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_notes')
    note = models.TextField()
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, related_name='notes_written'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Note for {self.client.name}"


class ClientAccountManager(models.Model):
    client = models.OneToOneField(User, on_delete=models.CASCADE, related_name='account_manager_link')
    manager = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, related_name='managed_clients'
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client.name} -> {self.manager.name if self.manager else 'Unassigned'}"