"""
SecureVote — Seed script to populate demo data.

Run with: python manage.py shell < seed_data.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'securevote.settings.development')
django.setup()

from django.utils import timezone
from datetime import timedelta
from voting.models import Election, Candidate

print("🌱 Seeding demo data...")

# Create demo election
election, created = Election.objects.get_or_create(
    title="Student Council President 2026",
    defaults={
        'description': (
            "Vote for your next Student Council President. "
            "Each registered student may cast one vote. "
            "Results will be published after the election closes."
        ),
        'start_date': timezone.now() - timedelta(hours=1),
        'end_date': timezone.now() + timedelta(days=7),
        'is_active': True,
    }
)

if created:
    print(f"✅ Created election: {election.title}")

    candidates_data = [
        {
            'name': 'Aria Chen',
            'party': 'Innovation Alliance',
            'bio': 'Computer Science major with a vision for modernizing campus technology and creating inclusive study spaces for all students.',
            'display_order': 1,
        },
        {
            'name': 'Marcus Johnson',
            'party': 'Unity Coalition',
            'bio': 'Political Science student focused on mental health resources, affordable housing, and strengthening student government transparency.',
            'display_order': 2,
        },
        {
            'name': 'Priya Patel',
            'party': 'Green Campus',
            'bio': 'Environmental Engineering student championing sustainability initiatives, campus recycling programs, and renewable energy adoption.',
            'display_order': 3,
        },
        {
            'name': 'David Kim',
            'party': 'Independent',
            'bio': 'Business Administration student advocating for entrepreneurship programs, career development workshops, and alumni networking events.',
            'display_order': 4,
        },
    ]

    for data in candidates_data:
        candidate = Candidate.objects.create(election=election, **data)
        print(f"  ➕ Added candidate: {candidate.name} ({candidate.party})")
else:
    print(f"ℹ️  Election already exists: {election.title}")

print("\n🎉 Seed complete! You can now register a user and vote.")
