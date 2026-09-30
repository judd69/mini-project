"""
SecureVote — Cryptographic and hashing utilities.
"""
import hmac
import hashlib

from django.conf import settings


def generate_ballot_hash(voter_id, election_id, candidate_id, cast_at):
    """
    Generate an HMAC-SHA256 integrity hash for a ballot.

    The hash binds the vote to a specific voter, election, candidate, and
    timestamp. Any modification to the stored ballot will invalidate the hash.
    """
    message = f"{voter_id}:{election_id}:{candidate_id}:{cast_at}"
    return hmac.new(
        settings.SECRET_KEY.encode(),
        message.encode(),
        hashlib.sha256,
    ).hexdigest()


def hash_ip(request):
    """
    Return a SHA-256 hash of the client's IP address.

    The raw IP is never stored — only its hash is kept for audit purposes.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
    return hashlib.sha256(ip.encode()).hexdigest()
