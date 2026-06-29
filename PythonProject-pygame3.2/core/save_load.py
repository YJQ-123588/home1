import json
import os
from datetime import datetime

SAVE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "saves")
MAX_SLOTS = 3


def _ensure_save_dir():
    os.makedirs(SAVE_DIR, exist_ok=True)


def _save_path(slot):
    return os.path.join(SAVE_DIR, f"save_{slot}.json")


def save_game(slot, game_state):
    """存档"""
    if slot < 1 or slot > MAX_SLOTS:
        return False
    _ensure_save_dir()
    data = {
        "slot": slot,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "state": game_state
    }
    try:
        with open(_save_path(slot), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"存档失败: {e}")
        return False


def load_game(slot):
    """读档"""
    if slot < 1 or slot > MAX_SLOTS:
        return None
    path = _save_path(slot)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"读档失败: {e}")
        return None


def delete_game(slot):
    """删档"""
    if slot < 1 or slot > MAX_SLOTS:
        return False
    path = _save_path(slot)
    if os.path.exists(path):
        try:
            os.remove(path)
            return True
        except Exception:
            return False
    return False


def get_all_saves():
    """获取所有存档信息"""
    _ensure_save_dir()
    saves = {}
    for slot in range(1, MAX_SLOTS + 1):
        data = load_game(slot)
        if data:
            saves[slot] = data
    return saves
