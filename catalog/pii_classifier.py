class PIIClassifier:
    PII_KEYWORDS = [
        "ssn", "aadhaar", "passport", "credit_card", "phone", "email", "address", "driver_license", "pan"]
    FINANCIAL_KEYWORDS = ["credit", "debit", "account", "bank", "ifsc", "upi", "balance"]

    def classify_column(self, column_name: str)-> str:
        name = column_name.lower()
        for kw in self.PII_KEYWORDS:
            if kw in name:
                return "PII"
        for kw in self.FINANCIAL_KEYWORDS:
            if kw in name:
                return "Financial"
        
        return "PUBLIC"

    def classify_columns(self, columns: list)-> dict:
        return {
            column: self.classify_column(column) for column in columns }