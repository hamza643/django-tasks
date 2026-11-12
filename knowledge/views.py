import requests
from django.http import JsonResponse

from .qa import answer_question


def ask(request):
    question = request.GET.get("q", "").strip()
    if not question:
        return JsonResponse(
            {"error": "Please give a question, like /ask/?q=What does DefaultRouter do"},
            status=400,
        )
    try:
        result = answer_question(question)
    except requests.RequestException:
        return JsonResponse(
            {"error": "The local model (Ollama) is not reachable. Is it running?"},
            status=503,
        )
    return JsonResponse({"question": question, **result})