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
    Analyze the image of one or more charts in detail and provide the following information in a CSV format:

    Columns to include: chartType,rows,columns,

    Instructions:
    - chartType: the type of chart
    - rows: the range of rows (0 indexed) that the chart takes up on the image. This should be of the form startRow-endRow.
    - columns: the range of columns (0 indexed) that the chart takes up on the image. This should be of the form startColumn-endColumn.
   
    To assign rows and columns, pretend there is a grid overlay over the image, where a new row starts at the topmost edge of each chart, and a new column starts at the leftmost edge of each chart.

    If there is only one chart in the image, the rows of the chart should be 0-0 and the columns of the chart should be 0-0. Examples with the title SINGLE_CHART_EXAMPLE_ followed by the image name are examples of images containing only one chart.
   
    {single_chart_examples}

    If there are multiple charts that are stacked on top of eachother, each columns value should be 0-0, but the rows value should start at 0-0 for the topmost chart, and increase by one to 1-1, then 2-2, for each chart present. Examples with the title COLUMN_EXAMPLE_ followed by the image name demonstrate what to do if there is a vertical line (a column) of charts.

    {column_examples}

    If there are multiple charts that are arranged in a horizontal line, each rows value should be 0-0, but the columns value should start at 0-0 for the leftmost chart, and increase by one to 1-1, then 2-2, for each chart present. Examples with the title ROW_EXAMPLE_ followed by the image name demonstrate what to do if there is a horizontal line (a row) of charts.

    {row_examples}

    If there are multiple rows and columns of charts, but their edges are aligned, there should be one chart per grid point. Examples with the title ALIGNED_GRID_EXAMPLE_ followed by the image name demonstrate how to handle cases where the edges of the graphs are aligned.
    
    {aligned_grid_examples}

    If the edges of the charts don't align, there may be some charts who occupy either multiple rows or multiple columns. Always start a new row when you see the topmost edge of a chart, and a new column when you see the leftmost edge of a chart. Examples with the title UNALIGNED_GRID_EXAMPLE_ followed by the image name demonstrate what to do if the edges of the charts don't line up.

    {unaligned_grid_examples}


    Now, analyze this chart: 
    [target_image]
    
    Provide the output CSV matching the format of the previous examples but using the data from the image itself.
    """
    
    try:
        # Upload images with mime type specification
        target_image = genai.upload_file(target_image_path, mime_type="image/png")
       
        # Generate content
        response = model.generate_content([
            *single_chart_example_files,
            *column_example_files,
            *row_example_files,
            *aligned_grid_example_files,
            *unaligned_grid_example_files,
            target_image, 
            prompt
        ])
        
        # Clean the response, removing any code block markers
        cleaned_response = response.text.strip().replace('```csv', '').replace('```', '')

        return cleaned_response
    except Exception as e:
        print(f"Error processing {target_image_path.name}: {str(e)}")
        return ""

def save_individual_csv(data: str, output_dir: pathlib.Path, filename: str) -> None:
    """Save text information for a single image to its own CSV file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    csv_path = output_dir / f"{filename.replace('.png', '')}.csv"
    
    try:
        # Create a CSV reader object from the string data
        csv_reader = csv.reader(StringIO(data))

        # Save to a CSV file
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            # Write all rows from the response
            for row in csv_reader:
                csv_writer.writerow(row)

        print(f"Saved CSV for {filename} to {csv_path}")

    except Exception as e:
        print(f"Error saving individual CSV for {filename}: {str(e)}")
def main():
    # Configuration
    GOOGLE_API_KEY = "AIzaSyDj2KnSUMkhDHXyNt2zDSCHKRBvyZrwqHQ"
    BASE_DIR = pathlib.Path(__file__).parent
    IMAGE_DIR = BASE_DIR / "test_images"
    OUTPUT_DIR = BASE_DIR / "result_csvs"
    
    # Initialize Gemini
    configure_gemini(GOOGLE_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash-8b")
    
    # Create output directory if it doesn't exist
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
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
            # Save individual CSV for this image's text data
            save_individual_csv(data, OUTPUT_DIR, image_file.name)
            
            print(f"Successfully processed {image_file.name}")
        else:
            print(f"No data extracted from {image_file.name}")

if __name__ == "__main__":
    main()