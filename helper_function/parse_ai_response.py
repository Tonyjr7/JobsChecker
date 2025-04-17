import re

class ParseResponse:
    def parse_groq_response(self, text: str) -> dict:
        try:
            title_match = re.search(r"Job Title:\s*(.*?),\s*Open:", text)
            explanation_match = re.search(r"Reason:\s*(.*)", text)
            remote_match = re.search(r"Remote:\s*(\w+)", text)
            us_based_match = re.search(r"US-Based:\s*(\w+)", text)
            clearance_match = re.search(r"Clearance:\s*(\w+)", text)
            travel_match = re.search(r"Travel:\s*(\w+)", text)
            open_match = re.search(r"Open:\s*(\w+)", text)
            suitable_match = re.search(r"Suitable:\s*(\w+)", text)

            remote = remote_match and remote_match.group(1).lower() == "true"
            us_based = us_based_match and us_based_match.group(1).lower() == "true"
            clearance = clearance_match and clearance_match.group(1).lower() == "true"
            open_ = open_match and open_match.group(1).lower() == "true"
            suitable = suitable_match and suitable_match.group(1).lower() == "true"

            approve = all([
                remote,
                us_based,
                not clearance,
                open_,
                suitable
            ])

            return {
                "title": title_match.group(1).strip() if title_match else "Unknown",
                "location": "Remote" if remote else "On-site" if remote_match else "Unknown",
                "clearance": "Yes" if clearance else "No",
                "open": "Yes" if open_ else "No" if open_match else "Unknown",
                "travel": "Minimal" if travel_match else "Unknown",
                "us_based": "Yes" if us_based else "No" if us_based_match else "Unknown",
                "suitable": "Yes" if suitable else "No" if suitable_match else "Unknown",
                "approve": "Yes" if approve else "No",
                "explanation": explanation_match.group(1).strip() if explanation_match else "None"
            }
        except Exception as e:
            return {
                "title": "Unknown",
                "location": "Unknown",
                "clearance": "Unknown",
                "open": "Unknown",
                "travel": "Unknown",
                "us_based": "Unknown",
                "suitable": "No",
                "approve": "No",
                "explanation": f"Failed to parse response: {str(e)}"
            }

parse_response = ParseResponse()