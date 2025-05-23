from io import StringIO
import google.generativeai as genai
import pathlib
import os
import csv
import json

BASE_DIR = pathlib.Path(__file__).parent

def configure_gemini(api_key: str) -> None:
    """Configure the Gemini API with the provided key."""
    genai.configure(api_key=api_key)


def create_examples(example_names, example_category):
 # Prepare example content
    example_content = []
    example_files = []
    
    for example_name in example_names:
        #create csv path:
        csvPath = BASE_DIR / "example_csvs" / f"{example_name}.csv"
        # Read CSV content
        with open(csvPath, 'r') as f:
            csv_content = f.read()
        
        # Prepare example block
        example_block = f"""
        <{example_category}_EXAMPLE_{example_name}>
            INPUT: 
            [{example_name}.png]
            
            OUTPUT: 
            {csv_content}
        </{example_category}_EXAMPLE_{example_name}>
        """
        example_content.append(example_block)
        
         #create csv path:
        image_path = BASE_DIR / "example_images" / f"{example_name}.png"
        # Upload files
        example_image = genai.upload_file(image_path, mime_type="image/png")
        example_files.extend([example_image])
    example_content_string = ''.join(example_content)
    return example_content_string, example_files


def process_image(model: genai.GenerativeModel, single_chart_chart_names, column_chart_names, row_chart_names, aligned_grid_chart_names, unaligned_grid_chart_names, target_image_path: pathlib.Path) -> str:
    """
    Process a single image and extract text information using Gemini.
    Returns the parsed data as a CSV string.
    """
    single_chart_examples, single_chart_example_files = create_examples(single_chart_chart_names, "SINGLE_CHART") 
    column_examples, column_example_files = create_examples(column_chart_names, "COLUMN")
    row_examples, row_example_files = create_examples(row_chart_names, "ROW")
    aligned_grid_examples, aligned_grid_example_files = create_examples(aligned_grid_chart_names, "ALIGNED_GRID")
    unaligned_grid_examples, unaligned_grid_example_files = create_examples(unaligned_grid_chart_names, "UNALIGNED_GRID")
    
    prompt = f"""
    Analyze the image of one or more charts and provide the number of charts that are in the image. Do not provide any information other than the integer number of charts in the image.

    [target_image]
    
    """
    
    try:
        # Upload images with mime type specification
        target_image = genai.upload_file(target_image_path, mime_type="image/png")
       
        # Generate content
        response = model.generate_content([
            target_image, 
            prompt
        ])
        
        # Clean the response, removing any code block markers

        return response.text.strip()
    except Exception as e:
        print(f"Error processing {target_image_path.name}: {str(e)}")
        return ""

def save_result(data: str, output_path: pathlib.Path, filename: str) -> None:
    """Save text information for a single image to its own CSV file."""
    
    try:
        # Create a CSV reader object from the string data

        # Save to a CSV file
        with open(output_path, 'a', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow([filename, data])

        print(f"Saved CSV for {filename} to {data}")

    except Exception as e:
        print(f"Error saving data for {filename}: {str(e)}")
def main():
    # Configuration
    GOOGLE_API_KEY = "AIzaSyDj2KnSUMkhDHXyNt2zDSCHKRBvyZrwqHQ"
    BASE_DIR = pathlib.Path(__file__).parent
    IMAGE_DIR = BASE_DIR / "test_images"
    OUTPUT_FILE = BASE_DIR / "chartCounts.csv"
    
    # Initialize Gemini
    configure_gemini(GOOGLE_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash-8b")
    
   
    
    #Create list of examples
    single_chart_chart_names  = [
    "wsj433",
    "wsj431", 
    "wsj419",
    "whoK15_2",
    "whoK12_1", 
    "treasuryB05",
    "treasuryB02", 
    "economist_daily_chart_36",
    "economist_daily_chart_25", 
    "economist_daily_chart_13"
    ]

    unaligned_grid_chart_names = [
    "economist_daily_chart_14",
    "economist_daily_chart_17",
    "economist_daily_chart_24",
    "treasuryA13",
    "treasuryB07",
    "wsj414",
    "wsj430"
    ]
    
    row_chart_names = [
    "economist_daily_chart_20",
    "economist_daily_chart_27",
    "wsj418", 
    "wsj420"
    ]
    column_chart_names = [
   "whoK13_1",
   "wsj426"
    ]

    aligned_grid_chart_names = [
   "economist_daily_chart_30",
   "economist_daily_chart_32",
   "wsj434"]
    


    # Process each image in the directory
    for image_file in IMAGE_DIR.glob("*.png"):
        print(f"\nProcessing {image_file.name}...")
        data = process_image(model, single_chart_chart_names, column_chart_names, row_chart_names, aligned_grid_chart_names, unaligned_grid_chart_names, image_file)
        
        if data:
            save_result(data, OUTPUT_FILE, image_file.name)
            
            print(f"Successfully processed {image_file.name}")
        else:
            print(f"No data extracted from {image_file.name}")

if __name__ == "__main__":
    main()