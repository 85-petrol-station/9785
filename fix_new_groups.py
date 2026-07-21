import json, os

with open('cet4.json', 'r') as f:
    cet4 = json.load(f)

# Build lookup: lowercase -> (cet4_key, cet4_word_field)
cet4_lookup = {}
for key, val in cet4.items():
    cet4_lookup[val['word'].lower()] = val['word']

print("=" * 60)
print("修正新增 group_31 ~ group_36")
print("=" * 60)

for group_num in [31, 32, 33, 34, 35, 36]:
    fp = f'cet4/group_{group_num}_word_time.json'
    with open(fp) as f:
        entries = json.load(f)

    original_count = len(entries)
    new_entries = []
    removed = []

    for e in entries:
        # Clean full_text: strip whitespace, remove trailing commas/punctuation
        raw_text = e['full_text'].strip()
        # Remove trailing punctuation
        cleaned = raw_text.rstrip(',.，。;；!！?？:：')
        cleaned_lower = cleaned.lower()

        # Check against cet4.json
        if cleaned_lower not in cet4_lookup:
            removed.append(raw_text)
            continue

        # Build standardized entry matching groups 1-30 format
        new_entry = {
            "group_id": group_num,
            "full_text": cet4_lookup[cleaned_lower],  # Canonical word form
            "segment_index": len(new_entries) + 1,
            "audio_file": f"group{group_num}_seg_{len(new_entries)+1:04d}.mp3",
            "audio_path": f"group_{group_num}_audio/group{group_num}_seg_{len(new_entries)+1:04d}.mp3"
        }
        new_entries.append(new_entry)

    # Write back
    with open(fp, 'w', encoding='utf-8') as f:
        json.dump(new_entries, f, ensure_ascii=False, indent=2)

    print(f"group_{group_num}: {original_count} -> {len(new_entries)} "
          f"(修正group_id/audio命名/字段格式/单词标准化"
          f"{'; 删除' + str(len(removed)) + '个不匹配: ' + ', '.join(removed) if removed else ''})")

# ==========================================
# Also re-check and fix groups 1-30 to ensure consistency
# ==========================================
print(f"\n{'=' * 60}")
print("复查 group_1 ~ group_30")
print("=" * 60)

for group_num in range(1, 31):
    fp = f'cet4/group_{group_num}_word_time.json'
    with open(fp) as f:
        entries = json.load(f)

    new_entries = []
    removed = []

    for e in entries:
        raw_text = e['full_text'].strip()
        cleaned = raw_text.rstrip(',.，。;；!！?？:：')
        cleaned_lower = cleaned.lower()

        if cleaned_lower not in cet4_lookup:
            removed.append(raw_text)
            continue

        new_entry = {
            "group_id": group_num,
            "full_text": cet4_lookup[cleaned_lower],
            "segment_index": len(new_entries) + 1,
            "audio_file": f"group{group_num}_seg_{len(new_entries)+1:04d}.mp3",
            "audio_path": f"group_{group_num}_audio/group{group_num}_seg_{len(new_entries)+1:04d}.mp3"
        }
        new_entries.append(new_entry)

    if removed:
        with open(fp, 'w', encoding='utf-8') as f:
            json.dump(new_entries, f, ensure_ascii=False, indent=2)
        print(f"group_{group_num}: {len(entries)} -> {len(new_entries)} "
              f"(删除{len(removed)}个: {removed})")

print(f"\n{'=' * 60}")
print("最终汇总")
print("=" * 60)

total_entries = 0
total_words = set()
for group_num in range(1, 37):
    fp = f'cet4/group_{group_num}_word_time.json'
    if os.path.exists(fp):
        with open(fp) as f:
            entries = json.load(f)
        total_entries += len(entries)
        for e in entries:
            total_words.add(e['full_text'].lower())

# Count remaining missing
valid_cet4 = sum(1 for v in cet4.values()
                 if not (v['meaning'] == '(待补充)' or not v['phonetic'] or not v['pos']))
missing = valid_cet4 - len(total_words)

print(f"总 group 文件: 36")
print(f"总音频条目:   {total_entries}")
print(f"不同单词数:   {len(total_words)}")
print(f"cet4有效词:   {valid_cet4}")
print(f"仍缺失:       {missing}")
print(f"匹配率:       {len(total_words)}/{valid_cet4} = {len(total_words)/valid_cet4*100:.1f}%")
