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

import json
import os
import shutil

def update_qna_questions_with_backup(json_file_path):
    base, ext = os.path.splitext(json_file_path)
    copy_file_path = f"{base}_copy{ext}"
    shutil.copy(json_file_path, copy_file_path)

    with open(copy_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for entry in data.get("qna", []):
        qid = entry.get("qid")
        questions = entry.get("q", [])
        print(f"\n[Processing QID: {qid}] — Original Qs: {len(questions)}")

        optimized_questions = azure_openai_model_for_optimizations_all(qid, questions)

        if optimized_questions:
            print(f"[Optimized Qs: {len(optimized_questions)}]")
            entry["q"] = optimized_questions
        else:
            print(f"[Fallback] Using original questions for QID: {qid}")
            entry["q"] = questions  # keep original

    updated_file_path = f"{base}_updated{ext}"
    with open(updated_file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return updated_file_path