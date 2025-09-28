import os

def check_template_blocks():
    template_dir = 'templates'
    if not os.path.exists(template_dir):
        print("  No blocks found.")
        return
    
    for filename in os.listdir(template_dir):
        if filename.endswith('.html'):
            filepath = os.path.join(template_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            starts = content.count('{% block')
            ends = content.count('{% endblock %}')
            
            print(f"{filename}:")
            print(f"   Block starts: {starts}")
            print(f"   Block ends: {ends}")
            print(f"   {'Balanced blocks' if starts == ends else 'UNBALANCED blocks'}\n")

if __name__ == '__main__':
    check_template_blocks()
