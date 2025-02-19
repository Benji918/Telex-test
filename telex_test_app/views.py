from datetime import datetime, timedelta
import requests
from rest_framework import generics
from rest_framework.response import Response
from .utils import JiraReports
from django.conf import settings

class TelexAPITest(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        integration_json = {

  "data": {
    "date": {
      "created_at": "2025-02-18",
      "updated_at": "2025-02-18"
    },
    "descriptions": {
      "app_name": "Django-Jira Integration",
      "app_description": "A Telex Interval integration that sends pending and resolved jira tasks for the week",
      "app_logo": "https://telex.im/dashboard/applications/generate-json",
      "app_url": "http://40.83.174.214/",
      "background_color": "#fff"
    },
    "is_active": true,
    "integration_category": "Monitoring & Logging",
    "integration_type": "interval",
    "key_features": [
      "automation"
    ],
    "category": "Monitoring",
    "author": "Benjamin",
    "settings": [
      {
        "label": "Interval",
        "type": "text",
        "required": true,
        "default": "*/3 * * * * *"  #schedule it for Saturday night at 11:59 PM(59 23 * * 6).
      },
      {
        "label": "include-logs",
        "type": "checkbox",
        "required": true,
        "default": "True"
      }
    ],
    "target_url": "",
    "tick_url": "http://40.83.174.214/jira-report"
  }
}


        return Response(integration_json, status=200)


class JiraReportAPIView(generics.GenericAPIView):

    def post(self, request, *args,  **kwargs,):
        jira_reporter = JiraReports(domain=settings.JIRA_DOMAIN, email=settings.JIRA_EMAIL, api_token='ATATT3xFfGF059PYzW7I1qPdY13jeh89F1T3VQQgwA9_BDuDPXw4eX8BMXI8Pl_J5SHkCtZHyi43lp4KaqE6KXCIJH86PBAoggjiwRFSYpG4uA7HpUsaZNMoXtptauqhhAw6MH7zJczRCwqf3uipoVQqzjZ47WQkNRLL2dH5kGhPi5jBc1YVo6U=865F5695')
        try:
            issues = jira_reporter.get_weekly_issues()
            # print(issues)
            # Calculate counts
            pending_count = len(issues["pending"])
            resolved_count = len(issues['resolved'])


            # Calculate priority distribution
            priority_counts = {"pending": {}, "resolved": {}}
            for status in ["pending", "resolved"]:
                for issue in issues[status]:
                    priority = issue["fields"]["priority"]["name"]
                    priority_counts[status][priority] = priority_counts[status].get(priority, 0) + 1

            # Format response data
            response_data = {
                "date_range": {
                    "start": (datetime.now() - timedelta(days=7)).strftime('%B %d'),
                    "end": datetime.now().strftime('%B %d, %Y')
                },
                "overview": {
                    "new_unresolved_issues": pending_count,
                    "resolved_issues": resolved_count,
                    "total_issues": pending_count + resolved_count
                },
                "priority_breakdown": {
                    "pending": jira_reporter.format_priority_counts(priority_counts['pending']),
                    "resolved": jira_reporter.format_priority_counts(priority_counts['resolved'])
                },
                "metrics": {
                    "resolution_rate": jira_reporter.calculate_resolution_rate(pending_count, resolved_count),
                    "workload_index": jira_reporter.calculate_workload_index(pending_count, resolved_count)
                }
            }

            return Response(response_data, status=200)

        except requests.exceptions.RequestException as e:
            return Response(
                {"error": f"Error fetching data from Jira: {str(e)}"},
                status=503
            )
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=500
            )



