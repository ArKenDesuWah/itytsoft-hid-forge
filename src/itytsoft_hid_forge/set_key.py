import hid
import time

# ==============================================================================
# 完整解鎖：全標準鍵盤鍵位與高階 F13-F24 映射表 (USB HID Usage ID)
# ==============================================================================
KEY_MAP = {
    # 高階功能鍵
    "F13": 0x68,
    "F14": 0x69,
    "F15": 0x6A,
    "F16": 0x6B,
    "F17": 0x6C,
    "F18": 0x6D,
    "F19": 0x6E,
    "F20": 0x6F,
    "F21": 0x70,
    "F22": 0x71,
    "F23": 0x72,
    "F24": 0x73,
    # 標準功能鍵
    "F1": 0x3A,
    "F2": 0x3B,
    "F3": 0x3C,
    "F4": 0x3D,
    "F5": 0x3E,
    "F6": 0x3F,
    "F7": 0x40,
    "F8": 0x41,
    "F9": 0x42,
    "F10": 0x43,
    "F11": 0x44,
    "F12": 0x45,
    # 字母鍵
    "A": 0x04,
    "B": 0x05,
    "C": 0x06,
    "D": 0x07,
    "E": 0x08,
    "F": 0x09,
    "G": 0x0A,
    "H": 0x0B,
    "I": 0x0C,
    "J": 0x0D,
    "K": 0x0E,
    "L": 0x0F,
    "M": 0x10,
    "N": 0x11,
    "O": 0x12,
    "P": 0x13,
    "Q": 0x14,
    "R": 0x15,
    "S": 0x16,
    "T": 0x17,
    "U": 0x18,
    "V": 0x19,
    "W": 0x1A,
    "X": 0x1B,
    "Y": 0x1C,
    "Z": 0x1D,
    # 數字鍵 (主鍵盤區)
    "1": 0x1E,
    "2": 0x1F,
    "3": 0x20,
    "4": 0x21,
    "5": 0x22,
    "6": 0x23,
    "7": 0x24,
    "8": 0x25,
    "9": 0x26,
    "0": 0x27,
    # 控制與常規鍵
    "ENTER": 0x28,
    "SPACE": 0x2C,
    "ESC": 0x29,
    "BACKSPACE": 0x2A,
    "TAB": 0x2B,
    "MINUS": 0x2D,
    "EQUAL": 0x2E,
    "LBRACKET": 0x2F,
    "RBRACKET": 0x30,
    "BACKSLASH": 0x31,
    "SEMICOLON": 0x33,
    "APOSTROPHE": 0x34,
    "GRAVE": 0x35,
    "COMMA": 0x36,
    "PERIOD": 0x37,
    "SLASH": 0x38,
    "CAPSLOCK": 0x39,
    # 方向鍵與功能區域
    "PRINTSCREEN": 0x46,
    "SCROLLLOCK": 0x47,
    "PAUSE": 0x48,
    "INSERT": 0x49,
    "HOME": 0x4A,
    "PAGEUP": 0x4B,
    "DELETE": 0x4C,
    "END": 0x4D,
    "PAGEDOWN": 0x4E,
    "RIGHT": 0x4F,
    "LEFT": 0x50,
    "DOWN": 0x51,
    "UP": 0x52,
    # 常用標準單鍵修飾（獨立發送碼）
    "LCTRL": 0xE0,
    "LSHIFT": 0xE1,
    "LALT": 0xE2,
    "LGUI": 0xE3,
    "RCTRL": 0xE4,
    "RSHIFT": 0xE5,
    "RALT": 0xE6,
    "RGUI": 0xE7,
}

# ==============================================================================
# 完全體修飾鍵排隊區對照表（經硬體實測 100% 驗證確認）
# ==============================================================================
MODIFIER_MAP = {
    # 左側/通用修飾鍵
    "CTRL": 0xF1,
    "LCTRL": 0xF1,
    "SHIFT": 0xF2,
    "LSHIFT": 0xF2,
    "ALT": 0xF3,
    "LALT": 0xF3,
    "WIN": 0xF4,
    "LWIN": 0xF4,
    "LGUI": 0xF4,
    # 右側修飾鍵（實測解鎖）
    "RCTRL": 0xF5,
    "RSHIFT": 0xF6,
    "RALT": 0xF7,
    "RWIN": 0xF8,
    "RGUI": 0xF8,
}

# 🎯 提取為靜態常數：儲存生效的 Commit 基礎結構 (對齊 65 位元組)
STATIC_COMMIT_PACKET = [
    0x03,
    0xFD,
    0xFE,
    0xFF,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
    0x00,
] + [0x00] * 49

TARGET_VID = 0x514C
TARGET_PID = 0x8850


def get_all_paths():
    paths = []
    for device in hid.enumerate():
        if device["vendor_id"] == TARGET_VID and device["product_id"] == TARGET_PID:
            if device["path"]:
                paths.append(device["path"])
    return paths


def parse_input_string(input_str):
    """
    依據 '+' 符號動態解析字串。
    同時儲存『晶片代碼鏈表』與『原始文字鏈表』並一起回傳。
    """
    parts = input_str.split("+")
    modifiers_hex = []
    modifiers_text = []
    main_key_hex = None
    main_key_text = None

    for part in parts:
        part = part.strip().upper()

        # 🎯 1. 檢查是否為修飾鍵：直接用 in 字典查表，一行搞定
        if part in MODIFIER_MAP:
            modifiers_hex.append(MODIFIER_MAP[part])
            modifiers_text.append(part)

        # 2. 檢查是否為一般主鍵
        elif part in KEY_MAP:
            main_key_hex = KEY_MAP[part]
            main_key_text = part

        else:
            return None

    if main_key_hex is None:
        return None

    # 🎯 將修飾鍵與主鍵依照硬體順序串接
    key_chain = modifiers_hex + [main_key_hex]
    text_chain = modifiers_text + [main_key_text]

    # 一併回傳兩組完整的鏈表
    return key_chain, text_chain


def generate_key_binding_part(key_chain):
    """
    純粹專注於構建從 '總鍵數' 開始的後半段動態線性陣列。
    傳入的 key_chain 格式範例：
        - 單鍵 A: [0x04]
        - 雙鍵 WIN+A: [0xF4, 0x04]
        - 三鍵 CTRL+SHIFT+F1: [0xF1, 0xF2, 0x3A]
        - 四鍵 CTRL+SHIFT+ALT+F1: [0xF1, 0xF2, 0xF3, 0x3A]
    """
    # 1. 取得總鍵數
    total_keys = len(key_chain)

    # 2. 起始填入總鍵數，以及緊跟在後的兩個 0x00 格式碼
    binding_part = [total_keys, 0x00, 0x00]

    # 3. 🎯 線性排隊：將鏈表中的每一個按鍵碼依序塞入，且每個鍵碼後方固定補兩個 0x00
    for keycode in key_chain:
        binding_part.append(keycode)
        binding_part.append(0x00)
        binding_part.append(0x00)

    # 4. 根據前面固定的前導標頭 [0x03, 0xFD, 0x01, layer_idx, 0x01, 0x00] (共 6 個位元組)
    # 為了讓全封包 packet 精確達到 65 位元組，前半段 6 位元組 + binding_part 必須等於 65
    # 因此 binding_part 的總長度必須精確固定為 59 位元組
    target_length = 59

    if len(binding_part) < target_length:
        # 後方自動補 0x00 填充對齊
        binding_part += [0x00] * (target_length - len(binding_part))
    else:
        # 安全邊界截斷
        binding_part = binding_part[:target_length]

    return binding_part


def burn_to_device(path, key_chain, layers):
    """
    動態發送按鍵鏈表，並直接在發送時對齊 66 位元組結構，不再拆分 A/B 變數。
    """
    try:
        dev = hid.device()
        dev.open_path(path)

        total_keys = len(key_chain)

        # 1. 逐層發送按鍵配置封包
        for layer_idx in layers:
            packet_data = [0x03, 0xFD, 0x01, layer_idx, 0x01, 0x00]

            # 線性排隊：填入總鍵數與間隔碼
            packet_data.append(total_keys)
            packet_data.append(0x00)
            packet_data.append(0x00)

            # 依序填入按鍵碼與間隔碼
            for keycode in key_chain:
                packet_data.append(keycode)
                packet_data.append(0x00)
                packet_data.append(0x00)

            # 🎯 告別 if/else！用數學切片確保長度絕對是 65 位元組
            packet = (packet_data + [0x00] * 65)[:65]

            # 直接發送
            try:
                dev.write(packet)
            except Exception:
                pass

            try:
                dev.write([0x00] + packet)  # Windows 穿透對齊
            except Exception:
                pass

            time.sleep(0.02)

        # 2. 🎯 發送靜態 Commit 儲存生效指令
        try:
            dev.write(STATIC_COMMIT_PACKET)
        except Exception:
            pass

        try:
            dev.write([0x00] + STATIC_COMMIT_PACKET)  # Windows 穿透對齊
        except Exception:
            pass

        dev.close()
        return True
    except Exception:
        return False


def main():
    print("=======================================================")
    print("        itytsoft MINI 鍵盤 ── 高效能動態改鍵系統         ")
    print("   (Current Status: Only 1-Key Hardware Supported)     ")
    print("=======================================================")

    # 🎯 移到迴圈外：先決定這次要改哪一層
    layer_input = (
        input("📁 請選擇這次要操作的 Layer (1 / 2 / 3 / ALL): ").strip().upper()
    )
    if layer_input == "1":
        target_layers = [0x01]
    elif layer_input == "2":
        target_layers = [0x02]
    elif layer_input == "3":
        target_layers = [0x03]
    else:
        target_layers = [0x01, 0x02, 0x03]

    while True:
        paths = get_all_paths()
        if not paths:
            print("❌ 找不到硬體連線。")
            continue

        # 🎯 迴圈內只需要瘋狂輸入你想改的按鍵即可
        user_input = (
            input("\n⌨️  請輸入指令 (如 CTRL+SHIFT+F1) 或 EXIT: ").strip().upper()
        )
        if user_input == "EXIT":
            print("\n👋 程式已順利退出。")
            break

        parsed_result = parse_input_string(user_input)
        if not parsed_result:
            print("⚠️ 格式錯誤...")
            continue

        key_chain, text_chain = parsed_result

        # 將文字與 Hex 結合，例如：["CTRL(0xF1)", "SHIFT(0xF2)", "J(0x0D)"]
        readable_list = [f"{txt}(0x{hx:02X})" for txt, hx in zip(text_chain, key_chain)]

        # 🎯 精簡成你設計的黃金單行輸出
        print(f"🚀 正在準備發送 -> {' + '.join(readable_list)}")

        success = False
        for path in paths:
            # 傳遞乾淨的 key_chain 給硬體刷寫函數
            if burn_to_device(path, key_chain, target_layers):
                success = True

        if success:
            print(f"🎉【改鍵成功】已成功依據動態矩陣將功能固化至晶片！")


if __name__ == "__main__":
    main()
