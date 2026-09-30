"""
SecureVote — Views for the voting engine.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Election, Candidate, Ballot, VoterProfile
from .forms import RegistrationForm, LoginForm
from .utils import generate_ballot_hash, hash_ip


# ── Public Views ──────────────────────────────────────────────────────

def home(request):
    """Landing page showing featured active elections."""
    active_elections = Election.objects.filter(
        is_active=True,
        end_date__gte=timezone.now(),
    ).order_by('start_date')[:3]
    return render(request, 'voting/home.html', {
        'active_elections': active_elections,
    })


# ── Auth Views ────────────────────────────────────────────────────────

def register_view(request):
    """Register a new user and auto-create their VoterProfile."""
    if request.user.is_authenticated:
        return redirect('election_list')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            VoterProfile.objects.create(user=user, is_verified=True)
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, 'Registration successful! You can now vote.')
            return redirect('election_list')
    else:
        form = RegistrationForm()

    return render(request, 'voting/register.html', {'form': form})


def login_view(request):
    """Log in an existing user."""
    if request.user.is_authenticated:
        return redirect('election_list')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'Welcome back, {user.username}!')
            next_url = request.GET.get('next', 'election_list')
            return redirect(next_url)
    else:
        form = LoginForm()

    return render(request, 'voting/login.html', {'form': form})


def logout_view(request):
    """Log out the current user."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


# ── Election Views ────────────────────────────────────────────────────

@login_required
def election_list(request):
    """List all active elections with the user's voting status."""
    elections = Election.objects.filter(is_active=True).order_by('start_date')

    # Determine which elections the user has already voted in
    voter_profile = getattr(request.user, 'voter_profile', None)
    voted_election_ids = set()
    if voter_profile:
        voted_election_ids = set(
            Ballot.objects.filter(voter=voter_profile)
            .values_list('election_id', flat=True)
        )

    election_data = []
    for election in elections:
        election_data.append({
            'election': election,
            'has_voted': election.id in voted_election_ids,
            'total_votes': election.ballots.count(),
        })

    return render(request, 'voting/election_list.html', {
        'election_data': election_data,
        'now': timezone.now(),
    })


@login_required
def vote_view(request, election_id):
    """Display voting interface for a specific election."""
    election = get_object_or_404(Election, id=election_id, is_active=True)

    if not election.is_ongoing:
        messages.warning(request, 'This election is not currently accepting votes.')
        return redirect('election_list')

    voter_profile = getattr(request.user, 'voter_profile', None)
    if not voter_profile:
        messages.error(request, 'Voter profile not found. Please contact support.')
        return redirect('election_list')

    if not voter_profile.is_verified:
        messages.warning(request, 'Your voter profile is not yet verified.')
        return redirect('election_list')

    # Already voted → redirect to results
    if Ballot.objects.filter(election=election, voter=voter_profile).exists():
        messages.info(request, 'You have already cast your vote in this election.')
        return redirect('results', election_id=election.id)

    candidates = election.candidates.all()
    return render(request, 'voting/vote.html', {
        'election': election,
        'candidates': candidates,
    })


@login_required
@require_POST
def cast_vote(request, election_id):
    """
    AJAX endpoint to cast a vote.

    Protected by:
    - @login_required
    - @require_POST
    - CSRF token (Django middleware)
    - DB unique constraint (election, voter)
    - Atomic transaction
    """
    election = get_object_or_404(Election, id=election_id, is_active=True)

    if not election.is_ongoing:
        return JsonResponse({'success': False, 'error': 'Election is not active.'}, status=400)

    voter_profile = getattr(request.user, 'voter_profile', None)
    if not voter_profile or not voter_profile.is_verified:
        return JsonResponse({'success': False, 'error': 'Voter not verified.'}, status=403)

    candidate_id = request.POST.get('candidate_id')
    if not candidate_id:
        return JsonResponse({'success': False, 'error': 'No candidate selected.'}, status=400)

    candidate = get_object_or_404(Candidate, id=candidate_id, election=election)

    try:
        with transaction.atomic():
            cast_at = timezone.now()
            ballot_hash = generate_ballot_hash(
                voter_id=voter_profile.id,
                election_id=election.id,
                candidate_id=candidate.id,
                cast_at=str(cast_at),
            )
            Ballot.objects.create(
                election=election,
                voter=voter_profile,
                candidate=candidate,
                ballot_hash=ballot_hash,
                ip_fingerprint=hash_ip(request),
            )

        return JsonResponse({
            'success': True,
            'message': 'Your vote has been recorded securely.',
            'ballot_hash': ballot_hash[:12] + '...',
            'redirect_url': f'/elections/{election.id}/confirmation/',
        })
    except IntegrityError:
        return JsonResponse({
            'success': False,
            'error': 'You have already voted in this election.',
        }, status=409)


@login_required
def confirmation_view(request, election_id):
    """Show a vote confirmation receipt."""
    election = get_object_or_404(Election, id=election_id)
    voter_profile = getattr(request.user, 'voter_profile', None)

    ballot = Ballot.objects.filter(
        election=election,
        voter=voter_profile,
    ).select_related('candidate').first()

    if not ballot:
        messages.warning(request, 'No ballot found for this election.')
        return redirect('election_list')

    return render(request, 'voting/confirmation.html', {
        'election': election,
        'ballot': ballot,
    })


def results_view(request, election_id):
    """Display election results with vote counts and percentages."""
    election = get_object_or_404(Election, id=election_id)
    candidates = election.candidates.all()

    results = []
    total_votes = election.ballots.count()

    for candidate in candidates:
        vote_count = candidate.ballots.filter(election=election).count()
        percentage = (vote_count / total_votes * 100) if total_votes > 0 else 0
        results.append({
            'candidate': candidate,
            'votes': vote_count,
            'percentage': round(percentage, 1),
        })

    results.sort(key=lambda x: x['votes'], reverse=True)

    return render(request, 'voting/results.html', {
        'election': election,
        'results': results,
        'total_votes': total_votes,
    })
