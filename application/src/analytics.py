from config import IS_PROD, GA_MEASUREMENT_ID
import streamlit.components.v1 as components

def inject_ga_script():
    if IS_PROD and GA_MEASUREMENT_ID.startswith("G-"):
        components.html(f"""
        <!-- Google tag (gtag.js) -->
        <script async src="https://www.googletagmanager.com/gtag/js?id={GA_MEASUREMENT_ID}"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){{dataLayer.push(arguments);}}
          gtag('js', new Date());
          gtag('config', '{GA_MEASUREMENT_ID}');
        </script>
        """, height=0)

def track_user_event(user_input: str, output: str):
    if IS_PROD and GA_MEASUREMENT_ID.startswith("G-"):
        components.html(f"""
        <script>
            if (window.gtag) {{
                gtag('event', 'user_interaction', {{
                    'event_category': 'User Query',
                    'event_label': `{user_input}`,
                    'value': `{output}`
                }});
            }}
        </script>
        """, height=0)

def track_error_event(error_message: str, context: str = "app"):
    if IS_PROD and GA_MEASUREMENT_ID.startswith("G-"):
        components.html(f"""
        <script>
            if (window.gtag) {{
                gtag('event', 'error_occurred', {{
                    'event_category': 'Error',
                    'event_label': `{context}`,
                    'value': `{error_message}`
                }});
            }}
        </script>
        """, height=0)