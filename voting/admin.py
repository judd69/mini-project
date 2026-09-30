"""SecureVote — Admin configuration for the voting engine."""
from django.contrib import admin
from .models import VoterProfile, Election, Candidate, Ballot


class CandidateInline(admin.TabularInline):
    model = Candidate
    extra = 2
    fields = ('name', 'party', 'bio', 'display_order')


@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'is_active', 'status_label', 'vote_count')
    list_filter = ('is_active', 'start_date')
    search_fields = ('title',)
    inlines = [CandidateInline]

    @admin.display(description='Votes')
    def vote_count(self, obj):
        return obj.ballots.count()


@admin.register(VoterProfile)
class VoterProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'voter_id', 'is_verified', 'created_at')
    list_filter = ('is_verified',)
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('voter_id',)


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'party', 'election', 'display_order')
    list_filter = ('election',)
    search_fields = ('name', 'party')


@admin.register(Ballot)
class BallotAdmin(admin.ModelAdmin):
    list_display = ('id', 'election', 'voter', 'candidate', 'cast_at', 'ballot_hash_short')
    list_filter = ('election',)
    readonly_fields = ('ballot_hash', 'ip_fingerprint', 'cast_at')

    @admin.display(description='Hash')
    def ballot_hash_short(self, obj):
        return obj.ballot_hash[:16] + '...' if obj.ballot_hash else '-'
