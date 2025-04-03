def load_json_file(file_path):
    """Load JSON content from a file safely."""
    import json
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Failed to load JSON from {file_path}: {e}")
        return {}

def save_json_file(file_path, data):
    """Save JSON data to a file safely."""
    import json
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"❌ Failed to save JSON to {file_path}: {e}")

def copy_json_file(source_path, destination_path):
    """Safely copy a JSON file from source to destination."""
    import shutil
    try:
        shutil.copy(source_path, destination_path)
    except Exception as e:
        print(f"❌ Failed to copy JSON file: {e}")

from src.Assisstant import azure_openai_model_for_optimizations_all

def get_top_qids_by_question_count(json_file_path):
    """
    Extracts the top 10 QIDs with the highest number of associated 'q' values from a QnA JSON file.

    Args:
        json_file_path (str): Path to the JSON file.

    Returns:
        List[str]: List of top 10 QIDs sorted by number of associated questions.
    """
    import json
    from collections import Counter

    # Load the JSON data
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Count the number of questions (`q`) per `qid`
    qid_counts = {entry['qid']: len(entry.get('q', [])) for entry in data.get('qna', [])}

    # Get the top 10 qids with the most questions
    top_qids = Counter(qid_counts).most_common(10)

    # Return only the list of QIDs (first item from each tuple)
    return [qid for qid, _ in top_qids]


def get_questions_by_qid(json_file_path, target_qid):
    """
    Retrieves the list of user utterances ('q') associated with a specific QID from a QnA JSON file.

    Args:
        json_file_path (str): Path to the JSON file.
        target_qid (str): The QID for which to fetch associated questions.

    Returns:
        List[str]: List of user utterances (questions), or an empty list if QID is not found.
    """
    import json

    # Load the JSON data
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Search for the target QID and return its 'q' list
    for entry in data.get('qna', []):
        if entry.get('qid') == target_qid:
            return entry.get('q', [])

    return []  # Return empty list if QID not found


import os
import json
import shutil
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def process_single_qid_with_index(index, entry, max_retries=20):
    # Keep all other keys unchanged — only update "q"
    updated_entry = entry.copy()
    qid = updated_entry.get("qid")
    questions = updated_entry.get("q", [])

    for attempt in range(max_retries):
        try:
            optimized_questions = azure_openai_model_for_optimizations_all(qid, questions)
            if optimized_questions:
                updated_entry["q"] = optimized_questions  # ONLY replace "q"
            return index, updated_entry
        except Exception as e:
            print(f"[Retry {attempt+1}] Failed QID: {qid} — {e}")
            time.sleep(2)

    print(f"[Failed Completely] QID: {qid}. Using original questions.")
    updated_entry["q"] = questions  # Fallback to original
    return index, updated_entry


# def update_qna_questions_multithreaded(json_file_path, max_workers=10):
#     base, ext = os.path.splitext(json_file_path)
#     copied_file_path = f"{base}_copy{ext}"
#     shutil.copy(json_file_path, copied_file_path)

#     with open(copied_file_path, 'r', encoding='utf-8') as f:
#         data = json.load(f)

#     qna_list = data.get("qna", [])

#     # Placeholder for ordered updates
#     updated_qna = [None] * len(qna_list)

#     with ThreadPoolExecutor(max_workers=max_workers) as executor:
#         futures = [
#             executor.submit(process_single_qid_with_index, idx, entry)
#             for idx, entry in enumerate(qna_list)
#         ]

#         for future in as_completed(futures):
#             idx, updated_entry = future.result()
#             updated_qna[idx] = updated_entry
#             print(f"[{idx+1}/{len(qna_list)}] QID Processed: {updated_entry.get('qid')}")

#     # Final JSON structure: all original structure, just updated "q" fields
#     data["qna"] = updated_qna

#     updated_file_path = f"{base}_updated{ext}"
#     with open(updated_file_path, 'w', encoding='utf-8') as f:
#         json.dump(data, f, ensure_ascii=False, indent=2)

#     return updated_file_path

import json
import os
import re

# def update_conditional_sentences_with_qid_matching(json_file_path):
#     # Load JSON file
#     with open(json_file_path, 'r', encoding='utf-8') as f:
#         data = json.load(f)

#     # Extract all valid QIDs
#     all_valid_qids = set(entry.get("qid", "").strip() for entry in data.get("qna", []) if entry.get("qid"))

#     for entry in data.get("qna", []):
#         chaining = entry.get("conditionalChaining")
#         if chaining and isinstance(chaining, str):
#             original_chaining = chaining.strip()

#             # Case 1: Strict match for single QID string (including single/double quotes)
#             match = re.match(r"['\"]?QID::([\w.\-]+)['\"]?$", original_chaining)
#             if match:
#                 ref_qid = match.group(1).strip()
#                 for actual_qid in all_valid_qids:
#                     if actual_qid == ref_qid or actual_qid.endswith("_" + ref_qid):
#                         chaining = f"'QID::{actual_qid}'"
#                         break

#             else:
#                 # Case 2: Ternary expression or JS sentence-style expression
#                 matches = re.findall(r'"QID::([\w.\-]+)"', chaining)
#                 for ref_qid in matches:
#                     for actual_qid in all_valid_qids:
#                         if actual_qid == ref_qid or actual_qid.endswith("_" + ref_qid):
#                             chaining = chaining.replace(f'"QID::{ref_qid}"', f'"QID::{actual_qid}"')
#                             break

#             # Print Before → After if changed
#             if chaining != original_chaining:
#                 print(f"\nQID: {entry.get('qid')}")
#                 print(f"🔸 Before: {original_chaining}")
#                 print(f"✅ After : {chaining}")

#             entry["conditionalChaining"] = chaining

#     # Save updated JSON file
#     updated_path = os.path.splitext(json_file_path)[0] + "_fully_updated_conditionalChaining.json"
#     with open(updated_path, 'w', encoding='utf-8') as f:
#         json.dump(data, f, ensure_ascii=False, indent=2)

#     print(f"\n✅ All conditionalChaining QIDs updated successfully.")
#     print(f"📁 Updated file saved at: {updated_path}")
#     return updated_path

import json
import os
import re

def update_conditional_sentences_with_qid_matching(json_file_path):
    # Load JSON file
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Extract all valid QIDs
    all_valid_qids = set(entry.get("qid", "").strip() for entry in data.get("qna", []) if entry.get("qid"))

    # Create a mapping from button value (QID::<...>) to actual QID
    qid_mapping = {}
    for item in data.get("qna", []):
        qid = item.get("qid")
        if not qid:
            continue
        if "r" in item and "buttons" in item["r"]:
            for button in item["r"]["buttons"]:
                value = button.get("value")
                if value and value.startswith("QID::"):
                    qid_mapping[value] = qid

    # Update conditionalChaining values
    for entry in data.get("qna", []):
        chaining = entry.get("conditionalChaining")
        if chaining and isinstance(chaining, str):
            original_chaining = chaining.strip()

            # Case 1: Strict match for single QID string (including single/double quotes)
            match = re.match(r"['\"]?QID::([\w.\-]+)['\"]?$", original_chaining)
            if match:
                ref_qid = match.group(1).strip()
                for actual_qid in all_valid_qids:
                    if actual_qid == ref_qid or actual_qid.endswith("_" + ref_qid):
                        chaining = f"'QID::{actual_qid}'"
                        break
            else:
                # Case 2: Ternary expression or JS sentence-style expression
                matches = re.findall(r'"QID::([\w.\-]+)"', chaining)
                for ref_qid in matches:
                    for actual_qid in all_valid_qids:
                        if actual_qid == ref_qid or actual_qid.endswith("_" + ref_qid):
                            chaining = chaining.replace(f'"QID::{ref_qid}"', f'"QID::{actual_qid}"')
                            break

            # Print Before → After if changed
            if chaining != original_chaining:
                print(f"\nQID: {entry.get('qid')}")
                print(f"🔸 Before: {original_chaining}")
                print(f"✅ After : {chaining}")

            entry["conditionalChaining"] = chaining

    # Update button values to use QID::MLPLUS_... format
    for item in data.get("qna", []):
        if "r" in item and "buttons" in item["r"]:
            for button in item["r"]["buttons"]:
                value = button.get("value")
                if value and value.startswith("QID::") and value in qid_mapping:
                    button["value"] = f"QID::{qid_mapping[value]}"

    # Save updated JSON file
    updated_path = os.path.splitext(json_file_path)[0] + "_fully_updated.json"
    with open(updated_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ All conditionalChaining and button QIDs updated successfully.")
    print(f"📁 Updated file saved at: {updated_path}")
    return updated_path

# def update_qna_questions_multithreaded(json_file_path, max_workers=5):
#     base, ext = os.path.splitext(json_file_path)
#     copied_file_path = f"{base}_copy{ext}"
#     shutil.copy(json_file_path, copied_file_path)

#     with open(copied_file_path, 'r', encoding='utf-8-sig') as f:
#         data = json.load(f)

#     qna_list = data.get("qna", [])

#     # Placeholder for ordered updates
#     updated_qna = [None] * len(qna_list)

#     with ThreadPoolExecutor(max_workers=max_workers) as executor:
#         futures = [
#             executor.submit(process_single_qid_with_index, idx, entry)
#             for idx, entry in enumerate(qna_list)
#         ]

#         for future in as_completed(futures):
#             try:
#                 idx, updated_entry = future.result()

#                 # ✅ New QID generation logic (ENV_PREFIX + 3-digit index + original intent name)
#                 prefix = os.environ["INTENT_PREFIX_TEXT"]
#                 ordinal = str(idx + 1).zfill(3)
#                 original_intent = updated_entry.get("qid", "").strip().replace(" ", "_").replace('"', "").replace("'", "")
#                 new_qid = f"{prefix}_{ordinal}_{original_intent}"
#                 updated_entry["qid"] = new_qid

#                 updated_qna[idx] = updated_entry
#                 print(f"[{idx+1}/{len(qna_list)}] QID Processed: {new_qid}")

#             except Exception as e:
#                 print(f"[{idx+1}/{len(qna_list)}] ❌ Error during processing QID: {e}")

#     # Final JSON structure: all original structure, just updated "q" fields and new QID
#     data["qna"] = updated_qna

#     updated_file_path = f"{base}_updated{ext}"
#     with open(updated_file_path, 'w', encoding='utf-8') as f:
#         json.dump(data, f, ensure_ascii=False, indent=2)

#     return updated_file_path

import os
import shutil
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

def update_qna_questions_multithreaded(json_file_path, max_workers=20):
    base, ext = os.path.splitext(json_file_path)
    copied_file_path = f"{base}_copy{ext}"
    shutil.copy(json_file_path, copied_file_path)

    with open(copied_file_path, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)

    qna_list = data.get("qna", [])
    updated_qna = [None] * len(qna_list)

    skip_count = 0
    processed_count = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []

        for idx, entry in enumerate(qna_list):
            qid = entry.get("qid", "").strip()
            q_list = entry.get("q", [])

            prefix = os.environ["INTENT_PREFIX_TEXT"]
            ordinal = str(idx + 1).zfill(3)
            original_intent = qid.replace(" ", "_").replace('"', "").replace("'", "")
            new_qid = f"{prefix}_{ordinal}_{original_intent}"

            # ✅ Apply new QID always
            entry["qid"] = new_qid

            # ✅ Check skip conditions (but still apply QID prefix!)
            if (
                (len(q_list) == 1 and q_list[0].strip() == qid)
                or any("_" in q.strip() for q in q_list)
                or any("qid" in q.strip().lower() for q in q_list)
            ):
                updated_qna[idx] = entry
                skip_count += 1
                print(f"[{idx+1}/{len(qna_list)}] QID Skipped Processing (Condition Match): {new_qid}")
                continue

            # ✅ Process only if none of the conditions matched
            futures.append(executor.submit(process_single_qid_with_index, idx, entry))

        for future in as_completed(futures):
            try:
                idx, updated_entry = future.result()

                # QID already updated above, no need to update again
                updated_qna[idx] = updated_entry
                processed_count += 1
                print(f"[{idx+1}/{len(qna_list)}] QID Processed Fully: {updated_entry['qid']}")

            except Exception as e:
                print(f"[{idx+1}/{len(qna_list)}] ❌ Error during processing QID: {e}")

    data["qna"] = updated_qna
    updated_file_path = f"{base}_updated{ext}"
    with open(updated_file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Update Complete: {processed_count} Processed | {skip_count} Skipped (Prefix Applied Only)")
    return updated_file_path


# import json
# import os

# def replace_q_values_with_actual_qid_file(json_file_path):
#     base, ext = os.path.splitext(json_file_path)
#     output_file_path = f"{base}_qreplaced{ext}"

#     # Load the file
#     with open(json_file_path, 'r', encoding='utf-8-sig') as f:
#         data = json.load(f)

#     qna_list = data.get("qna", [])

#     # Replace q items containing 'qid' with the actual QID
#     for entry in qna_list:
#         actual_qid = entry.get("qid", "").strip()
#         q_list = entry.get("q", [])

#         updated_q_list = [
#             actual_qid if "qid" in q.strip().lower() else q
#             for q in q_list
#         ]

#         entry["q"] = updated_q_list

#     data["qna"] = qna_list

#     # Save to new file
#     with open(output_file_path, 'w', encoding='utf-8') as f:
#         json.dump(data, f, ensure_ascii=False, indent=2)

#     print(f"✅ Q values replaced successfully. Output saved to: {output_file_path}")
#     return output_file_path

import json
import os
import re

def replace_q_values_with_actual_qid_file(json_file_path):
    base, ext = os.path.splitext(json_file_path)
    output_file_path = f"{base}_qreplaced{ext}"

    # Load JSON file
    with open(json_file_path, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)

    qna_list = data.get("qna", [])

    for entry in qna_list:
        full_qid = entry.get("qid", "").strip()  # e.g., MLPLUS_001_createCase
        q_list = entry.get("q", [])

        # Extract original QID part by removing prefix (e.g., createCase from MLPLUS_001_createCase)
        original_qid = re.sub(r'^MLPLUS_\d{3}_', '', full_qid)

        updated_q_list = []
        for q in q_list:
            q_clean = q.strip()
            if q_clean.lower().find("qid") != -1:
                updated_q_list.append(full_qid)  # Replace if contains 'qid'
            elif q_clean == original_qid:
                updated_q_list.append(full_qid)  # Replace if matches original qid
            else:
                updated_q_list.append(q)  # Keep as-is

        entry["q"] = updated_q_list

    data["qna"] = qna_list

    # Save updated file
    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ Q values replaced using QID. Output saved to: {output_file_path}")
    return output_file_path



######################################################################
# def update_qna_questions_multithreaded(json_file_path, max_workers=5):
#     base, ext = os.path.splitext(json_file_path)
#     copied_file_path = f"{base}_copy{ext}"
#     shutil.copy(json_file_path, copied_file_path)

#     with open(copied_file_path, 'r', encoding='utf-8-sig') as f:
#         data = json.load(f)

#     qna_list = data.get("qna", [])
#     updated_qna = [None] * len(qna_list)

#     skipped_count = 0
#     processed_count = 0

#     with ThreadPoolExecutor(max_workers=max_workers) as executor:
#         futures = []

#         for idx, entry in enumerate(qna_list):
#             qid = entry.get("qid", "").strip()
#             q_list = entry.get("q", [])

#             # ✅ Skip Condition 1: QID equals only item in q
#             if len(q_list) == 1 and q_list[0].strip() == qid:
#                 updated_qna[idx] = entry
#                 skipped_count += 1
#                 print(f"[{idx+1}/{len(qna_list)}] QID Skipped (QID == Q[0]): {qid}")
#                 continue

#             # ✅ Skip Condition 2: any question contains underscore
#             if any("_" in q.strip() for q in q_list):
#                 updated_qna[idx] = entry
#                 skipped_count += 1
#                 print(f"[{idx+1}/{len(qna_list)}] QID Skipped (underscore in Q): {qid}")
#                 continue

#             # ✅ Skip Condition 3: any question contains 'qid' (case-insensitive)
#             if any("qid" in q.strip().lower() for q in q_list):
#                 updated_qna[idx] = entry
#                 skipped_count += 1
#                 print(f"[{idx+1}/{len(qna_list)}] QID Skipped ('qid' in Q): {qid}")
#                 continue

#             # ✅ Submit for further processing
#             futures.append(executor.submit(process_single_qid_with_index, idx, entry))

#         for future in as_completed(futures):
#             try:
#                 idx, updated_entry = future.result()

#                 # ✅ QID renaming logic
#                 prefix = os.environ["INTENT_PREFIX_TEXT"]
#                 ordinal = str(idx + 1).zfill(3)
#                 original_intent = updated_entry.get("qid", "").strip().replace(" ", "_").replace('"', "").replace("'", "")
#                 new_qid = f"{prefix}_{ordinal}_{original_intent}"
#                 updated_entry["qid"] = new_qid

#                 updated_qna[idx] = updated_entry
#                 processed_count += 1
#                 print(f"[{idx+1}/{len(qna_list)}] QID Processed: {new_qid}")

#             except Exception as e:
#                 print(f"[{idx+1}/{len(qna_list)}] ❌ Error during processing QID: {e}")

#     # Final JSON output
#     data["qna"] = updated_qna
#     updated_file_path = f"{base}_updated{ext}"
#     with open(updated_file_path, 'w', encoding='utf-8') as f:
#         json.dump(data, f, ensure_ascii=False, indent=2)

#     print(f"\n✅ Update Complete: {processed_count} Processed | {skipped_count} Skipped")
#     return updated_file_path
##############################################################################


def update_json_copy_with_optimized_utterances(original_file_path, target_qid, optimized_utterances):
    """
    Creates a copy of the original JSON file and updates the utterances for the specified QID.

    Args:
        original_file_path (str): Path to the original JSON file.
        target_qid (str): The QID whose utterances need to be updated.
        optimized_utterances (list): List of optimized utterances.

    Returns:
        str: Path to the new updated JSON file.
    """
    updated_file_path = "updated_qna.json"  # New output file name

    # Load original JSON file
    with open(original_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Update only the QID's utterances
    for item in data.get("qna", []):
        if item.get("qid") == target_qid:
            item["q"] = optimized_utterances

    # Save to new file without touching the original
    with open(updated_file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    return updated_file_path
