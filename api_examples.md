# Solar Rooftop Analysis API - สำหรับ Google Maps Integration

## API Endpoints ใหม่

### 1. `/analyze/geojson` - สำหรับแสดงผลบน Google Maps

**วัตถุประสงค์:** ส่งข้อมูล GeoJSON ที่เหมาะสำหรับแสดงผลบนแผนที่ Google Maps หรือ web mapping libraries อื่นๆ

**Request:**
```json
POST /analyze/geojson
{
  "polygons_data": [
    {
      "polygon_coordinates": [
        {"longitude": 100.540148, "latitude": 13.671842},
        {"longitude": 100.540164, "latitude": 13.671602},
        {"longitude": 100.540577, "latitude": 13.67167},
        {"longitude": 100.54055, "latitude": 13.671899}
      ],
      "monthly_consumption_kwh": 500
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "rooftop_id": 0,
        "solar_potential_score": 85.2,
        "color": "#00FF00",
        "opacity": 0.8,
        "popup_content": "<div>...HTML popup content...</div>",
        "panel_count": 25,
        "yearly_energy_kwh": 12500,
        "monthly_savings": 420,
        "payback_years": 7.5,
        "system_cost": 50000,
        "roof_area_m2": 120.5
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[100.540148, 13.671842], ...]]
      }
    }
  ],
  "metadata": {
    "total_rooftops": 1,
    "total_panels": 25,
    "total_yearly_energy_kwh": 12500,
    "total_monthly_savings": 420,
    "average_solar_score": 85.2,
    "total_system_cost": 50000,
    "map_center": {"lat": 13.671742, "lng": 100.540362},
    "zoom_level": 18
  }
}
```

### 2. `/overlay/{rooftop_id}` - สำหรับดาวน์โหลดรูป overlay

**วัตถุประสงค์:** ส่งไฟล์ PNG overlay สำหรับแสดงเป็น ImageOverlay บนแผนที่

**Request:**
```
GET /overlay/0
```

**Response:** PNG image file

---

## การใช้งานกับ Next.js + Google Maps

### 1. เรียก API เพื่อขอข้อมูล GeoJSON

```javascript
// pages/api/analyze-rooftops.js (Next.js API route)
export default async function handler(req, res) {
  if (req.method === 'POST') {
    try {
      const response = await fetch('http://localhost:8000/analyze/geojson', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(req.body)
      });
      
      const data = await response.json();
      res.status(200).json(data);
    } catch (error) {
      res.status(500).json({ error: 'Failed to analyze rooftops' });
    }
  }
}
```

### 2. แสดงผลบน Google Maps (React Component)

```jsx
// components/SolarMap.jsx
import { GoogleMap, Polygon, InfoWindow, useLoadScript } from '@react-google-maps/api';
import { useState, useEffect } from 'react';

const SolarMap = ({ polygonsData }) => {
  const [geoJsonData, setGeoJsonData] = useState(null);
  const [selectedRooftop, setSelectedRooftop] = useState(null);
  
  const { isLoaded } = useLoadScript({
    googleMapsApiKey: process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY
  });

  useEffect(() => {
    const analyzeRooftops = async () => {
      try {
        const response = await fetch('/api/analyze-rooftops', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ polygons_data: polygonsData })
        });
        
        const data = await response.json();
        setGeoJsonData(data);
      } catch (error) {
        console.error('Failed to analyze rooftops:', error);
      }
    };

    if (polygonsData.length > 0) {
      analyzeRooftops();
    }
  }, [polygonsData]);

  if (!isLoaded || !geoJsonData) return <div>Loading...</div>;

  return (
    <GoogleMap
      center={geoJsonData.metadata.map_center}
      zoom={geoJsonData.metadata.zoom_level}
      mapContainerStyle={{ width: '100%', height: '600px' }}
    >
      {/* Render polygons with solar analysis data */}
      {geoJsonData.features.map((feature, index) => {
        const coordinates = feature.geometry.coordinates[0].map(coord => ({
          lat: coord[1],
          lng: coord[0]
        }));

        return (
          <Polygon
            key={index}
            paths={coordinates}
            options={{
              fillColor: feature.properties.color,
              fillOpacity: feature.properties.opacity,
              strokeColor: feature.properties.color,
              strokeOpacity: 1,
              strokeWeight: 2,
            }}
            onClick={() => setSelectedRooftop(feature)}
          />
        );
      })}

      {/* Info popup */}
      {selectedRooftop && (
        <InfoWindow
          position={{
            lat: selectedRooftop.geometry.coordinates[0][0][1],
            lng: selectedRooftop.geometry.coordinates[0][0][0]
          }}
          onCloseClick={() => setSelectedRooftop(null)}
        >
          <div 
            dangerouslySetInnerHTML={{ 
              __html: selectedRooftop.properties.popup_content 
            }} 
          />
        </InfoWindow>
      )}
    </GoogleMap>
  );
};

export default SolarMap;
```

### 3. Dashboard Component

```jsx
// components/SolarDashboard.jsx
import SolarMap from './SolarMap';
import { useState } from 'react';

const SolarDashboard = () => {
  const [polygonsData] = useState([
    {
      polygon_coordinates: [
        { longitude: 100.540148, latitude: 13.671842 },
        { longitude: 100.540164, latitude: 13.671602 },
        { longitude: 100.540577, latitude: 13.67167 },
        { longitude: 100.54055, latitude: 13.671899 }
      ],
      monthly_consumption_kwh: 500
    },
    // เพิ่มพหลังคาอื่นๆ...
  ]);

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">Solar Rooftop Analysis</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Map Section */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow-lg p-4">
            <h2 className="text-xl font-semibold mb-4">Solar Potential Map</h2>
            <SolarMap polygonsData={polygonsData} />
          </div>
        </div>
        
        {/* Summary Section */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-lg p-4">
            <h2 className="text-xl font-semibold mb-4">Project Summary</h2>
            {/* แสดง metadata จาก API response */}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SolarDashboard;
```

---

## ข้อดีของวิธีนี้

1. **ข้อมูลเบา:** ส่งแค่ coordinates + metadata แทนไฟล์ภาพ
2. **Interactive:** ปรับสี, opacity, popup ได้ทันที
3. **Responsive:** แสดงผลได้ดีทุกขนาดหน้าจอ
4. **Scalable:** รองรับหลักร้อยหลังคาได้
5. **Real-time:** อัปเดตได้ทันทีเมื่อข้อมูลเปลี่ยน

---

## การทดสอบ API

```bash
# เริ่ม FastAPI server
cd /Users/poon.such/Desktop/poom/fork/solsat_poc_phr2/main
python main.py

# ทดสอบ GeoJSON endpoint
curl -X POST "http://localhost:8000/analyze/geojson" \
  -H "Content-Type: application/json" \
  -d '{
    "polygons_data": [
      {
        "polygon_coordinates": [
          {"longitude": 100.540148, "latitude": 13.671842},
          {"longitude": 100.540164, "latitude": 13.671602},
          {"longitude": 100.540577, "latitude": 13.67167}
        ],
        "monthly_consumption_kwh": 500
      }
    ]
  }'

# ทดสอบ overlay image endpoint
curl "http://localhost:8000/overlay/0" --output solar_overlay_0.png
```
