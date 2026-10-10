"use client";

import { useEffect } from 'react';
import { MapContainer, TileLayer, useMap } from 'react-leaflet';
import L from 'leaflet';

// Ensure leaflet.heat works with SSR by requiring it only on the client
if (typeof window !== 'undefined') {
  window.L = L;
  require('leaflet.heat');
}

function HeatmapLayer({ points }) {
  const map = useMap();
  
  useEffect(() => {
    if (!map || !window.L || !window.L.heatLayer) return;
    
    const heat = window.L.heatLayer(points, {
      radius: 25,
      blur: 15,
      maxZoom: 17,
      gradient: { 0.4: 'green', 0.6: 'yellow', 0.8: 'orange', 1.0: 'red' }
    }).addTo(map);

    return () => {
      map.removeLayer(heat);
    };
  }, [map, points]);

  return null;
}

export default function VegetationHeatmap({ center = [14.65, 121.05], zoom = 12 }) {
  // Mock data for tree/vegetation density (Latitude, Longitude, Intensity)
  // Higher intensity (e.g. 1.0) means denser vegetation factors affecting water
  const heatmapPoints = [
    [14.65, 121.05, 0.9],
    [14.655, 121.052, 0.8],
    [14.66, 121.045, 0.6],
    [14.64, 121.06, 0.7],
    [14.645, 121.055, 1.0],
    [14.67, 121.07, 0.5],
    [14.63, 121.04, 0.4],
    [14.68, 121.03, 0.8],
    [14.62, 121.08, 0.9],
  ];

  return (
    <div style={{ position: 'relative', zIndex: 0 }}>
      <MapContainer 
        center={center} 
        zoom={zoom} 
        style={{ height: '400px', width: '100%', borderRadius: '12px' }}
        scrollWheelZoom={false}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        <HeatmapLayer points={heatmapPoints} />
      </MapContainer>
    </div>
  );
}
