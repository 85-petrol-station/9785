import json
import os
import re

# Load cet4.json reference
with open('cet4.json', 'r') as f:
    cet4_data = json.load(f)

# Build lookup: lowercase key -> actual key in cet4.json
cet4_lookup = {}
for key in cet4_data:
    cet4_lookup[key.lower()] = key

print(f"Reference cet4.json: {len(cet4_data)} words")

# Process all group files
cet4_dir = 'cet4'
total_removed = 0
total_kept = 0
results = []

for group_num in range(1, 31):
    filename = f'group_{group_num}_word_time.json'
    filepath = os.path.join(cet4_dir, filename)

    if not os.path.exists(filepath):
        print(f"  SKIP: {filename} not found")
        continue

    with open(filepath, 'r') as f:
        group_data = json.load(f)

    original_count = len(group_data)

    # Filter: keep only entries whose full_text (lowercased) matches a key in cet4
    new_data = []
    removed_words = []
    for entry in group_data:
        word_lower = entry['full_text'].lower().strip()
        if word_lower in cet4_lookup:
            # Normalize full_text to match the cet4.json word field
            entry['full_text'] = cet4_data[cet4_lookup[word_lower]]['word']
            new_data.append(entry)
        else:
            removed_words.append(entry['full_text'])

    # Update the remaining count
    kept_count = len(new_data)
    removed_count = original_count - kept_count
    total_removed += removed_count
    total_kept += kept_count

    # Re-index segment_index and update audio_file/audio_path
    for i, entry in enumerate(new_data, start=1):
        entry['segment_index'] = i
        seg_num = f'{i:04d}'
        entry['audio_file'] = f'group{group_num}_seg_{seg_num}.mp3'
        entry['audio_path'] = f'group_{group_num}_audio/group{group_num}_seg_{seg_num}.mp3'

    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)

    if removed_count > 0:
        print(f"  group_{group_num}: {original_count} -> {kept_count} (removed {removed_count}: {removed_words})")
    else:
        print(f"  group_{group_num}: {original_count} -> {kept_count} (no changes)")

    results.append({
        'group': group_num,
        'original': original_count,
        'kept': kept_count,
        'removed': removed_count,
        'removed_words': removed_words
    })

print(f"\n{'='*60}")
print(f"SUMMARY")
print(f"{'='*60}")
print(f"Total groups processed: {len(results)}")
print(f"Total entries before: {sum(r['original'] for r in results)}")
print(f"Total entries after:  {total_kept}")
print(f"Total removed:        {total_removed}")

# List all removed words
all_removed = set()
for r in results:
    all_removed.update(r['removed_words'])
print(f"\nAll removed words ({len(all_removed)} unique):")
for w in sorted(all_removed):
    print(f"  - {w}")
