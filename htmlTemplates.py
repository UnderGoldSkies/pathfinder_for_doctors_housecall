directions_map = """
<iframe
  width="700"
  height="500"
  frameborder="0" style="border:0"
  referrerpolicy="no-referrer-when-downgrade"
  src="https://www.google.com/maps/embed/v1/directions?key={google_api_key}&origin={ori}&destination={dest}&mode=driving&region=SG"
  allowfullscreen>
</iframe>
"""

directions_map_full = """
<iframe
    width="700"
    height="500"
    frameborder="0" style="border:0"
    src="https://www.google.com/maps/embed/v1/directions?key={google_api_key}&origin={origin}&destination={destination}&waypoints={waypoints}&mode=driving&region=SG"
    allowfullscreen>
</iframe>
"""
