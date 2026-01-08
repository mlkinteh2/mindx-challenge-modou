"""
MIND X FastAPI Backend Service
Provides REST API endpoints for compliance analysis and CO2 predictions
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import pandas as pd
import numpy as np
from compliance_engine import ComplianceEngine
import uvicorn

# Initialize FastAPI app
app = FastAPI(
    title="MIND X Compliance API",
    description="Maritime Compliance and Emissions Prediction API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize compliance engine
engine = ComplianceEngine()

# Load fleet data
try:
    fleet_data = pd.read_csv('data/mindx test dataset.csv')
except FileNotFoundError:
    fleet_data = None
    print("Warning: Dataset not found. Some endpoints may not work.")


# Pydantic models for request/response
class VesselJourney(BaseModel):
    ship_type: str
    route_id: str
    month: str
    distance: float
    fuel_type: str
    fuel_consumption: float
    weather_conditions: str
    engine_efficiency: float


class PredictionRequest(BaseModel):
    journeys: List[VesselJourney]


class PredictionResponse(BaseModel):
    predictions: List[Dict[str, float]]


class PoolingRequest(BaseModel):
    vessel1_id: str
    vessel2_id: str


class ComplianceSummary(BaseModel):
    total_vessels: int
    surplus_vessels: int
    deficit_vessels: int
    fleet_avg_intensity: float
    target_intensity: float
    total_financial_impact: float


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "MIND X Compliance API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "predict": "/api/predict",
            "compliance": "/api/compliance",
            "compliance_summary": "/api/compliance/summary",
            "vessels": "/api/vessels",
            "vessel_detail": "/api/vessels/{vessel_id}",
            "pooling": "/api/pooling",
            "optimal_pools": "/api/pooling/optimal"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model_loaded": engine.model_loaded,
        "data_loaded": fleet_data is not None
    }


@app.post("/api/predict", response_model=PredictionResponse)
async def predict_emissions(request: PredictionRequest):
    """
    Predict CO2 emissions for vessel journeys.
    
    Args:
        request: List of vessel journeys
        
    Returns:
        Predictions with CO2 emissions and GHG intensity
    """
    if not engine.model_loaded:
        raise HTTPException(status_code=503, detail="Model not loaded. Please train the model first.")
    
    try:
        # Convert request to DataFrame
        journeys_data = [journey.dict() for journey in request.journeys]
        df = pd.DataFrame(journeys_data)
        
        # Predict CO2 emissions
        predictions = engine.predict_co2_emissions(df)
        
        # Calculate GHG intensity
        results = []
        for i, (_, row) in enumerate(df.iterrows()):
            ghg_intensity = engine.calculate_ghg_intensity(predictions[i], row['distance'])
            results.append({
                "co2_emissions": float(predictions[i]),
                "ghg_intensity": float(ghg_intensity),
                "distance": float(row['distance']),
                "fuel_consumption": float(row['fuel_consumption'])
            })
        
        return {"predictions": results}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/compliance/summary", response_model=ComplianceSummary)
async def get_compliance_summary():
    """Get fleet compliance summary."""
    if fleet_data is None:
        raise HTTPException(status_code=503, detail="Fleet data not loaded")
    
    try:
        report = engine.generate_compliance_report(fleet_data)
        return ComplianceSummary(**report['fleet_summary'])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/compliance")
async def get_full_compliance_report():
    """Get full compliance report for all vessels."""
    if fleet_data is None:
        raise HTTPException(status_code=503, detail="Fleet data not loaded")
    
    try:
        report = engine.generate_compliance_report(fleet_data)
        
        # Convert DataFrames to dictionaries
        compliance_details = report['compliance_details'].to_dict(orient='records')
        top_performers = report['top_performers'].to_dict(orient='records')
        worst_performers = report['worst_performers'].to_dict(orient='records')
        
        return {
            "fleet_summary": report['fleet_summary'],
            "compliance_details": compliance_details,
            "top_performers": top_performers,
            "worst_performers": worst_performers,
            "optimal_pooling_opportunities": report['optimal_pooling_opportunities']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/vessels")
async def get_all_vessels():
    """Get list of all vessels with their compliance status."""
    if fleet_data is None:
        raise HTTPException(status_code=503, detail="Fleet data not loaded")
    
    try:
        compliance_df, _, _ = engine.calculate_fleet_compliance(fleet_data)
        vessels = compliance_df[['ship_id', 'ship_type', 'ghg_intensity', 'compliance_status', 
                                  'compliance_balance', 'financial_impact']].to_dict(orient='records')
        return {"vessels": vessels}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/vessels/{vessel_id}")
async def get_vessel_detail(vessel_id: str):
    """Get detailed information for a specific vessel."""
    if fleet_data is None:
        raise HTTPException(status_code=503, detail="Fleet data not loaded")
    
    try:
        # Get vessel journeys
        vessel_journeys = fleet_data[fleet_data['ship_id'] == vessel_id]
        
        if vessel_journeys.empty:
            raise HTTPException(status_code=404, detail=f"Vessel {vessel_id} not found")
        
        # Get compliance data
        compliance_df, fleet_avg, target = engine.calculate_fleet_compliance(fleet_data)
        vessel_compliance = compliance_df[compliance_df['ship_id'] == vessel_id].iloc[0].to_dict()
        
        # Get journey details
        journeys = vessel_journeys.to_dict(orient='records')
        
        return {
            "vessel_id": vessel_id,
            "compliance": vessel_compliance,
            "journeys": journeys,
            "total_journeys": len(journeys)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/pooling")
async def simulate_pooling(request: PoolingRequest):
    """
    Simulate pooling between two vessels.
    
    Args:
        request: Vessel IDs for pooling
        
    Returns:
        Pooling simulation results
    """
    if fleet_data is None:
        raise HTTPException(status_code=503, detail="Fleet data not loaded")
    
    try:
        compliance_df, _, _ = engine.calculate_fleet_compliance(fleet_data)
        
        # Check if vessels exist
        if request.vessel1_id not in compliance_df['ship_id'].values:
            raise HTTPException(status_code=404, detail=f"Vessel {request.vessel1_id} not found")
        if request.vessel2_id not in compliance_df['ship_id'].values:
            raise HTTPException(status_code=404, detail=f"Vessel {request.vessel2_id} not found")
        
        result = engine.simulate_pooling(request.vessel1_id, request.vessel2_id, compliance_df)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/pooling/optimal")
async def get_optimal_pooling(max_pools: int = 10):
    """
    Get optimal pooling opportunities.
    
    Args:
        max_pools: Maximum number of pooling pairs to return
        
    Returns:
        List of optimal pooling opportunities
    """
    if fleet_data is None:
        raise HTTPException(status_code=503, detail="Fleet data not loaded")
    
    try:
        compliance_df, _, _ = engine.calculate_fleet_compliance(fleet_data)
        optimal_pools = engine.identify_optimal_pools(compliance_df, max_pools)
        return {"optimal_pools": optimal_pools}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ship-types")
async def get_ship_types():
    """Get list of all ship types in the fleet."""
    if fleet_data is None:
        raise HTTPException(status_code=503, detail="Fleet data not loaded")
    
    ship_types = fleet_data['ship_type'].unique().tolist()
    return {"ship_types": ship_types}


@app.get("/api/routes")
async def get_routes():
    """Get list of all routes."""
    if fleet_data is None:
        raise HTTPException(status_code=503, detail="Fleet data not loaded")
    
    routes = fleet_data['route_id'].unique().tolist()
    return {"routes": routes}


if __name__ == "__main__":
    print("🚀 Starting MIND X Compliance API Server...")
    print("📊 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("\n✨ MIND X Maritime Compliance System")
    print("   - Task A: Compliance Engine with ML predictions")
    print("   - Task B: Fleet Arbitrage Dashboard integration")
    print("   - Task C: Anomaly detection and analysis\n")
    uvicorn.run("api:app", host="0.0.0.0", port=8001, reload=False)
