import os
from anthropic import Anthropic
from typing import Optional

class MoneyAI:
    def __init__(self):
        self.client = Anthropic(api_key = os.getenv("ANTHROPIC_API_KEY"))

    def categorize_transaction(self, description: str, amount: float, transaction_type: str) -> dict:

        categories = [
            "อาหาร", "ที่อยู่อาศัย", "การเดินทาง", "ความบันเทิง",
            "สุขภาพ", "การศึกษา", "เสื้อผ้า", "ยานพาหนะ",
            "เงินเดือน", "เงินลงทุน", "ของใช้ในบ้าน", "อื่นๆ"
        ]

        prompt = f"""
        จัดหมวดหมู่รายการการเงินต่อไปนี้:

        รายละเอียด: {description}
        จำนวนเงิน: {amount}
        ประเภท: {transaction_type}

        เลือกหมวดหมู่ที่เหมาะสมจากรายการนี้: {', '.join(categories)}

        ตอบเฉพาะชื่อหมวดหมู่เท่านั้น (ไม่ต้องอธิบาย)
        """

        try:
            response = self.client.messages.create(
                model = "claude-3-5-haiku-20241022",
                max_tokens = 50,
                messages = [{"role": "user", "content": prompt}]
            )

            category = response.content[0].text.strip()

            return {
                "category": category,
                "confidence": 0.85,
                "is_ai_categorized": True
            }
        
        except Exception as e:
            return {
                "category": "อื่นๆ",
                "confidence": 0.0,
                "is_ai_categorized": False,
                "error": str(e)
            }