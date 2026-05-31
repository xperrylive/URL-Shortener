"""
URL ORM Model.

Columns: id (UUID PK), original_url, short_code (UNIQUE, INDEXED),
         custom_alias, user_id (FK), is_active, expires_at,
         click_count, created_at, updated_at
"""
