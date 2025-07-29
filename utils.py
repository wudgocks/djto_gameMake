# 충돌 감지 함수 (is_colliding) 등 유틸리티 함수

# utils.py
def is_colliding(obj1_x, obj1_y, obj1_w, obj1_h, obj2_x, obj2_y, obj2_w, obj2_h):
    return (obj1_x < obj2_x + obj2_w and
            obj1_x + obj1_w > obj2_x and
            obj1_y < obj2_y + obj2_h and
            obj1_y + obj1_h > obj2_y)