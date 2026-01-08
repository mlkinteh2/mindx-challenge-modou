"""
MIND X Compliance Engine
Task A: CO2 Prediction, GHG Intensity Calculation, and Regulatory Benchmarking
"""

import pandas as pd
import numpy as np
import joblib
from typing import Dict, Tuple, List
import warnings
warnings.filterwarnings('ignore')


class ComplianceEngine:
    """
    Compliance Engine for maritime emissions compliance analysis.
    Implements FuelEU Maritime regulatory requirements.
    """
    
    def __init__(self, model_path: str = 'models/co2_emission_model.pkl',
                 scaler_path: str = 'models/scaler.pkl',
                 encoders_path: str = 'models/label_encoders.pkl',
                 features_path: str = 'models/feature_columns.pkl'):
        """Initialize the compliance engine with trained model and preprocessors."""
        try:
            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path) if scaler_path else None
            self.label_encoders = joblib.load(encoders_path)
            self.feature_columns = joblib.load(features_path)
            self.model_loaded = True
        except FileNotFoundError:
            print("Warning: Model files not found. Please train the model first.")
            self.model_loaded = False
    
    def predict_co2_emissions(self, vessel_data: pd.DataFrame) -> np.ndarray:
        """
        Predict CO2 emissions for vessel journeys.
        
        Args:
            vessel_data: DataFrame with vessel operational data
            
        Returns:
            Array of predicted CO2 emissions
        """
        if not self.model_loaded:
            raise ValueError("Model not loaded. Please train the model first.")
        
        # Encode categorical variables
        df_encoded = vessel_data.copy()
        categorical_cols = ['ship_type', 'route_id', 'month', 'fuel_type', 'weather_conditions']
        
        for col in categorical_cols:
            if col in df_encoded.columns:
                df_encoded[col + '_encoded'] = self.label_encoders[col].transform(df_encoded[col])
        
        # Select features
        X = df_encoded[self.feature_columns]
        
        # Scale if needed (for Linear Regression)
        if self.scaler is not None:
            X_scaled = self.scaler.transform(X)
            predictions = self.model.predict(X_scaled)
        else:
            predictions = self.model.predict(X)
        
        return predictions
    
    def calculate_ghg_intensity(self, co2_emissions: float, distance: float, 
                                 cargo_capacity: float = 1.0) -> float:
        """
        Calculate GHG Intensity (gCO2/ton-mile or gCO2/mile for passenger vessels).
        
        GHG Intensity = CO2 Emissions (kg) / (Distance (nautical miles) * Cargo Capacity (tons))
        
        For this dataset, we'll use a simplified version:
        GHG Intensity = CO2 Emissions (kg) / Distance (nautical miles)
        
        Args:
            co2_emissions: CO2 emissions in kg
            distance: Distance traveled in nautical miles
            cargo_capacity: Cargo capacity in tons (default 1.0 for normalization)
            
        Returns:
            GHG intensity in gCO2/ton-mile
        """
        if distance == 0:
            return 0.0
        
        # Convert kg to grams and calculate intensity
        ghg_intensity = (co2_emissions * 1000) / (distance * cargo_capacity)
        return ghg_intensity
    
    def calculate_fleet_compliance(self, fleet_data: pd.DataFrame, 
                                     target_reduction: float = 0.05) -> pd.DataFrame:
        """
        Calculate compliance balance for entire fleet.
        
        Args:
            fleet_data: DataFrame with fleet operational data including CO2_emissions and distance
            target_reduction: Target reduction percentage (default 5% for 2026)
            
        Returns:
            DataFrame with compliance analysis for each vessel
        """
        # Calculate GHG intensity for each vessel journey
        fleet_data['ghg_intensity'] = fleet_data.apply(
            lambda row: self.calculate_ghg_intensity(row['CO2_emissions'], row['distance']),
            axis=1
        )
        
        # Calculate average GHG intensity by vessel
        vessel_avg_intensity = fleet_data.groupby('ship_id').agg({
            'ghg_intensity': 'mean',
            'CO2_emissions': 'sum',
            'distance': 'sum',
            'ship_type': 'first'
        }).reset_index()
        
        # Calculate fleet average GHG intensity
        fleet_avg_intensity = fleet_data['ghg_intensity'].mean()
        
        # Calculate 2026 target intensity (5% reduction from average)
        target_intensity = fleet_avg_intensity * (1 - target_reduction)
        
        # Determine surplus/deficit for each vessel
        vessel_avg_intensity['target_intensity'] = target_intensity
        vessel_avg_intensity['intensity_difference'] = (
            vessel_avg_intensity['ghg_intensity'] - target_intensity
        )
        vessel_avg_intensity['compliance_status'] = vessel_avg_intensity['intensity_difference'].apply(
            lambda x: 'Surplus' if x < 0 else 'Deficit'
        )
        
        # Calculate compliance balance (negative = surplus, positive = deficit)
        vessel_avg_intensity['compliance_balance'] = vessel_avg_intensity['intensity_difference']
        
        # Calculate penalty/credit in monetary terms (simplified)
        # Assume penalty rate of $100 per ton of excess CO2
        vessel_avg_intensity['total_distance'] = vessel_avg_intensity['distance']
        vessel_avg_intensity['excess_co2_tons'] = (
            vessel_avg_intensity['intensity_difference'] * 
            vessel_avg_intensity['total_distance'] / 1000000  # Convert g to tons
        )
        vessel_avg_intensity['financial_impact'] = (
            vessel_avg_intensity['excess_co2_tons'] * 100  # $100 per ton
        )
        
        return vessel_avg_intensity, fleet_avg_intensity, target_intensity
    
    def simulate_pooling(self, vessel1_id: str, vessel2_id: str, 
                         compliance_df: pd.DataFrame) -> Dict:
        """
        Simulate pooling between two vessels to offset compliance deficit.
        
        Args:
            vessel1_id: ID of first vessel
            vessel2_id: ID of second vessel
            compliance_df: DataFrame with compliance analysis
            
        Returns:
            Dictionary with pooling simulation results
        """
        # Get vessel data
        vessel1 = compliance_df[compliance_df['ship_id'] == vessel1_id].iloc[0]
        vessel2 = compliance_df[compliance_df['ship_id'] == vessel2_id].iloc[0]
        
        # Calculate combined compliance balance
        combined_balance = vessel1['compliance_balance'] + vessel2['compliance_balance']
        combined_distance = vessel1['total_distance'] + vessel2['total_distance']
        
        # Calculate weighted average intensity
        weighted_intensity = (
            (vessel1['ghg_intensity'] * vessel1['total_distance'] +
             vessel2['ghg_intensity'] * vessel2['total_distance']) /
            combined_distance
        )
        
        # Determine if pooling achieves compliance
        target_intensity = vessel1['target_intensity']
        pooling_successful = weighted_intensity <= target_intensity
        
        # Calculate financial impact
        if pooling_successful:
            excess_co2_tons = 0
            financial_impact = 0
        else:
            excess_intensity = weighted_intensity - target_intensity
            excess_co2_tons = excess_intensity * combined_distance / 1000000
            financial_impact = excess_co2_tons * 100
        
        return {
            'vessel1_id': str(vessel1_id),
            'vessel2_id': str(vessel2_id),
            'vessel1_status': str(vessel1['compliance_status']),
            'vessel2_status': str(vessel2['compliance_status']),
            'vessel1_balance': float(vessel1['compliance_balance']),
            'vessel2_balance': float(vessel2['compliance_balance']),
            'combined_balance': float(combined_balance),
            'weighted_intensity': float(weighted_intensity),
            'target_intensity': float(target_intensity),
            'pooling_successful': bool(pooling_successful),
            'excess_co2_tons': float(excess_co2_tons),
            'financial_impact': float(financial_impact),
            'savings': float(vessel1['financial_impact'] + vessel2['financial_impact'] - financial_impact)
        }
    
    def identify_optimal_pools(self, compliance_df: pd.DataFrame, 
                                max_pools: int = 10) -> List[Dict]:
        """
        Identify optimal vessel pooling opportunities to minimize compliance costs.
        
        Args:
            compliance_df: DataFrame with compliance analysis
            max_pools: Maximum number of pooling pairs to return
            
        Returns:
            List of optimal pooling opportunities
        """
        surplus_vessels = compliance_df[compliance_df['compliance_status'] == 'Surplus']
        deficit_vessels = compliance_df[compliance_df['compliance_status'] == 'Deficit']
        
        pooling_opportunities = []
        
        for _, deficit_vessel in deficit_vessels.iterrows():
            for _, surplus_vessel in surplus_vessels.iterrows():
                pool_result = self.simulate_pooling(
                    deficit_vessel['ship_id'],
                    surplus_vessel['ship_id'],
                    compliance_df
                )
                
                if pool_result['savings'] > 0:
                    pooling_opportunities.append(pool_result)
        
        # Sort by savings (highest first)
        pooling_opportunities.sort(key=lambda x: x['savings'], reverse=True)
        
        return pooling_opportunities[:max_pools]
    
    def generate_compliance_report(self, fleet_data: pd.DataFrame) -> Dict:
        """
        Generate comprehensive compliance report for the fleet.
        
        Args:
            fleet_data: DataFrame with fleet operational data
            
        Returns:
            Dictionary with compliance report
        """
        compliance_df, fleet_avg, target = self.calculate_fleet_compliance(fleet_data)
        
        # Calculate summary statistics
        total_vessels = len(compliance_df)
        surplus_vessels = len(compliance_df[compliance_df['compliance_status'] == 'Surplus'])
        deficit_vessels = len(compliance_df[compliance_df['compliance_status'] == 'Deficit'])
        
        total_financial_impact = compliance_df['financial_impact'].sum()
        
        # Identify top performers and worst performers
        top_performers = compliance_df.nsmallest(5, 'ghg_intensity')[['ship_id', 'ship_type', 'ghg_intensity', 'compliance_status']]
        worst_performers = compliance_df.nlargest(5, 'ghg_intensity')[['ship_id', 'ship_type', 'ghg_intensity', 'compliance_status']]
        
        # Find optimal pooling opportunities
        optimal_pools = self.identify_optimal_pools(compliance_df)
        
        return {
            'fleet_summary': {
                'total_vessels': total_vessels,
                'surplus_vessels': surplus_vessels,
                'deficit_vessels': deficit_vessels,
                'fleet_avg_intensity': fleet_avg,
                'target_intensity': target,
                'total_financial_impact': total_financial_impact
            },
            'compliance_details': compliance_df,
            'top_performers': top_performers,
            'worst_performers': worst_performers,
            'optimal_pooling_opportunities': optimal_pools
        }


def main():
    """Main function to demonstrate compliance engine usage."""
    # Load dataset
    df = pd.read_csv('backend/data/mindx test dataset.csv')
    
    print("="*80)
    print("MIND X COMPLIANCE ENGINE - Task A")
    print("="*80)
    print(f"\nDataset loaded: {len(df)} records")
    print(f"Unique vessels: {df['ship_id'].nunique()}")
    
    # Initialize compliance engine
    engine = ComplianceEngine()
    
    # Generate compliance report
    if engine.model_loaded:
        print("\n" + "="*80)
        print("GENERATING COMPLIANCE REPORT")
        print("="*80)
        
        report = engine.generate_compliance_report(df)
        
        print("\n📊 FLEET SUMMARY:")
        print(f"  Total Vessels: {report['fleet_summary']['total_vessels']}")
        print(f"  Surplus Vessels: {report['fleet_summary']['surplus_vessels']}")
        print(f"  Deficit Vessels: {report['fleet_summary']['deficit_vessels']}")
        print(f"  Fleet Average GHG Intensity: {report['fleet_summary']['fleet_avg_intensity']:.2f} gCO2/mile")
        print(f"  2026 Target Intensity: {report['fleet_summary']['target_intensity']:.2f} gCO2/mile")
        print(f"  Total Financial Impact: ${report['fleet_summary']['total_financial_impact']:,.2f}")
        
        print("\n🏆 TOP 5 PERFORMERS (Lowest GHG Intensity):")
        print(report['top_performers'].to_string(index=False))
        
        print("\n⚠️  TOP 5 WORST PERFORMERS (Highest GHG Intensity):")
        print(report['worst_performers'].to_string(index=False))
        
        print("\n💡 TOP 5 POOLING OPPORTUNITIES:")
        for i, pool in enumerate(report['optimal_pooling_opportunities'][:5], 1):
            print(f"\n  {i}. {pool['vessel1_id']} ({pool['vessel1_status']}) + {pool['vessel2_id']} ({pool['vessel2_status']})")
            print(f"     Pooling Successful: {'✅ Yes' if pool['pooling_successful'] else '❌ No'}")
            print(f"     Potential Savings: ${pool['savings']:,.2f}")
        
        # Save compliance report
        report['compliance_details'].to_csv('backend/compliance_report.csv', index=False)
        print("\n✅ Compliance report saved to 'backend/compliance_report.csv'")
    else:
        print("\n⚠️  Model not trained yet. Please run the model.ipynb notebook first.")
        
        # Still calculate GHG intensity without predictions
        print("\n" + "="*80)
        print("CALCULATING GHG INTENSITY (WITHOUT PREDICTIONS)")
        print("="*80)
        
        engine_basic = ComplianceEngine.__new__(ComplianceEngine)
        engine_basic.model_loaded = False
        
        # Calculate GHG intensity using actual CO2 emissions
        df['ghg_intensity'] = df.apply(
            lambda row: engine_basic.calculate_ghg_intensity(row['CO2_emissions'], row['distance']),
            axis=1
        )
        
        # Calculate compliance metrics
        vessel_avg = df.groupby('ship_id').agg({
            'ghg_intensity': 'mean',
            'CO2_emissions': 'sum',
            'distance': 'sum',
            'ship_type': 'first'
        }).reset_index()
        
        fleet_avg = df['ghg_intensity'].mean()
        target = fleet_avg * 0.95  # 5% reduction
        
        vessel_avg['target_intensity'] = target
        vessel_avg['intensity_difference'] = vessel_avg['ghg_intensity'] - target
        vessel_avg['compliance_status'] = vessel_avg['intensity_difference'].apply(
            lambda x: 'Surplus' if x < 0 else 'Deficit'
        )
        
        print(f"\n📊 Fleet Average GHG Intensity: {fleet_avg:.2f} gCO2/mile")
        print(f"📊 2026 Target Intensity: {target:.2f} gCO2/mile")
        print(f"📊 Surplus Vessels: {len(vessel_avg[vessel_avg['compliance_status'] == 'Surplus'])}")
        print(f"📊 Deficit Vessels: {len(vessel_avg[vessel_avg['compliance_status'] == 'Deficit'])}")
        
        # Save basic compliance data
        vessel_avg.to_csv('backend/compliance_report_basic.csv', index=False)
        print("\n✅ Basic compliance report saved to 'backend/compliance_report_basic.csv'")


if __name__ == "__main__":
    main()
