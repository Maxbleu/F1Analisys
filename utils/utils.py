from fastapi import HTTPException

def format_time_mmssmmm(seconds):
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    return f"{minutes}:{remaining_seconds:06.3f}"

def send_error_message(status_code, title, message):
    raise HTTPException(
        status_code= status_code,
        detail={
            "error": title,
            "message": message,
        }
    )