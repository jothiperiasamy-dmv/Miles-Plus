def load_qna_json(json_file_path):
    with open(json_file_path, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    return data.get("qna", [])

def compare_qna_utterances(original_file_path: str, updated_file_path: str):
    import json
    import pandas as pd
    import re

    # Load the original and updated files
    with open(original_file_path, "r", encoding="utf-8-sig") as f:
        original_data = json.load(f)

    with open(updated_file_path, "r", encoding="utf-8") as f:
        updated_data = json.load(f)

    # Prepare a mapping from stripped QIDs to original and updated entries
    original_qnas = {entry["qid"]: entry for entry in original_data["qna"]}
    updated_qnas = {}
    for entry in updated_data["qna"]:
        match = re.match(r"MLPLUS_\d{3}_(.*)", entry["qid"])
        if match:
            stripped_qid = match.group(1)
            updated_qnas[stripped_qid] = entry

    # Compare utterance counts
    comparison_results = []
    for oqid, oentry in original_qnas.items():
        if oqid in updated_qnas:
            uentry = updated_qnas[oqid]
            original_count = len(oentry.get("q", []))
            updated_count = len(uentry.get("q", []))
            reduction_percent = ((original_count - updated_count) / original_count * 100) if original_count else 0
            comparison_results.append({
                "Original QID (vrstatus-fix)": oqid,
                "Original Utterance Count": original_count,
                "Updated QID (MLPLUS_*)": uentry["qid"],
                "Updated Utterance Count": updated_count,
                "Reduction %": round(reduction_percent, 2)
            })

    # Split into positive and negative reduction lists
    positive_reductions = [row for row in comparison_results if row["Reduction %"] >= 0]
    negative_reductions = [row for row in comparison_results if row["Reduction %"] < 0]

    # Combine into final DataFrame
    final_df = pd.DataFrame(positive_reductions + negative_reductions)
    
    return final_df

import json
import pandas as pd
from collections import defaultdict, Counter

def get_all_keys_with_descriptions(qna_items):
    key_descriptions = {
        "qid": "Unique identifier for the QnA item.",
        "q": "List of user utterances (questions) that trigger this QnA.",
        "a": "The answer or response text shown to the user.",
        "args": "List of external URLs or links used in the answer.",
        "r": "Response card options (e.g., buttons, title).",
        "sa": "Session attributes used for routing, personalization, or logic.",
        "clientFilterValues": "Specifies which client/channel the QnA applies to (e.g., 'ivr').",
        "type": "Type of QnA item, usually 'qna'.",
        "l": "Lambda ARN used for dynamic or conditional processing.",
        "alt": "Alternative answer or variation (rarely used).",
        "priority": "Priority score for response selection (if overlapping QnAs).",
        "rp": "Response progress, controls chaining logic (if used).",
        "t": "Title for the QnA card or flow.",
        "tags": "Optional tags to categorize or label the QnA.",
        "conditionalChaining": "Conditional follow-up QnAs based on user input.",
        "elicitResponse": "Field used to prompt users for specific slots (structured data)."
    }

    all_keys = set()
    for item in qna_items:
        all_keys.update(item.keys())

    key_description_df = pd.DataFrame([
        {"Key": key, "Description": key_descriptions.get(key, "No description available.")}
        for key in sorted(all_keys)
    ])
    return key_description_df


def get_referenced_qids(qna_items):
    referenced_links = []
    for item in qna_items:
        source_qid = item.get("qid", "Unknown")
        if "r" in item and "buttons" in item["r"]:
            for button in item["r"]["buttons"]:
                val = button.get("value", "")
                if val.startswith("QID::"):
                    target_qid = val.replace("QID::", "")
                    referenced_links.append({
                        "Referencing QID": source_qid,
                        "Referenced QID": target_qid
                    })
    return pd.DataFrame(referenced_links)


def get_keys_with_null_values(qna_items):
    keys_with_nulls = set()
    for item in qna_items:
        for key, value in item.items():
            if value is None:
                keys_with_nulls.add(key)
    keys = list(sorted(keys_with_nulls)) if keys_with_nulls else ["None"]
    return pd.DataFrame({"Keys with Null Values": keys})


def get_keys_with_duplicate_values(qna_items):
    key_value_qids = defaultdict(lambda: defaultdict(list))
    for item in qna_items:
        qid = item.get("qid", "Unknown")
        for key, value in item.items():
            normalized_value = json.dumps(value, sort_keys=True)
            key_value_qids[key][normalized_value].append(qid)

    duplicates_data = []
    for key, values in key_value_qids.items():
        for val, qids in values.items():
            if len(qids) > 1:
                duplicates_data.append({
                    "Key": key,
                    "Duplicate Value": val,
                    "QIDs": ", ".join(qids)
                })

    return pd.DataFrame(duplicates_data)


def get_qnas_with_lambda_details(qna_items):
    lambda_data = []
    for item in qna_items:
        lambda_arn = item.get("l")
        if lambda_arn:
            lambda_data.append({
                "QID": item.get("qid", "Unknown"),
                "Lambda ARN": lambda_arn
            })
    return pd.DataFrame(lambda_data)


def get_qna_type_count(qna_items):
    type_counts = Counter(item.get("type", "undefined") for item in qna_items)
    return pd.DataFrame(type_counts.items(), columns=["QnA Type", "Count"])


def get_qnas_with_lambda(qna_items):
    lambda_usage_count = sum(1 for item in qna_items if "l" in item and item["l"])
    return pd.DataFrame([{"QnAs with Lambda": lambda_usage_count}])


def get_qnas_with_buttons(qna_items):
    buttons_count = sum(1 for item in qna_items if "r" in item and "buttons" in item["r"] and item["r"]["buttons"])
    return pd.DataFrame([{"QnAs with Buttons": buttons_count}])


def get_top_utterance_qnas(qna_items, top_n=50):
    sorted_qnas = sorted(
        [{"QID": item["qid"], "Utterance Count": len(item["q"])} for item in qna_items if "q" in item],
        key=lambda x: x["Utterance Count"],
        reverse=True
    )
    return pd.DataFrame(sorted_qnas[:top_n])


def get_most_reused_urls(qna_items, top_n=5):
    url_counter = Counter()
    for item in qna_items:
        if "args" in item:
            url_counter.update(item["args"])
    most_common_urls = url_counter.most_common(top_n)
    return pd.DataFrame(most_common_urls, columns=["URL", "Count"])


def get_session_attribute_usage(qna_items):
    session_keys_counter = Counter()
    for item in qna_items:
        for sa in item.get("sa", []):
            session_keys_counter[sa.get("text", "")] += 1
    return pd.DataFrame(session_keys_counter.items(), columns=["Session Attribute", "Count"])

def get_lambda_usage_with_api_info(qna_items):
    lambda_api_details = {
        "miles-plus-lambda-hooks-uat-agentWaitTime": [
            "https://<SALESFORCE_ENDPOINT>/services/oauth2/token",
            "https://<SALESFORCE_ENDPOINT>/services/data/v<API_VERSION>.0/actions/custom/apex/slalom_LiveAgentBotControl"
        ],
        "miles-plus-lambda-hooks-uat-confirmEmailAddress": [
            "No external API calls"
        ],
        "miles-plus-lambda-hooks-uat-dlApplicationStatus": [
            "service.getDLInfo(DLNumber)",
            "getDlApplicationStatus(dlInfo, intentName, event, retryCount)",
            "createCase(createCaseEvent)"
        ],
        "miles-plus-lambda-hooks-uat-connect": [
            "https://<LIVEAGENT_ENDPOINT>/chat/rest/Chasitor/ChasitorInit",
            "translateService(chat.text, chat.language, 'en')"
        ],
        "miles-plus-lambda-hooks-uat-startOver": [
            "No external API calls"
        ],
        "miles-plus-lambda-hooks-uat-text-redirect": [
            "No external API calls"
        ],
        "miles-plus-lambda-hooks-uat-thumbs-up-down-feedback": [
            "(Not analyzed yet)"
        ],
        "miles-plus-lambda-hooks-uat-createCaseFlow": [
            "https://<SALESFORCE_ENDPOINT>/services/oauth2/token",
            "https://<SALESFORCE_ENDPOINT>/services/data/v<API_VERSION>.0/actions/custom/flow/Create_Support_Case"
        ],
        "miles-plus-lambda-hooks-uat-vrStatus": [
            "No external API calls *(placeholder logic only)*"
        ]
    }

    lambda_data = []
    for item in qna_items:
        lambda_arn = item.get("l")
        if lambda_arn:
            qid = item.get("qid", "Unknown")
            lambda_name = lambda_arn.split(":")[-1]
            api_calls = lambda_api_details.get(lambda_name, ["Unknown or Not Mapped"])
            for api_call in api_calls:
                lambda_data.append({
                    "QID": qid,
                    "Lambda Function Name": lambda_name,
                    "API Call / Endpoint": api_call
                })
    return pd.DataFrame(lambda_data)

def get_all_api_calls_used(qna_items):
    lambda_api_details = {
        "miles-plus-lambda-hooks-uat-agentWaitTime": [
            "https://<SALESFORCE_ENDPOINT>/services/oauth2/token",
            "https://<SALESFORCE_ENDPOINT>/services/data/v<API_VERSION>.0/actions/custom/apex/slalom_LiveAgentBotControl"
        ],
        "miles-plus-lambda-hooks-uat-confirmEmailAddress": [
            "No external API calls"
        ],
        "miles-plus-lambda-hooks-uat-dlApplicationStatus": [
            "service.getDLInfo(DLNumber)",
            "getDlApplicationStatus(dlInfo, intentName, event, retryCount)",
            "createCase(createCaseEvent)"
        ],
        "miles-plus-lambda-hooks-uat-connect": [
            "https://<LIVEAGENT_ENDPOINT>/chat/rest/Chasitor/ChasitorInit",
            "translateService(chat.text, chat.language, 'en')"
        ],
        "miles-plus-lambda-hooks-uat-startOver": [
            "No external API calls"
        ],
        "miles-plus-lambda-hooks-uat-text-redirect": [
            "No external API calls"
        ],
        "miles-plus-lambda-hooks-uat-thumbs-up-down-feedback": [
            "(Not analyzed yet)"
        ],
        "miles-plus-lambda-hooks-uat-createCaseFlow": [
            "https://<SALESFORCE_ENDPOINT>/services/oauth2/token",
            "https://<SALESFORCE_ENDPOINT>/services/data/v<API_VERSION>.0/actions/custom/flow/Create_Support_Case"
        ],
        "miles-plus-lambda-hooks-uat-vrStatus": [
            "No external API calls *(placeholder logic only)*"
        ]
    }

    lambda_names_used = set()
    for item in qna_items:
        arn = item.get("l")
        if arn:
            lambda_name = arn.split(":")[-1]
            lambda_names_used.add(lambda_name)

    api_calls = set()
    for name in lambda_names_used:
        for api_call in lambda_api_details.get(name, []):
            if "No external API calls" not in api_call:
                api_calls.add(api_call)

    return pd.DataFrame(sorted(api_calls), columns=["API Call / Endpoint"])

def get_qnas_with_conditional_chaining(qna_items):
    chaining_data = []
    for item in qna_items:
        qid = item.get("qid", "Unknown")
        chaining = item.get("conditionalChaining")
        if chaining:
            chaining_data.append({
                "QID": qid,
                "Conditional Chaining": json.dumps(chaining, ensure_ascii=False)
            })
    return pd.DataFrame(chaining_data)

def get_qnas_with_buttons_detailed(qna_items):
    button_data = []
    for item in qna_items:
        qid = item.get("qid", "Unknown")
        buttons = item.get("r", {}).get("buttons", [])
        for button in buttons:
            button_data.append({
                "QID": qid,
                "Button Text": button.get("text", ""),
                "Button Value": button.get("value", "")
            })
    return pd.DataFrame(button_data)

import pandas as pd
import json
from tempfile import NamedTemporaryFile

def generate_qna_analysis_excel(json_file_path: str) -> str:
    
    # Load the QnA items
    with open(json_file_path, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    qna_items = data.get("qna", [])

    # Ordered mapping: sheet name -> matching function
    analysis_functions = [
    ("All Keys Used", get_all_keys_with_descriptions),
    ("High Utterance QnAs (Over 50)", get_top_utterance_qnas),
    ("Keys with Duplicate Values", get_keys_with_duplicate_values),
    ("Keys with Null Values", get_keys_with_null_values),
    ("QnAs with Lambda Details", get_qnas_with_lambda_details),
    ("All API Calls Used", get_all_api_calls_used),
    ("Lambda Usage with API Info", get_lambda_usage_with_api_info),
    ("Most Reused URLs (args)", get_most_reused_urls),  # Make sure the function is renamed accordingly if needed
    ("QnA Type Count", get_qna_type_count),
    ("QnAs with Buttons", get_qnas_with_buttons),
    ("QnAs with Buttons (Detailed)", get_qnas_with_buttons_detailed),
    ("QnAs with Conditional Chaining", get_qnas_with_conditional_chaining),
    ("Referenced QIDs", get_referenced_qids),
    ("Session Attribute Usage", get_session_attribute_usage),
]

    # Create Excel file in a temporary location
    with NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        excel_path = tmp.name

    # Write each analysis to its own sheet
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        for sheet_name, func in analysis_functions:
            try:
                df = func(qna_items)
                df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
            except Exception as e:
                error_df = pd.DataFrame([{"Error": str(e)}])
                error_df.to_excel(writer, sheet_name=sheet_name[:31], index=False)

    return excel_path

import pandas as pd
import json
from tempfile import NamedTemporaryFile

def generate_comparison_excel(original_file_path: str, optimized_file_path: str) -> str:
    # Load both QnA datasets
    def load_qna(path):
        with open(path, "r", encoding="utf-8-sig") as f:
            return json.load(f).get("qna", [])
    
    original_qna = load_qna(original_file_path)
    optimized_qna = load_qna(optimized_file_path)

    # Ordered mapping: sheet name -> matching function
    analysis_functions = [
    ("All Keys Used", get_all_keys_with_descriptions),
    ("High Utterance QnAs (Over 50)", get_top_utterance_qnas),
    ("Keys with Duplicate Values", get_keys_with_duplicate_values),
    ("Keys with Null Values", get_keys_with_null_values),
    ("QnAs with Lambda Details", get_qnas_with_lambda_details),
    ("All API Calls Used", get_all_api_calls_used),
    ("Lambda Usage with API Info", get_lambda_usage_with_api_info),
    ("Most Reused URLs (args)", get_most_reused_urls),  # Make sure the function is renamed accordingly if needed
    ("QnA Type Count", get_qna_type_count),
    ("QnAs with Buttons", get_qnas_with_buttons),
    ("QnAs with Buttons (Detailed)", get_qnas_with_buttons_detailed),
    ("QnAs with Conditional Chaining", get_qnas_with_conditional_chaining),
    ("Referenced QIDs", get_referenced_qids),
    ("Session Attribute Usage", get_session_attribute_usage),
]
    # Create Excel output file
    with NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        excel_path = tmp.name

    # Write to Excel with side-by-side comparison
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        for sheet_name, func in analysis_functions:
            try:
                # Handle threshold parameter for top utterances
                if sheet_name == "High Utterance QnAs (Over 50)":
                    original_df = func(original_qna, top_n=50)
                    optimized_df = func(optimized_qna, top_n=50)
                else:
                    original_df = func(original_qna)
                    optimized_df = func(optimized_qna)

                # Rename columns to indicate source
                original_df = original_df.add_prefix("Original file ")
                optimized_df = optimized_df.add_prefix("Optimized file ")

                # Align rows side-by-side (outer join on index)
                combined_df = pd.concat([original_df, optimized_df], axis=1)

                # Write to Excel
                combined_df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
            except Exception as e:
                pd.DataFrame([{"Error": str(e)}]).to_excel(writer, sheet_name=sheet_name[:31], index=False)

    return excel_path

