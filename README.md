# Order Analytics Dashboard

A sleek, production-ready analytics dashboard for visualizing order data with interactive charts, geographic heatmaps, and export capabilities.

![Dashboard Preview](https://via.placeholder.com/800x400/3b82f6/ffffff?text=Order+Analytics+Dashboard)

## Features

- 📊 **Interactive Visualizations**: Real-time charts for sales trends and top products
- 🗺️ **Geographic Heatmap**: State-level sales distribution visualization
- 📅 **Date Filtering**: Quick presets (30/90 days) and custom date ranges
- 📤 **Export Functionality**: Download filtered data as Excel files
- 🔐 **Authentication**: Role-based access control (Admin/Viewer)
- 📱 **Responsive Design**: Works seamlessly on desktop and mobile

## Tech Stack

- **Frontend**: Next.js 15, React 19, TypeScript, Tailwind CSS, Recharts
- **Backend**: FastAPI, Python 3.9+, DuckDB, Pandas
- **Visualization**: Streamlit with Plotly for geographic maps
- **Authentication**: JWT-based auth with role management

## Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.9+
- Git

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd analytics-dashboard
```

2. Install frontend dependencies:
```bash
npm install
```

3. Install backend dependencies:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ..
```

### Running the Application

1. Start both servers with the included script:
```bash
./run_dev.sh
```

Or manually:

2. Start the backend server:
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

3. In a new terminal, start the frontend:
```bash
npm run dev
```

4. (Optional) Start Streamlit for geographic visualization:
```bash
streamlit run streamlit_app.py
```

### Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Streamlit App: http://localhost:8501 (if running)

## Usage

### Demo Credentials

- **Admin**: admin@example.com / admin123
- **Viewer**: viewer@example.com / viewer123

### Getting Started

1. Log in with demo credentials
2. Upload the sample CSV file (generated with `python3 scripts/generate_dummy_data.py`)
3. Explore the dashboard:
   - View key metrics (revenue, orders, customers)
   - Analyze sales trends over time
   - Identify top-selling products
   - Export filtered data to Excel

## Project Structure

```
analytics-dashboard/
├── app/                    # Next.js frontend
│   ├── components/        # React components
│   ├── lib/              # Utilities and API client
│   └── page.tsx          # Main page
├── backend/               # FastAPI backend
│   ├── api/              # API endpoints
│   ├── core/             # Core functionality
│   ├── schemas/          # Pydantic models
│   └── services/         # Business logic
├── scripts/              # Utility scripts
│   └── generate_dummy_data.py
├── streamlit_app.py      # Geographic visualization
└── dummy_orders.csv      # Sample data
```

## API Endpoints

- `POST /api/auth/login` - User authentication
- `POST /api/upload/csv` - Upload order data (Admin only)
- `GET /api/orders` - Get filtered orders
- `GET /api/metrics/dashboard` - Get dashboard metrics
- `GET /api/export/excel` - Export data to Excel

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
npm test
```

### Code Quality

```bash
# Lint frontend
npm run lint

# Format Python code
cd backend
black .
```

## Deployment

### Docker

```bash
docker-compose up
```

### Manual Deployment

See deployment guides for:
- Frontend: Vercel, Netlify
- Backend: Fly.io, Railway, Heroku
- Streamlit: Streamlit Cloud

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details