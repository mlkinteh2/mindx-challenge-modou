"""
Task C: Anomaly Detection and Technical Analysis
Identifies outliers in the maritime dataset and provides physical reasoning
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (14, 8)

# Load dataset
df = pd.read_csv('backend/data/mindx test dataset.csv')

print("="*80)
print("TASK C: ANOMALY DETECTION AND TECHNICAL ANALYSIS")
print("="*80)

# Calculate fuel efficiency (distance per unit fuel)
df['fuel_efficiency'] = df['distance'] / df['fuel_consumption']

# Calculate CO2 intensity (CO2 per distance)
df['co2_intensity'] = df['CO2_emissions'] / df['distance']

# Calculate fuel-to-CO2 ratio
df['fuel_to_co2_ratio'] = df['CO2_emissions'] / df['fuel_consumption']

print("\n📊 Dataset Overview:")
print(f"Total Records: {len(df)}")
print(f"Unique Vessels: {df['ship_id'].nunique()}")
print(f"Date Range: {df['month'].unique()}")

# ============================================================================
# ANOMALY DETECTION METHOD 1: Statistical Outliers (Z-Score)
# ============================================================================
print("\n" + "="*80)
print("METHOD 1: STATISTICAL OUTLIER DETECTION (Z-SCORE)")
print("="*80)

# Calculate Z-scores for key metrics
df['fuel_efficiency_zscore'] = np.abs(stats.zscore(df['fuel_efficiency']))
df['co2_intensity_zscore'] = np.abs(stats.zscore(df['co2_intensity']))
df['fuel_consumption_zscore'] = np.abs(stats.zscore(df['fuel_consumption']))

# Identify outliers (Z-score > 3)
outliers_fuel_eff = df[df['fuel_efficiency_zscore'] > 3]
outliers_co2_int = df[df['co2_intensity_zscore'] > 3]
outliers_fuel_cons = df[df['fuel_consumption_zscore'] > 3]

print(f"\n🔍 Outliers Found:")
print(f"  - Fuel Efficiency Outliers: {len(outliers_fuel_eff)}")
print(f"  - CO2 Intensity Outliers: {len(outliers_co2_int)}")
print(f"  - Fuel Consumption Outliers: {len(outliers_fuel_cons)}")

# ============================================================================
# ANOMALY DETECTION METHOD 2: Fuel Consumption vs Distance Analysis
# ============================================================================
print("\n" + "="*80)
print("METHOD 2: FUEL CONSUMPTION VS DISTANCE ANALYSIS")
print("="*80)

# Calculate expected fuel consumption based on distance (linear regression)
from sklearn.linear_model import LinearRegression

# Group by ship type for better analysis
ship_types = df['ship_type'].unique()

anomalies = []

for ship_type in ship_types:
    ship_df = df[df['ship_type'] == ship_type].copy()
    
    # Fit linear model
    X = ship_df[['distance']].values
    y = ship_df['fuel_consumption'].values
    
    model = LinearRegression()
    model.fit(X, y)
    
    # Predict expected fuel consumption
    ship_df['expected_fuel'] = model.predict(X)
    ship_df['fuel_deviation'] = ship_df['fuel_consumption'] - ship_df['expected_fuel']
    ship_df['fuel_deviation_pct'] = (ship_df['fuel_deviation'] / ship_df['expected_fuel']) * 100
    
    # Find significant deviations (>50% deviation)
    significant_anomalies = ship_df[abs(ship_df['fuel_deviation_pct']) > 50]
    
    if len(significant_anomalies) > 0:
        print(f"\n{ship_type}:")
        print(f"  Anomalies found: {len(significant_anomalies)}")
        
        for _, anomaly in significant_anomalies.head(3).iterrows():
            anomalies.append(anomaly)
            print(f"  - {anomaly['ship_id']} ({anomaly['month']}): "
                  f"{anomaly['fuel_deviation_pct']:.1f}% deviation")
            print(f"    Distance: {anomaly['distance']:.2f} nm, "
                  f"Fuel: {anomaly['fuel_consumption']:.2f} (Expected: {anomaly['expected_fuel']:.2f})")

# ============================================================================
# DETAILED ANALYSIS OF TOP ANOMALY
# ============================================================================
print("\n" + "="*80)
print("DETAILED ANALYSIS: TOP ANOMALY")
print("="*80)

# Find the most extreme anomaly
# Find the most extreme anomaly
if len(anomalies) > 0:
    top_anomaly = max(anomalies, key=lambda x: abs(x['fuel_deviation_pct']))
else:
    # Fallback: Just get the max positive deviation in the whole dataset
    df['fuel_deviation'] = df['fuel_consumption'] - (df['distance'] * (df['fuel_consumption'].mean() / df['distance'].mean())) # Approximate
    idx = df['fuel_deviation'].idxmax()
    top_anomaly = df.iloc[idx]
    # Re-calculate expected for this specific one for reporting
    top_anomaly['expected_fuel'] = top_anomaly['fuel_consumption'] - top_anomaly['fuel_deviation']
    top_anomaly['fuel_deviation_pct'] = (top_anomaly['fuel_deviation'] / top_anomaly['expected_fuel']) * 100
    print("Fallback to max deviation in dataset.")

with open('TaskC_Memo/outlier_details.txt', 'w') as f:
    f.write(f"Vessel ID: {top_anomaly['ship_id']}\\n")
    f.write(f"Ship Type: {top_anomaly['ship_type']}\\n")
    f.write(f"Deviation: {top_anomaly['fuel_deviation_pct']:.1f}%\\n")
    f.write(f"Distance: {top_anomaly['distance']:.2f}\\n")
    f.write(f"Fuel: {top_anomaly['fuel_consumption']:.2f}\\n")
    f.write(f"Weather: {top_anomaly['weather_conditions']}\\n")

print(f"\\n🚨 CRITICAL ANOMALY IDENTIFIED:")
print(f"  Vessel ID: {top_anomaly['ship_id']}")
print(f"  Ship Type: {top_anomaly['ship_type']}")
print(f"  Month: {top_anomaly['month']}")
print(f"  Route: {top_anomaly['route_id']}")
print(f"  Distance: {top_anomaly['distance']:.2f} nautical miles")
print(f"  Fuel Consumption: {top_anomaly['fuel_consumption']:.2f} units")
print(f"  Expected Fuel: {top_anomaly['expected_fuel']:.2f} units")
print(f"  Deviation: {top_anomaly['fuel_deviation_pct']:.1f}%")
print(f"  CO2 Emissions: {top_anomaly['CO2_emissions']:.2f} kg")
print(f"  Weather: {top_anomaly['weather_conditions']}")
print(f"  Engine Efficiency: {top_anomaly['engine_efficiency']:.2f}%")

# Physical reasoning
print(f"\n🔬 PHYSICAL REASONING:")

if top_anomaly['fuel_deviation_pct'] > 0:
    print(f"  This vessel consumed {abs(top_anomaly['fuel_deviation_pct']):.1f}% MORE fuel than expected.")
    print(f"\n  Possible Causes:")
    print(f"  1. HULL BIOFOULING:")
    print(f"     - Marine organism growth on hull increases friction")
    print(f"     - Can increase fuel consumption by 20-60%")
    print(f"     - Requires regular hull cleaning and maintenance")
    print(f"\n  2. PARAMETRIC ROLLING:")
    print(f"     - Dangerous rolling motion in head/following seas")
    print(f"     - Causes significant speed loss and fuel waste")
    print(f"     - Weather: {top_anomaly['weather_conditions']}")
    print(f"\n  3. ENGINE DEGRADATION:")
    print(f"     - Engine efficiency: {top_anomaly['engine_efficiency']:.2f}%")
    print(f"     - Worn components reduce combustion efficiency")
    print(f"     - Requires maintenance and overhaul")
    print(f"\n  4. ADVERSE WEATHER CONDITIONS:")
    print(f"     - Weather: {top_anomaly['weather_conditions']}")
    print(f"     - High waves and wind increase resistance")
    print(f"     - May require speed reduction or route deviation")
else:
    print(f"  This vessel consumed {abs(top_anomaly['fuel_deviation_pct']):.1f}% LESS fuel than expected.")
    print(f"\n  Possible Causes:")
    print(f"  1. OPTIMAL ROUTING:")
    print(f"     - Favorable currents and weather conditions")
    print(f"     - Efficient route planning")
    print(f"\n  2. RECENT MAINTENANCE:")
    print(f"     - Clean hull with minimal biofouling")
    print(f"     - Well-maintained engine systems")
    print(f"\n  3. DATA QUALITY ISSUE:")
    print(f"     - Potential sensor error or data entry mistake")
    print(f"     - Requires verification")
    
    # Save anomaly details for the memo
    anomaly_data = {
        'vessel_id': top_anomaly['ship_id'],
        'ship_type': top_anomaly['ship_type'],
        'month': top_anomaly['month'],
        'route': top_anomaly['route_id'],
        'distance': top_anomaly['distance'],
        'fuel_consumption': top_anomaly['fuel_consumption'],
        'expected_fuel': top_anomaly['expected_fuel'],
        'deviation_pct': top_anomaly['fuel_deviation_pct'],
        'co2_emissions': top_anomaly['CO2_emissions'],
        'weather': top_anomaly['weather_conditions'],
        'engine_efficiency': top_anomaly['engine_efficiency']
    }

# ============================================================================
# VISUALIZATION
# ============================================================================
print("\n" + "="*80)
print("GENERATING FOCUSED VISUALIZATION")
print("="*80)

# Create single focused visualization
plt.figure(figsize=(12, 8))
ax = plt.gca()

# Plot all vessels
for ship_type in df['ship_type'].unique():
    ship_df = df[df['ship_type'] == ship_type]
    plt.scatter(ship_df['distance'], ship_df['fuel_consumption'], 
                alpha=0.6, label=ship_type, s=50, edgecolors='w', linewidth=0.5)

# Highlight TOP anomaly (NG008)
if 'top_anomaly' in locals():
    plt.scatter(top_anomaly['distance'], top_anomaly['fuel_consumption'],
                color='#ef4444', s=300, marker='*', edgecolors='black', linewidths=2,
                label=f'Critical Anomaly ({top_anomaly["ship_id"]})', zorder=10)
    
    # Add annotation arrow
    plt.annotate(f"{top_anomaly['ship_id']}\n(+{top_anomaly['fuel_deviation_pct']:.1f}% Fuel)",
                 xy=(top_anomaly['distance'], top_anomaly['fuel_consumption']),
                 xytext=(top_anomaly['distance'] - 100, top_anomaly['fuel_consumption'] + 2000),
                 arrowprops=dict(facecolor='black', shrink=0.05),
                 fontsize=11, fontweight='bold', bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="black", alpha=0.9))

plt.xlabel('Distance Traveled (nautical miles)', fontsize=12, fontweight='bold')
plt.ylabel('Fuel Consumption (units)', fontsize=12, fontweight='bold')
plt.title('Fuel Consumption vs Distance: Anomaly Detection', fontsize=16, fontweight='bold', pad=20)
plt.legend(fontsize=10, loc='upper left', frameon=True, framealpha=0.9, shadow=True)
plt.grid(True, linestyle='--', alpha=0.7)
sns.despine()

# Save focused chart
output_path = 'TaskC_Memo/ng008_anomaly_scatter.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"✅ Focused visualization saved to '{output_path}'")

# Save anomaly data to CSV
if len(anomalies) > 0:
    anomalies_df = pd.DataFrame(anomalies)
    anomalies_df.to_csv('TaskC_Memo/anomalies_detected.csv', index=False)
    print("✅ Anomaly data saved to 'TaskC_Memo/anomalies_detected.csv'")

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)
print("Next Step: Embed 'ng008_anomaly_scatter.png' into your Technical Memo.")
