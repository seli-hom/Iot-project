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
                SELECT p.product_id, p.product_name, p.product_price, p.product_company, r.rfid_tag
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

def finalize_checkout(self, cart_items):
    """
    Call this when the 'Pay' button is pressed and successful.
    cart_items should be a list of tags scanned during the session.
    """
    try:
        storeDb = db.getDB()
        for item in cart_items:
            # item['rfid_tag'] is the hex code
            tag_hex = item.get('rfid_tag')
            
            # Remove the specific physical tag from the database
            storeDb.execute('DELETE FROM product_rfid WHERE rfid_tag = ?', (tag_hex,))
            
            # Optional: Log the sale in a separate 'sales' table if you have one
            print(f"CLEANUP: Tag {tag_hex} removed from inventory (Sold).")
            
        storeDb.commit()
        storeDb.close()
        return True
    except Exception as e:
        print(f"CHECKOUT ERROR: Could not clear tags: {e}")
        return False
