import os
import time
from crawler_modules.config import get_config


def cleanup_old_pickles():
    config = get_config()
    days = config.get("cleanup_days", 7)
    pickle_dir = "data/pickle"

    if not os.path.isdir(pickle_dir):
        print(f"⚠️ Directory not found: {pickle_dir}")
        return

    now = time.time()
    deleted = 0

    for fname in os.listdir(pickle_dir):
        if not fname.endswith(".pkl"):
            continue
        path = os.path.join(pickle_dir, fname)
        file_age_days = (now - os.path.getmtime(path)) / 86400
        if file_age_days > days:
            os.remove(path)
            deleted += 1
            print(f"🗑️ Deleted old pickle file: {fname} ({file_age_days:.1f} days old)")

    print(f"✅ Cleanup complete. {deleted} file(s) deleted.")


if __name__ == "__main__":
    cleanup_old_pickles()
