from core.models import Category

categories = [
    {"name": "Programming", "icon": "💻", "description": "Learn to code with Python, JavaScript, and more."},
    {"name": "Music", "icon": "🎵", "description": "Master instruments, music theory, and production."},
    {"name": "Art & Design", "icon": "🎨", "description": "Unleash your creativity with drawing, painting, and digital art."},
    {"name": "Business", "icon": "💼", "description": "Entrepreneurship, marketing, and management skills."},
    {"name": "Health & Fitness", "icon": "🧘", "description": "Yoga, nutrition, and workout plans."},
    {"name": "Language", "icon": "🗣️", "description": "Learn new languages and connect with the world."},
]

for cat in categories:
    Category.objects.get_or_create(name=cat['name'], defaults=cat)
    print(f"Created/Checked category: {cat['name']}")
