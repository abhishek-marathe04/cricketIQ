import streamlit as st
import posthog
from config import POSTHOG_API_KEY, POSTHOG_HOST

posthog.api_key = POSTHOG_API_KEY
posthog.host = POSTHOG_HOST

def inject_analytics_script():
    
    posthog_js = """
    <!-- PostHog JS snippet -->
    <script>
    !function(t,e){{
        var o,n,p;
        window.posthog=window.posthog||[],posthog._i=[],
        posthog.init=function(i,s){{
            function r(t,e){{
                var o=e.split(".");
                2==o.length&&(t=t[o[0]],e=o[1]),
                t[e]=function(){{
                    t.push([e].concat(Array.prototype.slice.call(arguments,0)));
                }}
            }}
            var a=posthog;
            "undefined"!==typeof s ? a=posthog[s]=[] : s="posthog";
            a.people=a.people||[];
            posthog._i.push([i,s]);
            for(var c=["capture","identify","alias","people.set","people.delete_user"],u=0;u<c.length;u++) r(posthog,c[u]);
        }},
        posthog.__SV=1;
        var d=e.createElement("script");
        d.type="text/javascript",d.async=!0,d.src="{host}/static/array.js";
        var m=e.getElementsByTagName("script")[0];
        m.parentNode.insertBefore(d,m)
    }}(document,window.posthog||[]);
    posthog.init("{api_key}", {{api_host: "{host}"}} );
    posthog.capture("$pageview");
    </script>
    """.format(api_key=POSTHOG_API_KEY, host=POSTHOG_HOST)

    st.components.v1.html(posthog_js, height=0)


def track_event(user_id, event_name, properties=None):
    """Function to track events with PostHog."""
    posthog.capture(
        distinct_id=user_id,  # You can use a user ID or session ID here
        event=event_name,
        properties=properties if properties else {}
    )
