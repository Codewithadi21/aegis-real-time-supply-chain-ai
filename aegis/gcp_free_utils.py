"""Pure helpers that can be tested without installing GCP SDKs."""
import re

def render_project_sql(sql: str, project_id: str) -> str:
    if not re.fullmatch(r'[a-z][a-z0-9-]{4,61}[a-z0-9]',project_id):
        raise ValueError('Invalid project ID')
    return sql.replace('{{PROJECT_ID}}',project_id)
