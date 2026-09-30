"""
SecureVote — Data models for the voting engine.

Models:
    VoterProfile  — extends Django User with a UUID voter_id
    Election      — time-bounded election container
    Candidate     — belongs to an Election
    Ballot        — tamper-evident vote record with HMAC integrity hash
"""
import uuid
import hmac
import hashlib

from django.db import models
from django.conf import settings
from django.utils import timezone


class VoterProfile(models.Model):
    """Extends the Django User with an anonymised voter reference."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='voter_profile',
    )
    voter_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    is_verified = models.BooleanField(
        default=True,
        help_text='Auto-verified on registration. Set False to require manual verification.',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Voter Profile'
        verbose_name_plural = 'Voter Profiles'

    def __str__(self):
        return f"Voter {self.voter_id} ({self.user.username})"


class Election(models.Model):
    """A time-bounded election that contains candidates and receives ballots."""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']

    @property
    def is_ongoing(self):
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date

    @property
    def is_upcoming(self):
        return self.is_active and timezone.now() < self.start_date

    @property
    def is_ended(self):
        return timezone.now() > self.end_date

    @property
    def status_label(self):
        if self.is_ongoing:
            return 'Live'
        if self.is_upcoming:
            return 'Upcoming'
        return 'Ended'

    def __str__(self):
        return self.title


class Candidate(models.Model):
    """A candidate running in a specific election."""
    election = models.ForeignKey(
        Election,
        on_delete=models.CASCADE,
        related_name='candidates',
    )
    name = models.CharField(max_length=200)
    party = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    photo_url = models.URLField(blank=True)
    display_order = models.IntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'name']

    def __str__(self):
        return f"{self.name} ({self.party})" if self.party else self.name


class Ballot(models.Model):
    """
    An immutable, tamper-evident vote record.

    Integrity is guaranteed by an HMAC-SHA256 hash computed from
    (voter_id, election_id, candidate_id, cast_at, SECRET_KEY).
    A unique constraint on (election, voter) enforces one-vote-per-user
    at the database level.
    """
    election = models.ForeignKey(
        Election,
        on_delete=models.CASCADE,
        related_name='ballots',
    )
    voter = models.ForeignKey(
        VoterProfile,
        on_delete=models.CASCADE,
        related_name='ballots',
    )
    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name='ballots',
    )
    ballot_hash = models.CharField(max_length=64, help_text='HMAC-SHA256 integrity hash')
    cast_at = models.DateTimeField(auto_now_add=True)
    ip_fingerprint = models.CharField(
        max_length=64,
        blank=True,
        help_text='SHA-256 hashed IP for audit (raw IP never stored)',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['election', 'voter'],
                name='unique_vote_per_election',
            )
        ]
        ordering = ['-cast_at']

    def generate_hash(self):
        """Generate HMAC-SHA256 integrity hash for this ballot."""
        message = f"{self.voter_id}:{self.election_id}:{self.candidate_id}:{self.cast_at}"
        return hmac.new(
            settings.SECRET_KEY.encode(),
            message.encode(),
            hashlib.sha256,
        ).hexdigest()

    def verify_integrity(self):
        """Verify that the ballot has not been tampered with."""
        return hmac.compare_digest(self.ballot_hash, self.generate_hash())

    def __str__(self):
        return f"Ballot #{self.id} — Election: {self.election}"
