import base64

# Base64 encode the Sonny Angel image
with open('images/cute sonny angel-modified.png', 'rb') as f:
    b64_img = base64.b64encode(f.read()).decode('utf-8')

text = "Hi there, Sreeja here!"

# Generate letter-by-letter keyframes and tspans
tspans_html = ""
css_rules = ""

for i, char in enumerate(text):
    delay = round(0.05 * i, 2)
    css_rules += f"      .c-{i} {{ animation: appear 0.15s {delay}s forwards; opacity: 0; }}\n"
    if char == " ":
        tspans_html += f'<tspan class="c-{i}">&#160;</tspan>'
    else:
        tspans_html += f'<tspan class="c-{i}">{char}</tspan>'

# Canvas width = 520px, Center = 260px
# Text width ~290px -> Text starts at x = 115px (Text center is at EXACT 260px center of canvas!)
# Sonny Angel image is placed right after text at x = 415px
svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="520" height="65" viewBox="0 0 520 65" fill="none">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Great+Vibes&amp;family=Dancing+Script:wght@700&amp;family=Pacifico&amp;display=swap');

      .cursive-title {{
        font-family: 'Great Vibes', 'Dancing Script', 'Pacifico', 'Brush Script MT', 'GreatVibes-Regular', cursive, sans-serif;
        font-size: 40px;
        font-weight: 500;
        fill: #FFFFFF;
      }}

      @keyframes appear {{
        0% {{ opacity: 0; transform: translateY(4px); }}
        100% {{ opacity: 1; transform: translateY(0); }}
      }}

{css_rules}
      /* Sonny Angel image fade in after text finishes */
      .angel-img {{
        animation: appear 0.35s 1.1s forwards;
        opacity: 0;
      }}
    </style>
  </defs>

  <g transform="translate(0, 32.5)">
    <!-- CURSIVE TITLE TEXT (WHITE COLOR) - CENTERED EXACTLY AT X=260 -->
    <text x="115" y="0" class="cursive-title" dominant-baseline="central">
      {tspans_html}
    </text>
    
    <!-- SONNY ANGEL IMAGE SHIFTED RIGHT AFTER THE CENTERED TEXT -->
    <g class="angel-img">
      <image href="data:image/png;base64,{b64_img}" x="412" y="-22" width="44" height="44"/>
    </g>
  </g>
</svg>
'''

with open('images/header_title.svg', 'w', encoding='utf-8') as f:
    f.write(svg_content)

print("Updated header_title.svg with WHITE text centered at x=260 and image shifted right!")
