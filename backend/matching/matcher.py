# backend/matching/matcher.py

from fuzzywuzzy import fuzz

# YOLO 객체명 → DB(규정) 객체명 매핑 딕셔너리
YOLO_TO_DB_MAP = {
    "airpod": ["Airpod"],
    "anseongtangmyeon": ["Ramen"],
    "axe": ["Axes and Hatchets"],
    "bag": ["General Bag"],
    "bottle": ["Bottle"],
    "buldalg": ["Ramen"],
    "camera": ["Digital Cameras"],
    "casual-shoes": ["Belts, Clothes and Shoes"],
    "cigga": ["Cigarettes"],
    "cup-buldalg": ["Ramen"],
    "cup-shin-black": ["Ramen"],
    "cup-shin-norm": ["Ramen"],
    "curling-iron": ["Curling Iron"],
    "disposable_razor": ["Disposable Razor"],
    "drone": ["Drones, Unmanned Aircraft Systems (UAS)"],
    "electric_shaver": ["Electric Razors"],
    "fork": ["Fork"],
    "gin-ramen": ["Ramen"],
    "glasses": ["Glasses"],
    "gochujang": ["Sauce (Fermented Paste)"],
    "hair-dryer": ["Hair Dryers"],
    "hammer": ["Hammers"],
    "kimchi pack": ["Kimchi"],
    "knife": ["Knives"],
    "laptop": ["Laptops"],
    "lighter": ["Lighter (Fluid)"],
    "nail_clipper": ["Nail Clippers"],
    "paldobibimmyeon": ["Ramen"],
    "passport": ["Passport"],
    "pen": ["Pen"],
    "portable-charger": ["Power Banks"],
    "portable umbrella": ["Umbrellas"],
    "samjang": ["Sauce (Fermented Paste)"],
    "scissors": ["Scissors"],
    "shampoo": ["Shampoo"],
    "shoes": ["Belts, Clothes and Shoes"],
    "sinlamyeon": ["Ramen"],
    "soybean": ["Sauce (Fermented Paste)"],
    "spray": ["Hair Spray"],
    "suitcase": ["General Bag"],
    "toothbrush": ["Toothbrush"],
    "touch_panel": ["Tablets"],
    "tube": ["Tube (Liquid)"],
    "umbrella": ["Umbrellas"],
    "wallet": ["Belts, Clothes and Shoes"],
    "watch": ["Clock"],
    "weapon": ["Knives"],
}


def map_yolo_name(yolo_name: str, item_list: list = None, threshold: int = 80):
    """
    YOLO 모델이 탐지한 영어 이름을 기반으로 가장 유사한 DB 아이템 이름을 찾습니다.
    먼저 정확한 매핑을 시도하고, 없으면 fuzzy matching을 사용합니다.
    """
    # 1. 정확한 매핑 시도
    mapped = YOLO_TO_DB_MAP.get(yolo_name.lower())
    if mapped:
        return mapped[0]  # 리스트에서 첫 번째 요소 사용
    
    # 2. item_list가 제공된 경우 fuzzy matching 사용
    if item_list:
        best_match = None
        highest_score = -1

        for item in item_list:
            # item_name_EN 필드가 없으므로 item_name_ko와 비교
            score = fuzz.ratio(yolo_name.lower(), item['item_name'].lower())
            if score > highest_score:
                highest_score = score
                best_match = item['item_name']
        
        if highest_score >= threshold:
            return best_match
    
    # 3. 매칭되는 것이 없으면 YOLO 이름을 그대로 반환
    return yolo_name
