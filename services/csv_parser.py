import pandas as pd
from io import BytesIO

ALLOWED_TYPES = {"text", "radio", "dropdown", "rating", "checkbox"}

def parse_csv(file_bytes: bytes) -> list:
    """
    Reads CSV bytes, validates columns, returns list of question dicts.
    """
    try:
        df = pd.read_csv(BytesIO(file_bytes))
    except Exception:
        raise ValueError("Could not read file. Make sure it is a valid CSV.")

    # Normalize column names — strip spaces, lowercase
    df.columns = df.columns.str.strip().str.lower()

    # Check required columns exist
    required_columns = {"question_text", "type", "options"}
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing these columns: {missing}. Required: question_text, type, options")

    # Check file is not empty
    if df.empty:
        raise ValueError("CSV file has no questions.")

    questions = []

    for index, row in df.iterrows():
        question_text = str(row["question_text"]).strip()
        question_type = str(row["type"]).strip().lower()
        options       = str(row["options"]).strip() if pd.notna(row["options"]) else None

        # Skip completely empty rows
        if not question_text or question_text == "nan":
            continue

        # Validate question type
        if question_type not in ALLOWED_TYPES:
            raise ValueError(
                f"Row {index + 2}: Invalid type '{question_type}'. "
                f"Allowed types are: {ALLOWED_TYPES}"
            )

        # text type should not have options
        if question_type == "text" and options and options != "nan":
            options = None

        # non-text types should have options
        if question_type != "text" and (not options or options == "nan"):
            raise ValueError(
                f"Row {index + 2}: Question type '{question_type}' "
                f"requires options but none were provided."
            )

        questions.append({
            "question_text": question_text,
            "question_type": question_type,
            "options":       options if options != "nan" else None,
            "order":         index
        })

    if not questions:
        raise ValueError("No valid questions found in CSV.")

    return questions 