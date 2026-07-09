import hid

print("====================================================")
print("🔍 正在全盤掃描新電腦上所有已連接的 HID 設備...")
print("====================================================")

all_devices = hid.enumerate()

if not all_devices:
    print("❌ 悲劇！系統連一個 HID 設備都撈不到，請確認 python-hidapi 是否安裝正確。")
else:
    print(f"總共發現 {len(all_devices)} 個 HID 通道特徵：\n")
    for idx, dev in enumerate(all_devices):
        # 格式化輸出
        vid = f"0x{dev['vendor_id']:04X}"
        pid = f"0x{dev['product_id']:04X}"
        mfg = dev.get("manufacturer_string", "未知廠商")
        prod = dev.get("product_string", "未知產品")
        interface = dev.get("interface_number", -1)
        usage_pg = dev.get("usage_page", 0)

        # 只要廠商名稱、產品名稱包含關鍵字，或者 Usage Page 是自訂區段，就加上高亮標籤
        keyword_match = ""
        if (
            "ityt" in str(mfg).lower()
            or "ityt" in str(prod).lower()
            or usage_pg == 65280
        ):
            keyword_match = " 🎯【疑似目標硬體！】"

        print(
            f"[{idx}] VID: {vid} | PID: {pid} | Interface: {interface} | Usage Page: {usage_pg}{keyword_match}"
        )
        print(f"    廠商: {mfg} | 產品: {prod}")
        print("-" * 60)

print("\n🏁 掃描結束。")
