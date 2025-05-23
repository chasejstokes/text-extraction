import google.generativeai as genai
import pathlib
import os
import csv
import json
from typing import Dict, List

def configure_gemini(api_key: str) -> None:
    """Configure the Gemini API with the provided key."""
    genai.configure(api_key=api_key)

def process_image(model: genai.GenerativeModel, image_path: pathlib.Path) -> List[Dict]:
    """
    Process a single image and extract text information using Gemini.
    Returns the parsed data as a list of dictionaries.
    """
    prompt = """
    Analyze this chart and provide the following information in a structured format:
    1. All text elements present in the chart
    2. The type of each text element (title, caption, axis_label, legend, annotation, etc.)
    3. The coordinates of each text element if possible (x,y position)
    4. The type of chart
    5. The semantic level of each annotation, based on the following definitions:
        L1: Encoded elements (e.g., chart topic, axis descriptions)
        L2: Statistical/relational details (e.g., comparisons, extrema)
        L3: Perceptual/cognitive aspects (e.g., patterns, trends)
        L4: External context (e.g., events affecting the data shown)

    Format the response as a JSON array with objects containing:
    {
        "text": "actual text content",
        "type": "type of text element",
        "chart_type": "type of chart",
        "semantic_level": "semantic level of text element"
    }
    
    """
    
    try:
        image = genai.upload_file(image_path)
        response = model.generate_content([image, prompt])
        
        # Parse the JSON response
        cleaned_response = response.text.strip().replace('```json', '').replace('```', '')
        data = json.loads(cleaned_response)
        return data
    except Exception as e:
        print(f"Error processing {image_path.name}: {str(e)}")
        return []

def save_individual_csv(data: List[Dict], output_dir: pathlib.Path, filename: str) -> None:
    """Save text information for a single image to its own CSV file."""
    # Create the output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Define the CSV path for this image
    csv_path = output_dir / f"{filename.replace('.png', '')}.csv"
    
    fieldnames = ['textContents', 'textType', 'semantic_level']
    
    try:
        with open(csv_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            # Write data for each text element
            for item in data:
                writer.writerow({
                    'textContents': item.get('text', ''),
                    'textType': item.get('type', ''),
                    
                    'semantic_level': item.get('semantic_level', '')
                })
        print(f"Created individual CSV for {filename}")
    except Exception as e:
        print(f"Error saving individual CSV for {filename}: {str(e)}")

def update_summary_csv(data: List[Dict], output_dir: pathlib.Path, filename: str) -> None:
    """Update the summary CSV with chart type information."""
    summary_path = output_dir / "chart_types_summary.csv"
    fieldnames = ['filename', 'chart_type']
    
    # Get the chart type from the first item (assuming all items have the same chart_type)
    chart_type = data[0].get('chart_type', '') if data else ''
    
    try:
        # Check if file exists to determine if we need to write headers
        file_exists = summary_path.exists()
        
        with open(summary_path, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow({
                'filename': filename,
                'chart_type': chart_type
            })
        print(f"Updated summary CSV with {filename}")
    except Exception as e:
        print(f"Error updating summary CSV: {str(e)}")

def main():
    # Configuration
    GOOGLE_API_KEY = "AIzaSyDj2KnSUMkhDHXyNt2zDSCHKRBvyZrwqHQ"
    BASE_DIR = pathlib.Path(__file__).parent
    IMAGE_DIR = BASE_DIR / "Couple of Chart QA Images"
    OUTPUT_DIR = BASE_DIR / "ChartTextData"
    
    # Initialize Gemini
    configure_gemini(GOOGLE_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    # Create output directory if it doesn't exist
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Process each image in the directory
    for image_file in IMAGE_DIR.glob("*.png"):
        print(f"\nProcessing {image_file.name}...")
        data = process_image(model, image_file)
        
        if data:
            # Save individual CSV for this image's text data
            save_individual_csv(data, OUTPUT_DIR, image_file.name)
            
            # Update the summary CSV with chart type information
            update_summary_csv(data, OUTPUT_DIR, image_file.name)
            
            print(f"Successfully processed {image_file.name}")
        else:
            print(f"No data extracted from {image_file.name}")

if __name__ == "__main__":
    main()