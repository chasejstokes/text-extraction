ALL CREDIT TO THIS WORK GOES TO SYLVIE VENUTO

# Graph Analysis Notes

This document summarizes insights and issues encountered when analyzing graph data. These findings cover two main attempts with different CSV configurations to evaluate the consistency and accuracy of (x, y) coordinates and labels.

## First Attempt

- **Data Format**: Created separate CSV files for each graph.
- **Observations**:
  - **X Coordinates**: All points initially show `0` and then `900`, even though the bars end at different points visually.
  - **Y Coordinates**: Consistent relative to each other.
- **Next Steps**:
  - Consider adding specific categories for each part of the graph, or determine if this is unnecessary.

## Second Attempt

- **Data Format**: Separate CSV for each graph.
- **Improvements**:
  - **Graph Type Detection**: The correct graph type was identified.
  - **(x, y) Coordinates**: Generated coordinates for points at `(427, 277)`.
  - **Coordinate Consistency**: Values are mostly correct relative to each other (points with the same x or y value appear consistent), but the pixel-to-coordinate ratio is still off. 
    - Expected Ratio: x < y.
    - Observed Ratio: x > y.
- **Specific Issues for Graph 427**:
  - **Y-Axis Label**: No clear y-axis label; only numbers appear, leading to label errors.
  - **Annotation vs. Axis Labels**: 
    - First two points (`50` and `44`) are classified as `axis_label`, while others are labeled as `annotations`, though they should follow the same convention.

## Future Considerations

- Revisit how labels and annotations are being classified.
- Investigate methods to calibrate pixel-to-coordinate ratio for accurate visualization.
- Review whether consistent categories for graph elements would improve accuracy.

## Semantic Levels
Also added a check for the semantic levels from https://chasejstokes.github.io/pdfs/Striking%20a%20Balance.pdf
- not consistent on what qualifies as different levels (caption at the bottom of graph is L4 for 166, but is L1 for 277)

## To use HTML Viewer with notes: 
  1. run python app.py
  2. access at http://localhost:8000

## To use simple HTML Viewer:
  1. open Viewer/simpel_chart_display.html in web browser
  2. choose images and data from the same dataset as input, and upload to page
