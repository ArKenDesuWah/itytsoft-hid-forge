import hid
import time

TARGET_VID = 0x514C
TARGET_PID = 0x8850
TARGET_USAGE_PAGE = 65280


def get_test_path():
    devices = hid.enumerate(TARGET_VID, TARGET_PID)
    for dev in devices:
        if dev.get("usage_page") == TARGET_USAGE_PAGE:
            return dev["path"]
    if devices:
        return devices[0]["path"]
    return None


path = get_test_path()
if not path:
    print("❌ 錯誤：找不到有線直連設備！請檢查線材。")
    exit()

dev = hid.device()
dev.open_path(path)

# ====================================================
# 🎯 核心 Payload 定義 (移除了開頭的 0x03，純粹 64 位元組數據)
# ====================================================
# 將 Layer 1 改為標準 A 鍵 (Keycode: 0x04)
base_data_raw = [0xFD, 0x01, 0x01, 0x01, 0x00, 0x01, 0x00, 0x00, 0x04, 0x00, 0x00]
padded_data = (base_data_raw + [0x00] * 64)[:64]  # 嚴格對齊 64 位元組

# 假設原本的 Commit 除去 0x03 後是 [0x01, 0x00, 0x00, 0x00]
commit_data_raw = [0x01, 0x00, 0x00, 0x00]
padded_commit = (commit_data_raw + [0x00] * 64)[:64]  # 嚴格對齊 64 位元組

print("====================================================")
print("🚀 啟動物理對齊 V3 測試程序 (不猜測，純對齊比對)")
print("====================================================")

# 構造 Windows 底層四種不同的核心發送包
combinations = {
    "組合 A: 標頭外掛 0x03 - Output (Write) 通道": (
        "write",
        [0x03] + padded_data,
        [0x03] + padded_commit,
    ),
    "組合 B: 標頭外掛 0x03 - Feature 通道": (
        "feature",
        [0x03] + padded_data,
        [0x03] + padded_commit,
    ),
    "組合 C: 前導雙零 [0x00, 0x03] - Output (Write) 通道": (
        "write",
        [0x00, 0x03] + padded_data[:-1],
        [0x00, 0x03] + padded_commit[:-1],
    ),
    "組合 D: 前導雙零 [0x00, 0x03] - Feature 通道": (
        "feature",
        [0x00, 0x03] + padded_data[:-1],
        [0x00, 0x03] + padded_commit[:-1],
    ),
}

for name, (method, config_packet, commit_packet) in combinations.items():
    print(f"\n🧪 正在執行【{name}】...")
    print(f"   配置包長度: {len(config_packet)} | Commit 包長度: {len(commit_packet)}")

    try:
        if method == "write":
            dev.write(config_packet)
            time.sleep(0.02)
            dev.write(commit_packet)
        else:
            dev.send_feature_report(config_packet)
            time.sleep(0.02)
            dev.send_feature_report(commit_packet)

        print("   -> 雙階封包已成功送出作業系統核心緩衝區。")
    except Exception as e:
        print(f"   ❌ 被作業系統拒絕 (API Error): {e}")

    print("👉 請按一下實體小鍵盤，測試是否有打出 [A] 鍵？")
    print("----------------------------------------------------")
    time.sleep(2.5)

dev.close()
print("🏁 V3 實體測試完畢。")
