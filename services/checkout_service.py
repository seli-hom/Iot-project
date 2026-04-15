# services/checkout_service.py

class CheckoutManager:
    def __init__(self, db_module):
        self.db = db_module

    # --- THE MISSING ATTRIBUTE ---
    def process_simultaneous_scan(self, scanned_tags):
        """
        Takes a list of RFID hex strings and returns a priced receipt.
        """
        if not scanned_tags:
            return None
        
        # Remove duplicates from the physical scan burst
        unique_tags = list(set(scanned_tags))
        conn = self.db.getDB()
        
        try:
            placeholders = ', '.join(['?'] * len(unique_tags))
            # Joining products with product_rfid to get names/prices
            query = f'''
                SELECT p.product_name, p.product_price, p.product_company
                FROM products p
                JOIN product_rfid r ON p.product_id = r.product_id
                WHERE LOWER(r.rfid_tag) IN ({placeholders})
            '''
            
            items = conn.execute(query, [t.lower() for t in unique_tags]).fetchall()
            
            # Formatting the data for the frontend/receipt
            product_list = [dict(item) for item in items]
            subtotal = sum(item['product_price'] for item in product_list)
            
            # Quebec Tax Calculation
            gst = round(subtotal * 0.05, 2)
            qst = round(subtotal * 0.09975, 2)
            
            return {
                "items": product_list,
                "subtotal": round(subtotal, 2),
                "gst": gst,
                "qst": qst,
                "total": round(subtotal + gst + qst, 2),
                "item_count": len(product_list),
                "timestamp": "2026-04-06 15:20:57" # Current time for the receipt
            }
        finally:
            conn.close()