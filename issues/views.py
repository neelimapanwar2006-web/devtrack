import json
import os

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Reporter, Issue, CriticalIssue, LowPriorityIssue

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTERS_FILE = os.path.join(BASE_DIR, "reporters.json")
ISSUES_FILE = os.path.join(BASE_DIR, "issues.json")


def read_json(file_path):
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def write_json(file_path, data):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)


@csrf_exempt
def reporters(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            for field in ["id", "name", "email", "team"]:
                if field not in data:
                    return JsonResponse(
                        {"error": f"Missing field: {field}"}, status=400
                    )

            reporter = Reporter(
                data["id"], data["name"], data["email"], data["team"]
            )
            reporter.validate()

            reporters_data = read_json(REPORTERS_FILE)

            if any(r["id"] == reporter.id for r in reporters_data):
                return JsonResponse(
                    {"error": "Reporter ID already exists"}, status=400
                )

            reporters_data.append(reporter.to_dict())
            write_json(REPORTERS_FILE, reporters_data)

            return JsonResponse(reporter.to_dict(), status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except ValueError as error:
            return JsonResponse({"error": str(error)}, status=400)

    if request.method == "GET":
        reporters_data = read_json(REPORTERS_FILE)
        reporter_id = request.GET.get("id")

        if reporter_id is not None:
            try:
                reporter_id = int(reporter_id)
            except ValueError:
                return JsonResponse({"error": "Invalid reporter ID"}, status=400)

            for reporter in reporters_data:
                if reporter["id"] == reporter_id:
                    return JsonResponse(reporter, status=200)

            return JsonResponse({"error": "Reporter not found"}, status=404)

        return JsonResponse(reporters_data, safe=False, status=200)

    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
def issues(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            for field in [
                "id", "title", "description", "status", "priority", "reporter_id"
            ]:
                if field not in data:
                    return JsonResponse(
                        {"error": f"Missing field: {field}"}, status=400
                    )

            if data["priority"] == "critical":
                issue = CriticalIssue(
                    data["id"], data["title"], data["description"],
                    data["status"], data["priority"], data["reporter_id"]
                )
            elif data["priority"] == "low":
                issue = LowPriorityIssue(
                    data["id"], data["title"], data["description"],
                    data["status"], data["priority"], data["reporter_id"]
                )
            else:
                issue = Issue(
                    data["id"], data["title"], data["description"],
                    data["status"], data["priority"], data["reporter_id"]
                )

            issue.validate()

            issues_data = read_json(ISSUES_FILE)

            if any(i["id"] == issue.id for i in issues_data):
                return JsonResponse(
                    {"error": "Issue ID already exists"}, status=400
                )

            reporters_data = read_json(REPORTERS_FILE)
            if not any(r["id"] == issue.reporter_id for r in reporters_data):
                return JsonResponse(
                    {"error": "Reporter not found"}, status=404
                )

            issues_data.append(issue.to_dict())
            write_json(ISSUES_FILE, issues_data)

            response_data = issue.to_dict()
            response_data["message"] = issue.describe()

            return JsonResponse(response_data, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except ValueError as error:
            return JsonResponse({"error": str(error)}, status=400)

    if request.method == "GET":
        issues_data = read_json(ISSUES_FILE)
        issue_id = request.GET.get("id")
        status_filter = request.GET.get("status")

        if issue_id is not None:
            try:
                issue_id = int(issue_id)
            except ValueError:
                return JsonResponse({"error": "Invalid issue ID"}, status=400)

            for issue in issues_data:
                if issue["id"] == issue_id:
                    return JsonResponse(issue, status=200)

            return JsonResponse({"error": "Issue not found"}, status=404)

        if status_filter is not None:
            if status_filter not in Issue.ALLOWED_STATUS:
                return JsonResponse(
                    {
                        "error": (
                            "Invalid status. Allowed values: "
                            "open, in_progress, resolved, closed"
                        )
                    },
                    status=400
                )

            filtered_issues = [
                issue for issue in issues_data
                if issue["status"] == status_filter
            ]
            return JsonResponse(filtered_issues, safe=False, status=200)

        return JsonResponse(issues_data, safe=False, status=200)

    return JsonResponse({"error": "Method not allowed"}, status=405)
