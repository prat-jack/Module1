# Brand Configuration for Executive Analytics Dashboard
# Customize these settings to match your company's brand identity

BRAND_THEMES = {
    "corporate_blue": {
        "name": "Corporate Blue (Default)",
        "primary": "#1B365D",
        "secondary": "#2E5984", 
        "accent": "#C5912B",
        "success": "#27AE60",
        "warning": "#F39C12",
        "danger": "#E74C3C",
        "description": "Professional navy blue theme suitable for corporate presentations"
    },
    
    "executive_green": {
        "name": "Executive Green",
        "primary": "#1B4332",
        "secondary": "#2D6A4F",
        "accent": "#D4A574",
        "success": "#52B788",
        "warning": "#F77F00",
        "danger": "#D00000",
        "description": "Sophisticated green theme for finance and growth-focused presentations"
    },
    
    "modern_purple": {
        "name": "Modern Purple",
        "primary": "#3D1A78",
        "secondary": "#5B2C87",
        "accent": "#FFB347",
        "success": "#4ECDC4",
        "warning": "#FFA726",
        "danger": "#EF5350",
        "description": "Contemporary purple theme for technology and innovation companies"
    },
    
    "classic_burgundy": {
        "name": "Classic Burgundy",
        "primary": "#722F37",
        "secondary": "#8B4A47",
        "accent": "#DAA520",
        "success": "#4F7942",
        "warning": "#CD853F",
        "danger": "#B22222",
        "description": "Traditional burgundy theme for luxury brands and professional services"
    },
    
    "minimal_gray": {
        "name": "Minimal Gray",
        "primary": "#2C3E50",
        "secondary": "#34495E",
        "accent": "#E67E22",
        "success": "#27AE60",
        "warning": "#F39C12",
        "danger": "#E74C3C",
        "description": "Clean grayscale theme with orange accents for modern, minimal presentations"
    }
}

LOGO_POSITIONS = {
    "top_left": "Top Left",
    "top_right": "Top Right", 
    "center": "Center Header",
    "bottom_right": "Bottom Right"
}

FONT_FAMILIES = {
    "segoe": "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    "arial": "Arial, Helvetica, sans-serif",
    "times": "'Times New Roman', Times, serif",
    "georgia": "Georgia, serif",
    "helvetica": "'Helvetica Neue', Helvetica, Arial, sans-serif",
    "roboto": "'Roboto', sans-serif"
}

def get_brand_css(theme_key="corporate_blue", font_family="segoe", company_name="", logo_url=""):
    """Generate CSS with brand customizations"""
    
    theme = BRAND_THEMES.get(theme_key, BRAND_THEMES["corporate_blue"])
    font = FONT_FAMILIES.get(font_family, FONT_FAMILIES["segoe"])
    
    css = f"""
    <style>
    /* Brand Customized Executive Theme */
    :root {{
        --primary-color: {theme['primary']};
        --secondary-color: {theme['secondary']};
        --accent-color: {theme['accent']};
        --success-color: {theme['success']};
        --warning-color: {theme['warning']};
        --danger-color: {theme['danger']};
        --brand-font: {font};
        --executive-gradient: linear-gradient(135deg, {theme['primary']} 0%, {theme['secondary']} 50%, {theme['accent']} 100%);
    }}
    
    /* Updated Executive Header with Brand Colors */
    .executive-header {{
        background: var(--executive-gradient);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        position: relative;
        overflow: hidden;
    }}
    
    .executive-title {{
        font-family: var(--brand-font);
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }}
    
    .executive-subtitle {{
        font-family: var(--brand-font);
        font-size: 1.2rem;
        opacity: 0.9;
        font-weight: 300;
        margin: 0;
    }}
    
    /* Company Branding */
    .company-brand {{
        position: absolute;
        top: 1rem;
        right: 1rem;
        font-size: 1.1rem;
        font-weight: 600;
        opacity: 0.8;
    }}
    
    /* Updated Metric Cards */
    .executive-metric {{
        background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid var(--primary-color);
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }}
    
    .executive-metric h3 {{
        font-family: var(--brand-font);
        font-size: 2.2rem;
        font-weight: 700;
        color: var(--primary-color);
        margin-bottom: 0.5rem;
    }}
    
    .executive-metric p {{
        font-family: var(--brand-font);
        color: var(--primary-color);
        font-size: 1rem;
        font-weight: 500;
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    
    /* Updated Section Headers */
    .section-header {{
        background: linear-gradient(90deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        margin: 1.5rem 0 1rem 0;
        font-family: var(--brand-font);
        font-size: 1.3rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }}
    
    /* Summary Cards with Brand Colors */
    .summary-card {{
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
    }}
    
    .summary-card h4 {{
        font-family: var(--brand-font);
        color: white;
        margin-bottom: 1rem;
        font-size: 1.3rem;
        font-weight: 600;
    }}
    
    .summary-card .metric-value {{
        font-family: var(--brand-font);
        font-size: 2rem;
        font-weight: 700;
        color: var(--accent-color);
        margin-bottom: 0.5rem;
    }}
    
    /* Enhanced Status Indicators */
    .status-excellent {{ 
        background: linear-gradient(135deg, var(--success-color) 0%, #2ECC71 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        text-align: center;
        font-family: var(--brand-font);
    }}
    
    .status-good {{ 
        background: linear-gradient(135deg, var(--secondary-color) 0%, #3498DB 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        text-align: center;
        font-family: var(--brand-font);
    }}
    
    .status-warning {{ 
        background: linear-gradient(135deg, var(--warning-color) 0%, #F7B942 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        text-align: center;
        font-family: var(--brand-font);
    }}
    
    .status-critical {{ 
        background: linear-gradient(135deg, var(--danger-color) 0%, #EC7063 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        text-align: center;
        font-family: var(--brand-font);
    }}
    
    /* Segment Colors with Brand Theme */
    .segment-champions {{ border-left-color: var(--success-color); }}
    .segment-loyal {{ border-left-color: var(--secondary-color); }}
    .segment-potential {{ border-left-color: var(--accent-color); }}
    .segment-risk {{ border-left-color: var(--warning-color); }}
    .segment-lost {{ border-left-color: var(--danger-color); }}
    
    /* Typography Updates */
    h1, h2, h3 {{
        color: var(--primary-color);
        font-family: var(--brand-font);
        font-weight: 600;
    }}
    
    h1 {{
        border-bottom: 3px solid var(--accent-color);
        padding-bottom: 10px;
        margin-bottom: 20px;
    }}
    
    /* Enhanced Sidebar */
    .css-1d391kg {{
        background: linear-gradient(180deg, var(--primary-color) 0%, var(--secondary-color) 100%);
    }}
    
    /* Form Controls */
    .stSelectbox > div > div > div > div:focus {{
        border-color: var(--primary-color);
        box-shadow: 0 0 10px rgba(0,0,0,0.2);
    }}
    """
    
    # Add company name if provided
    if company_name:
        css += f"""
    .company-name::after {{
        content: "{company_name}";
    }}
    """
    
    # Add logo if provided
    if logo_url:
        css += f"""
    .company-logo {{
        background-image: url('{logo_url}');
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center;
        width: 120px;
        height: 40px;
        position: absolute;
        top: 1rem;
        right: 1rem;
    }}
    """
    
    css += "</style>"
    return css

def get_available_themes():
    """Return list of available brand themes"""
    return [(key, theme["name"], theme["description"]) for key, theme in BRAND_THEMES.items()]

def get_available_fonts():
    """Return list of available font families"""
    return [(key, name.split(',')[0].replace("'", "")) for key, name in FONT_FAMILIES.items()]