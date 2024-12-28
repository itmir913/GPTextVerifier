from difflib import SequenceMatcher

def highlight_diff(text_box1, text_box2):
    content1 = text_box1.get("1.0", "end-1c")
    content2 = text_box2.get("1.0", "end-1c")

    # 기존 하이라이트 제거
    text_box1.tag_remove("highlight", "1.0", "end")
    text_box2.tag_remove("highlight", "1.0", "end")

    # 태그 설정
    text_box1.tag_configure("highlight", background="lightcoral")
    text_box2.tag_configure("highlight", background="lightgreen")

    # 문자 단위 비교
    matcher = SequenceMatcher(None, content1, content2)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "replace" or tag == "delete":
            start_idx = f"1.{i1}"
            end_idx = f"1.{i2}"
            text_box1.tag_add("highlight", start_idx, end_idx)
        if tag == "replace" or tag == "insert":
            start_idx = f"1.{j1}"
            end_idx = f"1.{j2}"
            text_box2.tag_add("highlight", start_idx, end_idx)
