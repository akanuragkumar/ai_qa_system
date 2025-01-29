from django.db import models
import uuid


class VectorField(models.Field):
    def __init__(self, dimensions, *args, **kwargs):
        self.dimensions = dimensions
        super().__init__(*args, **kwargs)

    def db_type(self, connection):
        return f'vector({self.dimensions})'

    def deconstruct(self):
        """
        Deconstruct the field for migrations.
        """
        name, path, args, kwargs = super().deconstruct()
        kwargs['dimensions'] = self.dimensions  # Add the dimensions argument
        return name, path, args, kwargs


class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    embedding = VectorField(dimensions=1536, null=True, blank=True)
    chunk_id = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.title

    class Meta:
        """Meta Information."""

        db_table = 'document'


class ChatSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta Information."""

        db_table = 'chat_session'

class Message(models.Model):
    chat_session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=10, choices=(("system", "System"), ("user", "User"), ("assistant", "Assistant")))
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta Information."""

        db_table = 'message'
