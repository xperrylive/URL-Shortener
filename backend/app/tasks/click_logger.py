"""
Click Logger Background Task.

Processes a click event asynchronously:
  1. Parse user_agent → device_type (mobile / desktop / bot / unknown)
  2. Resolve ip_address → country, city (via geoip2)
  3. Insert row into clicks table
  4. Increment urls.click_count counter
"""
