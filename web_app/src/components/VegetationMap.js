"use client";

import { useEffect } from 'react';
import { MapContainer, TileLayer, LayersControl, Polygon, LayerGroup, Rectangle } from 'react-leaflet';
import L from 'leaflet';

// Fix leaflet icon issue in Next.js
if (typeof window !== 'undefined') {
  delete L.Icon.Default.prototype._getIconUrl;
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  });
}

// Tree types and colors based on user reference
const treeSpecies = [
  { name: 'Norway Spruce', color: '#006400', bounds: [[10.82, 122.39], [10.83, 122.40]] },
  { name: 'Scots Pine', color: '#228B22', bounds: [[10.81, 122.38], [10.825, 122.395]] },
  { name: 'Birch', color: '#EE82EE', bounds: [[10.815, 122.395], [10.825, 122.41]] },
  { name: 'Beech', color: '#FF0000', bounds: [[10.825, 122.38], [10.835, 122.39]] },
  { name: 'Oak', color: '#DAA520', bounds: [[10.81, 122.40], [10.82, 122.41]] },
];

// Generate some random patches to make it look like a real coverage map
function generatePatches(baseBounds, color, count) {
  const patches = [];
  const latDiff = baseBounds[1][0] - baseBounds[0][0];
  const lngDiff = baseBounds[1][1] - baseBounds[0][1];
  
  for (let i = 0; i < count; i++) {
    const lat = baseBounds[0][0] + (Math.random() * latDiff * 3) - latDiff;
    const lng = baseBounds[0][1] + (Math.random() * lngDiff * 3) - lngDiff;
    const w = 0.002 + Math.random() * 0.005;
    const h = 0.002 + Math.random() * 0.005;
    patches.push({
      bounds: [[lat, lng], [lat + h, lng + w]],
      color
    });
  }
  return patches;
}

export default function VegetationMap({ center = [10.8228, 122.3952], zoom = 14 }) {
  
  return (
    <div className="map-wrapper" style={{ position: 'relative', height: '600px', width: '100%', borderRadius: '12px', overflow: 'hidden' }}>
      <MapContainer 
        center={center} 
        zoom={zoom} 
        style={{ height: '100%', width: '100%' }}
        scrollWheelZoom={true}
      >
        <LayersControl position="topright">
          <LayersControl.BaseLayer checked name="Satellite">
            <TileLayer
              url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
              attribution='Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
            />
          </LayersControl.BaseLayer>
          <LayersControl.BaseLayer name="Street Map">
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            />
          </LayersControl.BaseLayer>

          <LayersControl.Overlay checked name="Dominant Tree Species">
            <LayerGroup>
              {treeSpecies.map((species, i) => (
                <LayerGroup key={i}>
                  {generatePatches(species.bounds, species.color, 15).map((patch, j) => (
                    <Rectangle 
                      key={j} 
                      bounds={patch.bounds} 
                      pathOptions={{ color: patch.color, fillColor: patch.color, fillOpacity: 0.7, weight: 0 }} 
                    />
                  ))}
                </LayerGroup>
              ))}
            </LayerGroup>
          </LayersControl.Overlay>
        </LayersControl>

        {/* Custom Legend Overlay */}
        <div className="map-legend">
          <h4>Dominant tree species</h4>
          <div className="legend-list">
            <div className="legend-item">
              <span className="color-box" style={{ backgroundColor: '#006400' }}></span>
              <span>Norway Spruce</span>
            </div>
            <div className="legend-item">
              <span className="color-box" style={{ backgroundColor: '#228B22' }}></span>
              <span>Scots Pine</span>
            </div>
            <div className="legend-item">
              <span className="color-box" style={{ backgroundColor: '#EE82EE' }}></span>
              <span>Birch</span>
            </div>
            <div className="legend-item">
              <span className="color-box" style={{ backgroundColor: '#FF0000' }}></span>
              <span>Beech</span>
            </div>
            <div className="legend-item">
              <span className="color-box" style={{ backgroundColor: '#DAA520' }}></span>
              <span>Oak</span>
            </div>
          </div>
          
          <h4 style={{ marginTop: '15px' }}>Species Coverage per Hectare</h4>
          <div className="gradient-bar"></div>
          <div className="gradient-labels">
            <span>0%</span>
            <span>50%</span>
            <span>100%</span>
          </div>
        </div>
      </MapContainer>
    </div>
  );
}
