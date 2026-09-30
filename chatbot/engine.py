"""
SecureVote — Rule-based chatbot engine.

Matches user messages against keyword patterns and returns contextual
responses. Falls back to a generic support message for unrecognised input.
"""
import re


# ── FAQ Knowledge Base ────────────────────────────────────────────────
# Each entry: (compiled regex pattern, response text)
FAQ_ENTRIES = [
    (
        re.compile(r'\b(register|sign\s*up|create\s*account|join)\b', re.IGNORECASE),
        "To register, click the <strong>Register</strong> button in the navigation bar. "
        "You'll need a username, email address, and password. Once registered, you can "
        "immediately start voting in active elections."
    ),
    (
        re.compile(r'\b(forgot|reset|lost)\b.*\b(password|pass)\b', re.IGNORECASE),
        "To reset your password, please contact the election administrator. "
        "For security, password resets are handled manually to prevent unauthorized access."
    ),
    (
        re.compile(r'\b(how|is)\b.*\b(vote|ballot)\b.*\b(secure|safe|protect|encrypt)\b', re.IGNORECASE),
        "Your vote is protected by multiple layers of security:<br>"
        "• <strong>HMAC-SHA256</strong> integrity hash on every ballot<br>"
        "• <strong>Database-level</strong> unique constraint (one vote per election)<br>"
        "• <strong>CSRF protection</strong> on all form submissions<br>"
        "• <strong>Atomic transactions</strong> to prevent race conditions<br>"
        "• Your IP is hashed — we never store raw IP addresses."
    ),
    (
        re.compile(r'\b(change|modify|update|edit)\b.*\b(vote|ballot|choice)\b', re.IGNORECASE),
        "For election integrity, votes <strong>cannot be changed</strong> once cast. "
        "Each ballot is cryptographically sealed with an HMAC hash. "
        "Please review your choice carefully before confirming."
    ),
    (
        re.compile(r'\b(who|which)\b.*\b(candidate|running|options)\b', re.IGNORECASE),
        "You can view all candidates by navigating to an active election. "
        "Each candidate's name, party affiliation, and bio are displayed on the voting page."
    ),
    (
        re.compile(r'\b(result|outcome|winner|tally|count)\b', re.IGNORECASE),
        "Election results are available on each election's <strong>Results</strong> page. "
        "Results show vote counts and percentages for all candidates in real time."
    ),
    (
        re.compile(r'\b(when|deadline|time|schedule)\b.*\b(vote|election|end|close)\b', re.IGNORECASE),
        "Each election has a specific start and end date displayed on the Elections page. "
        "You can only cast your vote while the election is marked as <strong>Live</strong>."
    ),
    (
        re.compile(r'\b(eligible|can\s*i\s*vote|allowed|qualify)\b', re.IGNORECASE),
        "Any registered user with a verified voter profile can vote. "
        "After registration, your profile is automatically verified. "
        "You may vote once in each active election."
    ),
    (
        re.compile(r'\b(anonymous|privacy|private|identity|track)\b', re.IGNORECASE),
        "Your privacy is important to us. Each voter is assigned an <strong>anonymous UUID</strong> "
        "that is separate from your username. Your IP address is hashed before storage — "
        "we never store or log raw IP addresses."
    ),
    (
        re.compile(r'\b(help|support|contact|issue|problem|bug)\b', re.IGNORECASE),
        "I can help with common questions about registration, voting, security, and results. "
        "For technical issues, please contact the election administrator or email "
        "<strong>support@securevote.app</strong>."
    ),
    (
        re.compile(r'\b(hello|hi|hey|greet|good\s*(morning|afternoon|evening))\b', re.IGNORECASE),
        "Hello! 👋 I'm the SecureVote assistant. I can help you with:<br>"
        "• How to register and vote<br>"
        "• Password issues<br>"
        "• Vote security and privacy<br>"
        "• Election results<br>"
        "Just ask me anything!"
    ),
    (
        re.compile(r'\b(thank|thanks|thx|cheers)\b', re.IGNORECASE),
        "You're welcome! 😊 If you have any other questions, feel free to ask."
    ),
]

FALLBACK_RESPONSE = (
    "I'm not sure about that. Here are some things I can help with:<br>"
    "• <strong>\"How do I register?\"</strong><br>"
    "• <strong>\"How is my vote secured?\"</strong><br>"
    "• <strong>\"Can I change my vote?\"</strong><br>"
    "• <strong>\"When does the election end?\"</strong><br><br>"
    "For other questions, please contact <strong>support@securevote.app</strong>."
)


def get_response(user_message):
    """
    Match user_message against FAQ patterns and return the best response.

    Returns a dict with 'message' (HTML string) and 'matched' (bool).
    """
    if not user_message or not user_message.strip():
        return {
            'message': "Please type a question and I'll do my best to help!",
            'matched': False,
        }

    text = user_message.strip()

    for pattern, response in FAQ_ENTRIES:
        if pattern.search(text):
            return {
                'message': response,
                'matched': True,
            }

    return {
        'message': FALLBACK_RESPONSE,
        'matched': False,
    }
