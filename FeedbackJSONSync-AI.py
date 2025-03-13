import json
import csv
import re
import datetime
from typing import Dict, List, Union, Tuple, Optional

class FeedbackJSONSyncAI:
    """
    A system designed to translate and synchronize multilingual customer feedback
    from noisy social media data into structured JSON for sentiment analysis and actionable insights.
    """
    
    def __init__(self):
        self.positive_words = ["good", "excellent", "great", "happy", "love", "positive", "satisfied"]
        self.negative_words = ["bad", "poor", "terrible", "unhappy", "hate", "negative", "dissatisfied"]
        self.required_fields = ["feedback_id", "language", "feedback_text", "timestamp"]
        self.optional_fields = ["sentiment_score"]
        
    def validate_data(self, data: List[Dict]) -> Tuple[bool, List[str]]:
        """
        Validates the input data against required fields and data types.
        
        Args:
            data: List of feedback records
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        is_valid = True
        error_messages = []
        
        for idx, record in enumerate(data):
            row_num = idx + 1
            
            # Check for missing required fields
            missing_fields = [field for field in self.required_fields if field not in record or not record[field]]
            if missing_fields:
                is_valid = False
                error_messages.append(f"ERROR: Missing required field(s): {', '.join(missing_fields)} in row {row_num}.")
            
            # Check sentiment_score if provided
            if "sentiment_score" in record and record["sentiment_score"] is not None:
                try:
                    score = float(record["sentiment_score"])
                    if score < -1 or score > 1:
                        is_valid = False
                        error_messages.append(f"ERROR: Invalid value for the field(s): sentiment_score in row {row_num}. Score must be between -1 and 1.")
                except (ValueError, TypeError):
                    is_valid = False
                    error_messages.append(f"ERROR: Invalid data type for the field(s): sentiment_score in row {row_num}. Please ensure correct data types.")
            
            # Check language format (ISO 639-1)
            if "language" in record and record["language"]:
                if not re.match(r'^[a-z]{2}$', record["language"]):
                    is_valid = False
                    error_messages.append(f"ERROR: Invalid value for the field(s): language in row {row_num}. Language must be in ISO 639-1 format.")
            
            # Check timestamp format (ISO 8601)
            if "timestamp" in record and record["timestamp"]:
                try:
                    datetime.datetime.fromisoformat(record["timestamp"].replace('Z', '+00:00'))
                except (ValueError, TypeError):
                    is_valid = False
                    error_messages.append(f"ERROR: Invalid value for the field(s): timestamp in row {row_num}. Timestamp must be in ISO 8601 format.")
        
        return is_valid, error_messages
    
    def generate_validation_report(self, data: List[Dict]) -> str:
        """
        Generates a validation report for the data.
        
        Args:
            data: List of feedback records
            
        Returns:
            Markdown formatted validation report
        """
        is_valid, error_messages = self.validate_data(data)
        
        # Check field presence across all records
        field_status = {
            "feedback_id": "present" if all("feedback_id" in record and record["feedback_id"] for record in data) else "missing",
            "language": "valid" if all("language" in record and re.match(r'^[a-z]{2}$', record["language"]) for record in data if "language" in record) else "invalid",
            "feedback_text": "valid" if all("feedback_text" in record for record in data) else "invalid",
            "timestamp": "valid" if all("timestamp" in record and record["timestamp"] for record in data) else "invalid",
            "sentiment_score": "valid"
        }
        
        # Check sentiment_score validity if provided
        for record in data:
            if "sentiment_score" in record and record["sentiment_score"] is not None:
                try:
                    score = float(record["sentiment_score"])
                    if score < -1 or score > 1:
                        field_status["sentiment_score"] = "invalid"
                        break
                except (ValueError, TypeError):
                    field_status["sentiment_score"] = "invalid"
                    break
        
        report = f"""# Customer Feedback Data Validation Report:
- Total Feedback Records: {len(data)}
## Required Fields Check:
  feedback_id: {field_status["feedback_id"]}
  language: {field_status["language"]}
  feedback_text: {field_status["feedback_text"]}
  timestamp: {field_status["timestamp"]}
  sentiment_score: {field_status["sentiment_score"]}

## Validation Status:
"""
        
        if is_valid:
            report += "Data validation is successful! Would you like to proceed with the analysis or provide another dataset?"
        else:
            report += "\n".join(error_messages)
        
        return report
    
    def translate_feedback(self, text: str, language: str) -> str:
        """
        Simulates translation of feedback text to English.
        In a real implementation, this would call an external translation API.
        
        Args:
            text: The feedback text to translate
            language: The language code of the text
            
        Returns:
            Translated text (or original if language is English)
        """
        if language == "en":
            return text
        
        # In a real implementation, call a translation API here
        # For this simulation, we'll just add a note
        return f"[Translated from {language}] {text}"
    
    def synchronize_timestamp(self, timestamp: str) -> str:
        """
        Ensures the timestamp is in UTC timezone.
        
        Args:
            timestamp: The timestamp in ISO 8601 format
            
        Returns:
            Synchronized timestamp in ISO 8601 format
        """
        # Parse timestamp and ensure it's in UTC
        dt = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.astimezone(datetime.timezone.utc).isoformat()
    
    def calculate_sentiment_score(self, text: str) -> Tuple[float, int, int, int]:
        """
        Calculates sentiment score based on positive and negative word counts.
        
        Args:
            text: The feedback text
            
        Returns:
            Tuple of (sentiment_score, positive_count, negative_count, total_words)
        """
        # Convert to lowercase for case-insensitive matching
        lower_text = text.lower()
        
        # Count positive and negative words
        positive_count = sum(1 for word in self.positive_words if word in lower_text.split())
        negative_count = sum(1 for word in self.negative_words if word in lower_text.split())
        
        # Count total words
        total_words = len(lower_text.split())
        
        # Calculate sentiment score
        if total_words > 0:
            sentiment_score = (positive_count - negative_count) / total_words
        else:
            sentiment_score = 0.0  # Empty feedback text
        
        # Round to 2 decimal places
        sentiment_score = round(sentiment_score, 2)
        
        return sentiment_score, positive_count, negative_count, total_words
    
    def process_feedback(self, data: List[Dict]) -> List[Dict]:
        """
        Processes each feedback record with translation, sentiment analysis, and timestamp synchronization.
        
        Args:
            data: List of feedback records
            
        Returns:
            Processed feedback records
        """
        processed_data = []
        
        for record in data:
            # Create a new record to avoid modifying the original
            processed_record = {
                "feedback_id": record["feedback_id"],
                "language": record["language"],
                "feedback_text": self.translate_feedback(record["feedback_text"], record["language"]),
                "timestamp": self.synchronize_timestamp(record["timestamp"])
            }
            
            # Calculate sentiment score if not provided
            if "sentiment_score" not in record or record["sentiment_score"] is None:
                sentiment_score, _, _, _ = self.calculate_sentiment_score(processed_record["feedback_text"])
                processed_record["sentiment_score"] = sentiment_score
            else:
                processed_record["sentiment_score"] = float(record["sentiment_score"])
            
            processed_data.append(processed_record)
        
        return processed_data
    
    def generate_detailed_report(self, data: List[Dict], processed_data: List[Dict]) -> str:
        """
        Generates a detailed report with processing steps for each feedback.
        
        Args:
            data: Original feedback records
            processed_data: Processed feedback records
            
        Returns:
            Markdown formatted detailed report
        """
        report = f"""# Customer Feedback JSON Summary

**Total Feedback Records Evaluated:** {len(data)}

---

"""
        
        for idx, (original, processed) in enumerate(zip(data, processed_data)):
            # Calculate sentiment analysis details
            sentiment_score, positive_count, negative_count, total_words = self.calculate_sentiment_score(processed["feedback_text"])
            
            report += f"""## Detailed Analysis per Feedback

### Feedback: {original["feedback_id"]}

#### Input Data:
- **Language:** {original["language"]}
- **Feedback Text:** {original["feedback_text"]}
- **Sentiment Score (if provided):** {original.get("sentiment_score", "Not provided")}
- **Timestamp:** {original["timestamp"]}

---

## Processing Steps

### 1. Translation Check
- **IF** language is not "en", **THEN** the translated text is: {processed["feedback_text"]}
- **ELSE**: Use the original text.

### 2. Sentiment Analysis Calculation
- **Count of Positive Words (P):** {positive_count}
- **Count of Negative Words (N):** {negative_count}
- **Total Words:** {total_words}
- **Calculation:**  
  $$ \\text{{sentiment\\_score}} = \\frac{{({positive_count} - {negative_count})}}{{total\\_words}} = \\frac{{{positive_count - negative_count}}}{{{total_words}}} = {sentiment_score} $$
- **Final Sentiment Score:** {processed["sentiment_score"]}

### 3. Timestamp Synchronization
- **Synchronized Timestamp:** {processed["timestamp"]}

---

"""
        
        # Add structured JSON output
        report += """## Structured JSON OUTPUT

```json
"""
        
        json_output = {
            "feedbacks": processed_data
        }
        report += json.dumps(json_output, indent=2)
        report += "\n```"
        
        return report
    
    def parse_csv(self, csv_data: str) -> List[Dict]:
        """
        Parses CSV formatted data into a list of records.
        
        Args:
            csv_data: CSV formatted string
            
        Returns:
            List of feedback records
        """
        records = []
        try:
            csv_reader = csv.DictReader(csv_data.strip().split('\n'))
            for row in csv_reader:
                # Convert empty string sentiment_score to None
                if "sentiment_score" in row and (not row["sentiment_score"] or row["sentiment_score"].lower() == "null"):
                    row["sentiment_score"] = None
                elif "sentiment_score" in row and row["sentiment_score"]:
                    row["sentiment_score"] = float(row["sentiment_score"])
                
                records.append(row)
            return records
        except Exception as e:
            raise ValueError(f"ERROR: Invalid CSV format. {str(e)}")
    
    def parse_json(self, json_data: str) -> List[Dict]:
        """
        Parses JSON formatted data into a list of records.
        
        Args:
            json_data: JSON formatted string
            
        Returns:
            List of feedback records
        """
        try:
            data = json.loads(json_data)
            if "feedbacks" in data and isinstance(data["feedbacks"], list):
                records = data["feedbacks"]
                
                # Process sentiment_score field
                for record in records:
                    if "sentiment_score" in record and (record["sentiment_score"] is None or record["sentiment_score"] == "null"):
                        record["sentiment_score"] = None
                    elif "sentiment_score" in record and record["sentiment_score"] != "":
                        record["sentiment_score"] = float(record["sentiment_score"])
                
                return records
            else:
                raise ValueError("ERROR: Invalid JSON structure. Expected 'feedbacks' array.")
        except json.JSONDecodeError:
            raise ValueError("ERROR: Invalid JSON format.")
    
    def process_data(self, data_input: str) -> str:
        """
        Processes the input data and generates a report.
        
        Args:
            data_input: Input data in CSV or JSON format
            
        Returns:
            Markdown formatted report
        """
        # Try to parse as JSON first, then CSV
        try:
            if data_input.strip().startswith('{'):
                data = self.parse_json(data_input)
            else:
                data = self.parse_csv(data_input)
        except ValueError as e:
            return str(e)
        
        # Validate data
        is_valid, error_messages = self.validate_data(data)
        if not is_valid:
            return self.generate_validation_report(data)
        
        # Process the valid data
        processed_data = self.process_feedback(data)
        
        # Generate detailed report
        return self.generate_detailed_report(data, processed_data)

# Example usage
def main():
    processor = FeedbackJSONSyncAI()
    # Example CSV input
    csv_input = """feedback_id,language,feedback_text,sentiment_score,timestamp
FB601,en,The new interface is good and intuitive,null,2023-03-21T08:00:00Z
FB602,es,La aplicación es excelente y muy útil,null,2023-03-21T08:10:00Z
FB603,fr,Le service client est très attentionné,null,2023-03-21T08:20:00Z
FB604,de,Die Funktionen sind schlecht und verwirrend,null,2023-03-21T08:30:00Z
FB605,en,I love the fast response times,null,2023-03-21T08:40:00Z
FB606,es,La calidad es buena pero el precio es alto,null,2023-03-21T08:50:00Z
FB607,fr,Je suis satisfait de la performance,null,2023-03-21T09:00:00Z
FB608,en,The update did not meet my expectations,null,2023-03-21T09:10:00Z
FB609,de,Ausgezeichnete Unterstützung und schnelle Hilfe,null,2023-03-21T09:20:00Z
FB610,en,Not impressed with the overall functionality,null,2023-03-21T09:30:00Z"""
    
    result = processor.process_data(csv_input)
    print(result)
    



if __name__ == "__main__":
    main()