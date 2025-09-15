"""
Example adaptive card templates for testing
"""

# Example of an "unanswered" adaptive card that needs fixing
EXAMPLE_UNANSWERED_CARD = {
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "type": "AdaptiveCard",
    "version": "1.3",
    "body": [
        {
            "type": "TextBlock",
            "text": "📋 **Action Required**",
            "weight": "Bolder",
            "size": "Medium",
            "color": "Attention"
        },
        {
            "type": "TextBlock",
            "text": "Please review and approve the following request:",
            "wrap": True
        },
        {
            "type": "FactSet",
            "facts": [
                {
                    "title": "Request Type:",
                    "value": "Budget Approval"
                },
                {
                    "title": "Amount:",
                    "value": "$5,000"
                },
                {
                    "title": "Status:",
                    "value": "⏳ **PENDING**"
                }
            ]
        },
        {
            "type": "TextBlock",
            "text": "Please respond by EOD today.",
            "wrap": True,
            "color": "Warning"
        }
    ],
    "actions": [
        {
            "type": "Action.Submit",
            "title": "✅ Approve",
            "style": "positive",
            "data": {
                "action": "approve"
            }
        },
        {
            "type": "Action.Submit", 
            "title": "❌ Reject",
            "style": "destructive",
            "data": {
                "action": "reject"
            }
        }
    ]
}

# Example of how the card looks after being marked as "completed"
EXAMPLE_COMPLETED_CARD = {
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "type": "AdaptiveCard",
    "version": "1.3",
    "body": [
        {
            "type": "TextBlock",
            "text": "✅ **COMPLETED** - Updated on 2025-09-11 15:30",
            "color": "Good",
            "weight": "Bolder",
            "spacing": "Medium"
        },
        {
            "type": "TextBlock",
            "text": "📋 **Action Required**",
            "weight": "Bolder",
            "size": "Medium",
            "color": "Attention"
        },
        {
            "type": "TextBlock",
            "text": "Please review and approve the following request:",
            "wrap": True
        },
        {
            "type": "FactSet",
            "facts": [
                {
                    "title": "Request Type:",
                    "value": "Budget Approval"
                },
                {
                    "title": "Amount:",
                    "value": "$5,000"
                },
                {
                    "title": "Status:",
                    "value": "✅ **APPROVED**"
                }
            ]
        }
    ],
    "actions": []  # Actions removed since it's completed
}
