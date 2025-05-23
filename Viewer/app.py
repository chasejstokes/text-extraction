from flask import Flask, jsonify, send_from_directory
import os
import glob

app = Flask(__name__)

# Serve the main HTML page
@app.route('/')
def home():
    return send_from_directory('.', 'chart_display.html')

# Endpoint to list all chart files

@app.route('/list_charts')
def list_charts():
    try:
        # Get all PNG files from ChartImages directory
        chart_files = glob.glob(os.path.join('ChartImages', '*.png'))
        # Extract just the chart names without extension
        chart_names = [os.path.splitext(os.path.basename(f))[0] for f in chart_files]
        # Sort numerically
        
        chart_names.sort(key=str)

        return jsonify({'files': chart_names})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Serve files from ChartImages directory
@app.route('/ChartImages/<path:filename>')
def serve_image(filename):
    return send_from_directory('ChartImages', filename)

# Serve files from ChartData directory
@app.route('/ChartData/<path:filename>')
def serve_csv(filename):
    return send_from_directory('ChartData', filename)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
