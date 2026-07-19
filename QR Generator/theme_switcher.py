import os
import re

# 1. Update CSS
css_file = r'c:\Users\Pinak\Desktop\QR Generator\app\static\css\style.css'
with open(css_file, 'r', encoding='utf-8') as f:
    css = f.read()

# Replace root variables
new_root = """:root {
  --bg-deepest:       #f4f6f8;
  --bg-page:          #ffffff;
  --bg-card:          #ffffff;
  --bg-card-hover:    #fdfdfd;
  --bg-header:        #f8f9fa;

  --sidebar-start:    #ffffff;
  --sidebar-end:      #f4f6f8;

  --accent-primary:   #9A4F3F;
  --accent-primary-dark: #7A3B2D;
  --accent-secondary: #5a5a5a;
  --success:          #2e7d32;
  --danger:           #c62828;
  --warning:          #ef6c00;

  --text-primary:     #212529;
  --text-secondary:   #495057;
  --text-muted:       #6c757d;

  --border-color:     #dee2e6;
  --border-focus:     rgba(154, 79, 63, 0.3);

  --glass-bg:         rgba(255, 255, 255, 0.95);
  --glass-border:     rgba(0, 0, 0, 0.08);

  --shadow-sm:        0 2px 4px rgba(0, 0, 0, 0.05);
  --shadow-md:        0 4px 12px rgba(0, 0, 0, 0.08);
  --shadow-lg:        0 8px 24px rgba(0, 0, 0, 0.12);
  --shadow-glow-amber: 0 4px 20px rgba(154, 79, 63, 0.15);
  --shadow-glow-blue:  0 4px 20px rgba(90, 90, 90, 0.1);
  --shadow-glow-red:   0 4px 20px rgba(198, 40, 40, 0.15);
  --shadow-glow-cyan:  0 4px 20px rgba(90, 90, 90, 0.1);

  --sidebar-width:    260px;
  --radius-sm:        6px;
  --radius-md:        10px;
  --radius-lg:        14px;
  --transition:       all 0.3s ease;
}"""
css = re.sub(r':root\s*\{.*?\}', new_root, css, flags=re.DOTALL)

# Replace hardcoded RGBA amber (240, 165, 0) with rust (154, 79, 63)
css = css.replace('240, 165, 0', '154, 79, 63')
# Replace hardcoded button text from dark to white
css = css.replace('color: #0a0a14 !important;', 'color: #ffffff !important;')
# Fix scrollbar
css = css.replace('background: #2a2a44;', 'background: #ccc;')
css = css.replace('background: #3a3a56;', 'background: #aaa;')
# Fix login gradient
css = css.replace('linear-gradient(135deg, #0a0a14, #0d1b2a, #1a1a2e, #0f0f1a)', 'linear-gradient(135deg, #ffffff, #f4f6f8, #e9ecef, #f8f9fa)')

with open(css_file, 'w', encoding='utf-8') as f:
    f.write(css)

# 2. Update HTML templates
templates_dir = r'c:\Users\Pinak\Desktop\QR Generator\app\templates'

replacements = {
    'bg-dark': 'bg-light',
    'table-dark': 'table-light',
    'text-white': 'text-dark',
    'border-secondary': 'border-muted',
    'btn-warning': 'btn-primary',
    'text-warning': 'text-primary',
    'bg-warning': 'bg-primary',
    'btn-outline-light': 'btn-outline-secondary',
    '#f0a500': '#9A4F3F',
    '#1a1a2e': '#ffffff'
}

for root, _, files in os.walk(templates_dir):
    for file in files:
        if file.endswith('.html'):
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for old, new in replacements.items():
                content = content.replace(old, new)
                
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)

print("Theme updated successfully.")
