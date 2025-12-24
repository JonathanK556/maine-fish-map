# Fish Stocking Data Visualization

An interactive map visualization of Maine fish stocking data, built with Folium and Streamlit.

## 🌐 Live Application

**Try the interactive map:** [https://mainecoldwaterfishing.streamlit.app/](https://mainecoldwaterfishing.streamlit.app/)

Explore Maine's fish stocking data with interactive filtering, search, and detailed location information.

## Features

- Interactive map showing fish stocking locations across Maine
- Filter by fish species
- Filter by season (Spring/Fall)
- Search by water body, town, or county
- Filter by minimum quantity of fish
- Detailed popup information for each location

## Files

- `QuickMap.ipynb` - Jupyter notebook version with interactive widgets
- `FishMap.py` - Streamlit web application
- `FishMap_2024.html` - Static HTML version of the map
- `df_updated.csv` - Main dataset with fish stocking information

## Deployment Options

### Option 1: Streamlit Cloud (✅ LIVE!)

**🌐 Live App:** [https://mainecoldwaterfishing.streamlit.app/](https://mainecoldwaterfishing.streamlit.app/)

1. **Prepare your repository:**
   - Push your code to GitHub (make sure all files are included)
   - Ensure `requirements.txt` is in the root directory

2. **Deploy to Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub account
   - Select your repository
   - Set the main file path to `FishMap.py`
   - Click "Deploy"

3. **Your app will be available at:** `https://your-app-name.streamlit.app`

### Option 2: Local Streamlit Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Streamlit app:**
   ```bash
   streamlit run FishMap.py
   ```

3. **Access the app:** Open your browser to `http://localhost:8501`

### Option 3: Static HTML Deployment

The `FishMap_2024.html` file can be deployed to any web hosting service:

1. **GitHub Pages:**
   - Create a repository on GitHub
   - Upload the HTML file
   - Enable GitHub Pages in repository settings
   - Access at `https://yourusername.github.io/repository-name/FishMap_2024.html`

2. **Netlify:**
   - Go to [netlify.com](https://netlify.com)
   - Drag and drop the HTML file
   - Get a custom URL

3. **Other hosting services:** Upload the HTML file to any web hosting provider

### Option 4: Docker Deployment (Production Ready!)

**Complete Docker setup is included!** See `DOCKER_DEPLOYMENT.md` for full instructions.

**Quick start:**
```bash
# Using Docker Compose (Recommended)
docker-compose up -d

# Or using Docker directly
docker build -t fish-stocking-map .
docker run -p 8501:8501 fish-stocking-map
```

**Features:**
- ✅ Production-ready configuration
- ✅ Nginx reverse proxy
- ✅ Health checks
- ✅ Security optimizations
- ✅ Cloud deployment ready

### Option 5: Jupyter Notebook with Binder

1. **Create a `binder` directory with `postBuild` file:**
   ```bash
   mkdir binder
   echo "pip install -r requirements.txt" > binder/postBuild
   ```

2. **Push to GitHub and create Binder link:**
   - Go to [mybinder.org](https://mybinder.org)
   - Enter your GitHub repository URL
   - Click "launch"

## Data Requirements

Make sure you have the following files in your project directory:
- `df_updated.csv` - Contains the fish stocking data with columns:
  - WATER, TOWN, COUNTY - Location information
  - SPECIES - Fish species
  - QTY - Quantity of fish
  - SIZE (inch) - Fish size
  - DATE - Stocking date
  - X_coord, Y_coord - Coordinates for mapping

## Customization

### Changing the Map Center
Edit the `map_center` variable in your code:
```python
map_center = [latitude, longitude]  # Your desired center point
```

### Adding More Filters
You can add additional filters by modifying the widget creation and update_map function.

### Styling
- Modify marker colors in the `folium.Marker` call
- Change popup styling in the `popup_text` HTML
- Adjust map size in `st_folium(width=800, height=600)`

## Troubleshooting

### Common Issues:

1. **Map not displaying:** Ensure all dependencies are installed and CSV file exists
2. **Slow loading:** Consider data preprocessing or pagination for large datasets
3. **Missing markers:** Check that coordinates are valid and data is properly filtered

### Performance Tips:

- Preprocess data to reduce computation during filtering
- Use caching for expensive operations in Streamlit
- Consider data aggregation for better performance

## Contributing

Feel free to fork this project and submit pull requests for improvements!

## License

This project is open source and available under the MIT License.
