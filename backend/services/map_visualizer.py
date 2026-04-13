"""
Interactive Map Visualization Service
Creates interactive maps using Folium
"""

from typing import List, Dict, Tuple
import folium
import logging
import os

logger = logging.getLogger("avartan")


class MapVisualizer:
    """
    Creates interactive maps for route visualization
    """
    
    COLORS = {
        'user': 'blue',
        'best_route': 'green',
        'routes': ['green', 'orange', 'red', 'purple', 'gray'],
        'line': '#2ca02c',
    }
    
    @staticmethod
    def create_route_map(user_location: Tuple[float, float],
                        selected_facility: Dict,
                        alternative_facilities: List[Dict],
                        route_info: Dict,
                        output_path: str = 'route_map.html') -> str:
        """
        Create interactive map with user location and facilities
        """
        
        try:
            m = folium.Map(
                location=user_location,
                zoom_start=12,
                tiles='OpenStreetMap'
            )
            
            # Add user location marker
            folium.Marker(
                location=user_location,
                popup=folium.Popup('Your Location', max_width=200),
                icon=folium.Icon(color='blue', icon='info-sign'),
                tooltip='Starting Point'
            ).add_to(m)
            
            # Add selected facility (highlighted)
            folium.Marker(
                location=(selected_facility['latitude'], selected_facility['longitude']),
                popup=folium.Popup(
                    f"<b>{selected_facility['name']}</b><br>"
                    f"Rating: {selected_facility.get('rating', 0)}<br>"
                    f"Distance: {route_info.get('distance_km', 0):.1f} km",
                    max_width=300
                ),
                icon=folium.Icon(color='green', icon='check', prefix='fa'),
                tooltip='Selected Facility'
            ).add_to(m)
            
            # Draw line from user to selected facility
            folium.PolyLine(
                locations=[user_location, 
                          (selected_facility['latitude'], selected_facility['longitude'])],
                color=MapVisualizer.COLORS['line'],
                weight=3,
                opacity=0.8,
                popup=f"Distance: {route_info.get('distance_km', 0):.1f} km"
            ).add_to(m)
            
            # Add alternative facilities
            for idx, facility in enumerate(alternative_facilities[:4]):
                color = MapVisualizer.COLORS['routes'][idx % len(MapVisualizer.COLORS['routes'])]
                
                folium.Marker(
                    location=(facility['latitude'], facility['longitude']),
                    popup=folium.Popup(
                        f"<b>{facility['name']}</b><br>"
                        f"Rating: {facility.get('rating', 0)}<br>"
                        f"Rank: {idx + 2}",
                        max_width=250
                    ),
                    icon=folium.Icon(color=color, icon='star', prefix='fa'),
                    tooltip=f"Option {idx + 2}: {facility['name']}"
                ).add_to(m)
            
            # Save map
            m.save(output_path)
            logger.info(f"✅ Map created: {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error creating map: {e}")
            return None


map_visualizer = MapVisualizer()