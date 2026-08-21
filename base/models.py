from django.db import models
import uuid


# Shared base model for all domain entities.
# This keeps database auditing fields consistent across apps and avoids repeating
# common metadata like created/updated timestamps and a UUID primary key.
class BaseModel(models.Model):
    uid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True