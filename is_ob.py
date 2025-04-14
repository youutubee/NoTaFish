import re

def is_obfuscated(html_content, verbose=True):
    reasons = []

    # Check 1: Long lines
    if any(len(line) > 1200 for line in html_content.splitlines()):
        reasons.append("💡 Long unbroken lines detected (>1200 chars)")

    # Check 2: High density of special chars
    total = len(html_content)
    special = len(re.findall(r"[;{}()\[\]=+]", html_content))
    if total > 0 and (special / total) > 0.15:
        reasons.append("💡 High ratio of special characters")

    # Check 3: Mangled JS functions (like _0x2a4b)
    if re.search(r"function\s+_0x[a-f0-9]{4,}", html_content):
        reasons.append("💡 Mangled JS function names found")

    # Check 4: Script-heavy content
    if html_content.strip().lower().startswith("<script") and "</html>" not in html_content.lower():
        reasons.append("💡 Dominated by <script> block")

    if verbose:
        if reasons:
            print("⚠️ Obfuscation Detected:")
            for r in reasons:
                print("   -", r)
        else:
            print("✅ No major signs of obfuscation.")

    return bool(reasons)


# Load the index.html file
with open("Templates/Facebook/index.html", "r", encoding="utf-8") as f:
    content = f.read()
