from difflib import SequenceMatcher

def highlight_diff(text_box1, text_box2):
    """
    두 텍스트 박스의 내용을 비교하고 변경된 부분을 하이라이트합니다 (문자 단위 비교).
    """
    text1 = text_box1.get("1.0", "end-1c")  # 왼쪽 텍스트
    text2 = text_box2.get("1.0", "end-1c")  # 오른쪽 텍스트

    # 기존 하이라이트 제거
    text_box1.tag_remove("highlight", "1.0", "end")
    text_box2.tag_remove("highlight", "1.0", "end")

    # 문자 단위 비교
    matcher = SequenceMatcher(None, text1, text2)
    opcodes = matcher.get_opcodes()

    for tag, i1, i2, j1, j2 in opcodes:
        if tag == "delete":
            start_idx = f"1.0 + {i1} chars"
            end_idx = f"1.0 + {i2} chars"
            text_box1.tag_add("highlight", start_idx, end_idx)
        elif tag == "insert":
            start_idx = f"1.0 + {j1} chars"
            end_idx = f"1.0 + {j2} chars"
            text_box2.tag_add("highlight", start_idx, end_idx)
        elif tag == "replace":
            # 하이라이트 변경된 부분 (왼쪽 텍스트)
            start_idx1 = f"1.0 + {i1} chars"
            end_idx1 = f"1.0 + {i2} chars"
            text_box1.tag_add("highlight", start_idx1, end_idx1)

            # 하이라이트 변경된 부분 (오른쪽 텍스트)
            start_idx2 = f"1.0 + {j1} chars"
            end_idx2 = f"1.0 + {j2} chars"
            text_box2.tag_add("highlight", start_idx2, end_idx2)
