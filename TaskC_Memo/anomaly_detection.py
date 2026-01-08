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
if len(anomalies) > 0:
    top_anomaly = max(anomalies, key=lambda x: abs(x['fuel_deviation_pct']))
    
    print(f"\n🚨 CRITICAL ANOMALY IDENTIFIED:")
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
print("GENERATING VISUALIZATIONS")
print("="*80)

# Create visualization
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# 1. Fuel Consumption vs Distance (with anomalies highlighted)
ax1 = axes[0, 0]
for ship_type in df['ship_type'].unique():
    ship_df = df[df['ship_type'] == ship_type]
    ax1.scatter(ship_df['distance'], ship_df['fuel_consumption'], 
                alpha=0.5, label=ship_type, s=30)

# Highlight top anomaly
if len(anomalies) > 0:
    ax1.scatter(top_anomaly['distance'], top_anomaly['fuel_consumption'],
                color='red', s=200, marker='*', edgecolors='black', linewidths=2,
                label='Critical Anomaly', zorder=5)

ax1.set_xlabel('Distance (nautical miles)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Fuel Consumption', fontsize=12, fontweight='bold')
ax1.set_title('Fuel Consumption vs Distance\n(Anomaly Highlighted)', fontsize=14, fontweight='bold')
ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
ax1.grid(alpha=0.3)

# 2. CO2 Intensity Distribution
ax2 = axes[0, 1]
df.boxplot(column='co2_intensity', by='ship_type', ax=ax2)
ax2.set_xlabel('Ship Type', fontsize=12, fontweight='bold')
ax2.set_ylabel('CO2 Intensity (kg/nm)', fontsize=12, fontweight='bold')
ax2.set_title('CO2 Intensity by Ship Type', fontsize=14, fontweight='bold')
plt.suptitle('')

# 3. Fuel Efficiency Distribution
ax3 = axes[1, 0]
df['fuel_efficiency'].hist(bins=50, ax=ax3, edgecolor='black', alpha=0.7)
ax3.set_xlabel('Fuel Efficiency (nm/unit fuel)', fontsize=12, fontweight='bold')
ax3.set_ylabel('Frequency', fontsize=12, fontweight='bold')
ax3.set_title('Fuel Efficiency Distribution', fontsize=14, fontweight='bold')
ax3.axvline(df['fuel_efficiency'].mean(), color='red', linestyle='--', 
            linewidth=2, label=f'Mean: {df["fuel_efficiency"].mean():.2f}')
ax3.legend()

# 4. Weather Impact on Fuel Consumption
ax4 = axes[1, 1]
weather_fuel = df.groupby('weather_conditions')['fuel_consumption'].mean().sort_values()
weather_fuel.plot(kind='barh', ax=ax4, color=['#10b981', '#f59e0b', '#ef4444'])
ax4.set_xlabel('Average Fuel Consumption', fontsize=12, fontweight='bold')
ax4.set_ylabel('Weather Conditions', fontsize=12, fontweight='bold')
ax4.set_title('Weather Impact on Fuel Consumption', fontsize=14, fontweight='bold')
ax4.grid(axis='x', alpha=0.3)

plt.tight_layout()
plt.savefig('TaskC_Memo/anomaly_analysis.png', dpi=300, bbox_inches='tight')
print("✅ Visualization saved to 'TaskC_Memo/anomaly_analysis.png'")

# Save anomaly data to CSV
if len(anomalies) > 0:
    anomalies_df = pd.DataFrame(anomalies)
    anomalies_df.to_csv('TaskC_Memo/anomalies_detected.csv', index=False)
    print("✅ Anomaly data saved to 'TaskC_Memo/anomalies_detected.csv'")

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)
print("\nNext Step: Generate PDF technical memo with findings.")
