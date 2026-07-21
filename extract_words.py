#!/usr/bin/env python3
"""
从 PDF 提取四六级单词，输出为 cet4.json / cet6.json 格式。

用法：
  1. 安装依赖：pip install pdfplumber
  2. 运行：python3 extract_words.py 你的单词.pdf --type cet4
  3. 也支持从剪贴板文本直接解析：python3 extract_words.py --clipboard --type cet4

PDF 格式要求（每行）：
  1.peril [ˈperəl] n.危险
  2.experienced [ɪkˈspɪəriənst] adj.有经验的;熟练的

输出格式（与现有 cet4.json 兼容）：
  {"peril": {"word":"peril","type":"cet4","phonetic":"/ˈperəl/","meaning":"危险","pos":"n."}, ...}
"""

import re
import json
import sys
import argparse

# 匹配: 编号.单词 [音标] 词性.释义
LINE_PATTERN = re.compile(
    r'^\d+\.\s*'           # 编号.
    r'([a-zA-Z\-]+)\s*'    # 单词 (含连字符)
    r'\[(.+?)\]\s*'         # [音标]
    r'(.+)$'               # 词性.释义
)

# 分离 词性.释义 组合
# 支持: n.危险 / adj.有经验的;熟练的 / n./v.谋杀 / n.账户;描述 v.认为是
POS_LIST = ['n', 'v', 'adj', 'adv', 'prep', 'conj', 'pron', 'num', 'art', 'int', 'aux', 'vi', 'vt', 'abbr']
POS_RE = re.compile(
    r'(' + '|'.join(POS_LIST) + r')'   # 词性
    r'(?:/(?:' + '|'.join(POS_LIST) + r'))*'  # 可选 /另一词性
    r'\.'                               # 句点
)

def split_pos_meaning(text):
    text = text.strip()

    # 找所有 词性. 位置
    matches = list(POS_RE.finditer(text))
    if not matches:
        return '', text

    pairs = []
    for i, m in enumerate(matches):
        pos = m.group(0)  # 如 "n." "n./v." "adj."
        start = m.end()
        # 释义结束位置: 下一个词性前 或 文本末尾
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        meaning = text[start:end].strip().rstrip(';；')
        pairs.append((pos, meaning))

    # 合并
    pos_all = '；'.join(p for p, _ in pairs) if len(pairs) > 1 else pairs[0][0]
    meaning_all = '；'.join(m for _, m in pairs) if len(pairs) > 1 else pairs[0][1]

    return pos_all, meaning_all


def parse_line(line):
    """解析一行文本，返回 (word, phonetic, pos, meaning) 或 None"""
    line = line.strip()
    if not line:
        return None

    match = LINE_PATTERN.match(line)
    if not match:
        # 尝试宽松匹配：单词 [音标] 其余
        loose = re.match(r'^(\d+\.)?\s*([a-zA-Z\-]+)\s*\[(.+?)\]\s*(.*)', line)
        if loose:
            word = loose.group(2).strip()
            phonetic = '/' + loose.group(3).strip() + '/'
            pos_meaning = loose.group(4).strip()
            pos, meaning = split_pos_meaning(pos_meaning)
            return word, phonetic, meaning, pos
        return None

    word = match.group(1).strip()
    phonetic = '/' + match.group(2).strip() + '/'
    pos_meaning = match.group(3).strip()
    pos, meaning = split_pos_meaning(pos_meaning)

    return word, phonetic, meaning, pos


def extract_from_text(text, word_type='cet4'):
    """从文本中提取所有单词"""
    words = {}
    errors = []

    for line_num, line in enumerate(text.split('\n'), 1):
        result = parse_line(line)
        if result is None:
            if line.strip():
                errors.append(f"第{line_num}行无法解析: {line[:60]}...")
            continue

        word, phonetic, meaning, pos = result
        key = word.lower()
        # 如果重复，保留第一次出现的
        if key in words:
            continue

        words[key] = {
            "word": word,
            "type": word_type,
            "phonetic": phonetic,
            "meaning": meaning,
            "pos": pos
        }

    if errors:
        print(f"⚠️  {len(errors)} 行未能解析:")
        for e in errors[:10]:
            print(f"   {e}")
        if len(errors) > 10:
            print(f"   ... 还有 {len(errors) - 10} 行")

    return words


def main():
    parser = argparse.ArgumentParser(description='从 PDF 或文本提取四六级单词')
    parser.add_argument('file', nargs='?', help='PDF 文件路径')
    parser.add_argument('--type', default='cet4', choices=['cet4', 'cet6'],
                        help='单词类型 (默认 cet4)')
    parser.add_argument('--output', '-o', help='输出 JSON 文件路径')
    parser.add_argument('--clipboard', '-c', action='store_true',
                        help='从剪贴板读取文本（Mac 需安装 pbpaste）')
    parser.add_argument('--txt', help='从 TXT 文本文件读取')

    args = parser.parse_args()

    text = ''
    source = ''

    if args.clipboard:
        import subprocess
        text = subprocess.check_output(['pbpaste']).decode('utf-8')
        source = '剪贴板'
    elif args.txt:
        with open(args.txt, 'r', encoding='utf-8') as f:
            text = f.read()
        source = args.txt
    elif args.file and args.file.endswith('.pdf'):
        try:
            import pdfplumber
        except ImportError:
            print("请先安装 pdfplumber: pip install pdfplumber")
            sys.exit(1)

        with pdfplumber.open(args.file) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text += t + '\n'
        source = args.file
    elif args.file:
        # 当作 txt 处理
        with open(args.file, 'r', encoding='utf-8') as f:
            text = f.read()
        source = args.file
    else:
        print("请提供 PDF 文件路径，或使用 --clipboard 从剪贴板读取")
        print("示例: python3 extract_words.py words.pdf --type cet4")
        sys.exit(1)

    if not text.strip():
        print(f"❌ 未能从 {source} 提取到任何文本")
        sys.exit(1)

    print(f"从 {source} 读取了 {len(text)} 个字符")

    words = extract_from_text(text, args.type)
    print(f"✅ 成功提取 {len(words)} 个单词")

    # 输出
    output_file = args.output or f'{args.type}_extracted.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(words, f, indent=2, ensure_ascii=False)
    print(f"已保存到: {output_file}")

    # 预览前5个
    print("\n预览（前5个）:")
    for i, (k, v) in enumerate(words.items()):
        if i >= 5:
            break
        print(f"  {v['word']} {v['phonetic']} {v['pos']}{v['meaning']}")


if __name__ == '__main__':
    main()
