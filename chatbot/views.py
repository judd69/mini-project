"""SecureVote — Chatbot AJAX views."""
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .engine import get_response


@require_POST
def chat_message(request):
    """
    Accept a chat message via POST and return the chatbot's response.

    Expects JSON body: {"message": "user text"}
    Returns JSON: {"reply": "HTML response", "matched": bool}
    """
    try:
        body = json.loads(request.body)
        user_message = body.get('message', '')
    except (json.JSONDecodeError, AttributeError):
        user_message = request.POST.get('message', '')

    result = get_response(user_message)

    return JsonResponse({
        'reply': result['message'],
        'matched': result['matched'],
    })
