"""The owner's private control room: a secret address, an emailed one-time code, and a live dashboard of
parents, quizzes, rooms and children. See `mount_admin`."""

from .pages import mount_admin

__all__ = ["mount_admin"]
