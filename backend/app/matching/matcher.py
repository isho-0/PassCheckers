# app/matching/matcher.py

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


def map_yolo_name(yolo_name: str) -> str:
    """
    YOLO 결과명을 매핑 딕셔너리에서 DB 객체명으로 변환.
    없으면 원래 이름 그대로 반환.
    """
    mapped = YOLO_TO_DB_MAP.get(yolo_name)
    if mapped:
        return mapped[0]  # 리스트에서 첫 번째 요소 사용
    return yolo_name
