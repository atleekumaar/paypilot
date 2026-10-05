"""Script to generate a deterministic catalogue of realistic demo products for PayPilot."""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent
OUTPUT_FILE = DATA_DIR / "products.json"

PRODUCTS = []

# 1. LAPTOPS (26)
laptops = [
    ("LAP-001", "NovaBook Pro 14", "Nova", "Performance laptop designed for developers and AI workloads with dedicated tensor acceleration.", 1049.0, 4.7, 842, True, "Nova Direct", 3, {"ram_gb": 16, "storage_gb": 512, "gpu": "RTX 4060", "cpu": "Intel Core Ultra 7", "battery_hours": 9.5, "display_inches": 14.0}),
    ("LAP-002", "ApexBook AI 15", "Apex", "High-efficiency machine learning workstation with high-density battery and low thermal throttling.", 1149.0, 4.6, 620, True, "TechWorld", 2, {"ram_gb": 16, "storage_gb": 1000, "gpu": "RTX 4050", "cpu": "AMD Ryzen 7 8845HS", "battery_hours": 8.5, "display_inches": 15.6}),
    ("LAP-003", "ZenAir Dev 14", "Zenith", "Ultra-portable developer ultrabook with all-day battery life and neural processing unit.", 899.0, 4.5, 412, True, "PrimeSupply", 3, {"ram_gb": 16, "storage_gb": 512, "gpu": "Radeon 780M", "cpu": "AMD Ryzen 7 7840U", "battery_hours": 13.0, "display_inches": 14.0}),
    ("LAP-004", "ThinkDev Ultra 16", "Lenovo", "Engineered for robust software engineering and local LLM fine-tuning.", 1399.0, 4.8, 1250, True, "Lenovo Store", 4, {"ram_gb": 32, "storage_gb": 1000, "gpu": "RTX 4070", "cpu": "Intel Core i9 14900HX", "battery_hours": 6.0, "display_inches": 16.0}),
    ("LAP-005", "AeroEdge AI 14", "AeroTech", "Balanced daily driver with dedicated RTX graphics under 1.4kg.", 1099.0, 4.4, 310, True, "ElectroMart", 3, {"ram_gb": 16, "storage_gb": 512, "gpu": "RTX 4060", "cpu": "Intel Core Ultra 5", "battery_hours": 8.0, "display_inches": 14.5}),
    ("LAP-006", "BudgetCode 15", "CodeTech", "Affordable coding laptop with expandable RAM and solid battery.", 649.0, 4.1, 180, True, "BudgetPC", 5, {"ram_gb": 16, "storage_gb": 512, "gpu": "Integrated UHD", "cpu": "Intel Core i5 1335U", "battery_hours": 7.5, "display_inches": 15.6}),
    ("LAP-007", "TitanWorkstation 17", "Titan", "Heavyweight desktop replacement for deep learning with dual NVMe.", 2499.0, 4.9, 540, True, "Titan Official", 2, {"ram_gb": 64, "storage_gb": 2000, "gpu": "RTX 4090 Mobile", "cpu": "Intel Core i9 14900HX", "battery_hours": 3.5, "display_inches": 17.3}),
    ("LAP-008", "NovaBook Air 13", "Nova", "Featherweight laptop with high endurance battery for remote developers.", 799.0, 4.5, 520, True, "Nova Direct", 3, {"ram_gb": 16, "storage_gb": 512, "gpu": "Intel Arc", "cpu": "Intel Core Ultra 5", "battery_hours": 14.0, "display_inches": 13.3}),
    ("LAP-009", "Legion Pro 5 AI", "Lenovo", "High TDP gaming and machine learning laptop with rapid charge technology.", 1199.0, 4.6, 950, True, "Lenovo Store", 2, {"ram_gb": 16, "storage_gb": 1000, "gpu": "RTX 4060", "cpu": "AMD Ryzen 7 7745HX", "battery_hours": 5.5, "display_inches": 16.0}),
    ("LAP-010", "MacStudio Pro 14", "Apple", "Apple Silicon workhorse with unified memory architecture and industry-leading battery.", 1999.0, 4.9, 2100, True, "Apple Authorized", 2, {"ram_gb": 18, "storage_gb": 512, "gpu": "M3 Pro 14-Core", "cpu": "Apple M3 Pro", "battery_hours": 17.0, "display_inches": 14.2}),
    ("LAP-011", "ROG Zephyrus G14 AI", "ASUS", "OLED compact gaming and AI machine with vapor chamber cooling.", 1449.0, 4.7, 720, True, "ASUS Store", 3, {"ram_gb": 16, "storage_gb": 1000, "gpu": "RTX 4070", "cpu": "AMD Ryzen 9 8945HS", "battery_hours": 7.5, "display_inches": 14.0}),
    ("LAP-012", "Swift Go 14 AI", "Acer", "OLED display laptop equipped with Intel AI Boost NPU and lightweight aluminum chassis.", 749.0, 4.2, 280, True, "QuickShip Tech", 4, {"ram_gb": 16, "storage_gb": 512, "gpu": "Intel Arc", "cpu": "Intel Core Ultra 7", "battery_hours": 9.0, "display_inches": 14.0}),
    ("LAP-013", "Surface Dev Studio 2", "Microsoft", "Versatile touchscreen convertible for creators and developers.", 2199.0, 4.6, 380, True, "Microsoft Store", 3, {"ram_gb": 32, "storage_gb": 1000, "gpu": "RTX 4060", "cpu": "Intel Core i7 13700H", "battery_hours": 8.0, "display_inches": 14.4}),
    ("LAP-014", "Framework 13 Modular", "Framework", "Fully modular and upgradeable laptop made with sustainable aluminum.", 999.0, 4.6, 610, True, "Framework Direct", 5, {"ram_gb": 16, "storage_gb": 512, "gpu": "Radeon 780M", "cpu": "AMD Ryzen 5 7640U", "battery_hours": 9.0, "display_inches": 13.5}),
    ("LAP-015", "Tuxedo InfinityBook 14", "Tuxedo", "Native Linux ultrabook with pre-configured PyTorch and CUDA environments.", 1180.0, 4.5, 190, True, "OpenHardware Inc", 6, {"ram_gb": 32, "storage_gb": 1000, "gpu": "RTX 3050", "cpu": "Intel Core i7 13700H", "battery_hours": 8.0, "display_inches": 14.0}),
    ("LAP-016", "NovaBook Elite 16", "Nova", "Flagship workstation with 4K Mini-LED display and enterprise security.", 1899.0, 4.8, 430, True, "Nova Direct", 2, {"ram_gb": 32, "storage_gb": 2000, "gpu": "RTX 4080", "cpu": "Intel Core Ultra 9", "battery_hours": 7.0, "display_inches": 16.0}),
    ("LAP-017", "Predator Helios AI 16", "Acer", "Raw computational throughput for neural network training and heavy rendering.", 1249.0, 4.4, 510, True, "Acer Outlet", 3, {"ram_gb": 16, "storage_gb": 1000, "gpu": "RTX 4070", "cpu": "Intel Core i7 14700HX", "battery_hours": 4.5, "display_inches": 16.0}),
    ("LAP-018", "Stealth Dev 14", "MSI", "Magnesium-alloy slim chassis with dedicated RTX graphics for mobile developers.", 1120.0, 4.5, 340, True, "MicroCenter Hub", 2, {"ram_gb": 16, "storage_gb": 1000, "gpu": "RTX 4060", "cpu": "Intel Core Ultra 7", "battery_hours": 8.5, "display_inches": 14.0}),
    ("LAP-019", "OmniBook X AI", "HP", "Snapdragon X Elite powered laptop with 45 TOPS NPU and incredible 22h battery life.", 1199.0, 4.6, 420, True, "HP Store", 3, {"ram_gb": 16, "storage_gb": 1000, "gpu": "Qualcomm Adreno", "cpu": "Snapdragon X Elite", "battery_hours": 20.0, "display_inches": 14.0}),
    ("LAP-020", "Spectre x360 14", "HP", "2-in-1 convertible with 2.8K OLED display and haptic touchpad.", 1349.0, 4.7, 670, True, "HP Store", 2, {"ram_gb": 16, "storage_gb": 1000, "gpu": "Intel Arc", "cpu": "Intel Core Ultra 7", "battery_hours": 11.0, "display_inches": 14.0}),
    ("LAP-021", "Dell XPS 14 AI", "Dell", "Precision CNC aluminum craftsmanship with edge-to-edge glass and OLED panel.", 1499.0, 4.3, 810, True, "Dell Direct", 4, {"ram_gb": 16, "storage_gb": 512, "gpu": "RTX 4050", "cpu": "Intel Core Ultra 7", "battery_hours": 7.0, "display_inches": 14.5}),
    ("LAP-022", "ZenBook Pro 15 Duo", "ASUS", "Dual touchscreen workstation with secondary ScreenPad Plus for multitasking.", 1699.0, 4.5, 290, True, "ASUS Store", 3, {"ram_gb": 32, "storage_gb": 1000, "gpu": "RTX 4060", "cpu": "Intel Core i9 13900H", "battery_hours": 5.5, "display_inches": 15.6}),
    ("LAP-023", "Galaxy Book4 Pro 14", "Samsung", "Dynamic AMOLED 2X touchscreen with seamless Galaxy ecosystem synergy.", 1149.0, 4.5, 480, True, "Samsung Official", 2, {"ram_gb": 16, "storage_gb": 512, "gpu": "Intel Arc", "cpu": "Intel Core Ultra 7", "battery_hours": 12.0, "display_inches": 14.0}),
    ("LAP-024", "CyberBook 15 (Out of Stock)", "CyberTech", "Discounted RTX 4060 laptop, currently out of stock inventory.", 950.0, 4.4, 300, False, "Discount Warehouse", 7, {"ram_gb": 16, "storage_gb": 512, "gpu": "RTX 4060", "cpu": "AMD Ryzen 7 7735HS", "battery_hours": 7.0, "display_inches": 15.6}),
    ("LAP-025", "UltraBook AI Student", "Nova", "Accessible coding laptop designed for computer science and data science students.", 799.0, 4.5, 590, True, "Nova Direct", 2, {"ram_gb": 16, "storage_gb": 512, "gpu": "Radeon 780M", "cpu": "AMD Ryzen 7 7730U", "battery_hours": 11.5, "display_inches": 14.0}),
    ("LAP-026", "MonsterGaming 16", "Monster", "Bulky high-performance gaming laptop with loud cooling fans.", 1220.0, 4.0, 150, True, "GamerZone", 5, {"ram_gb": 16, "storage_gb": 1000, "gpu": "RTX 4060", "cpu": "Intel Core i7 13700HX", "battery_hours": 3.5, "display_inches": 16.0}),
]

for item in laptops:
    PRODUCTS.append({
        "id": item[0], "name": item[1], "brand": item[2], "category": "laptop",
        "description": item[3], "price": item[4], "currency": "USD",
        "rating": item[5], "review_count": item[6], "stock": item[7],
        "seller": item[8], "delivery_days": item[9], "features": item[10],
        "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=500&auto=format&fit=crop&q=60"
    })

# 2. PHONES (20)
phones = [
    ("PHN-001", "Pixel 9 Pro", "Google", "Cutting-edge on-device Gemini Nano AI phone with exceptional triple camera system.", 999.0, 4.8, 1420, True, "Google Store", 2, {"storage_gb": 256, "ram_gb": 16, "battery_hours": 24.0, "5g": True, "display_inches": 6.3}),
    ("PHN-002", "Galaxy S24 Ultra", "Samsung", "Titanium flagship with Galaxy AI capabilities, built-in S-Pen, and 200MP camera.", 1199.0, 4.7, 2800, True, "Samsung Official", 2, {"storage_gb": 256, "ram_gb": 12, "battery_hours": 26.0, "5g": True, "display_inches": 6.8}),
    ("PHN-003", "iPhone 16 Pro", "Apple", "Apple Intelligence powerhouse in grade 5 titanium with customizable Camera Control button.", 999.0, 4.8, 3500, True, "Apple Authorized", 2, {"storage_gb": 128, "ram_gb": 8, "battery_hours": 27.0, "5g": True, "display_inches": 6.3}),
    ("PHN-004", "Nothing Phone (2a)", "Nothing", "Iconic transparent Glyph design with balanced performance and clean Nothing OS.", 349.0, 4.4, 890, True, "Nothing Direct", 3, {"storage_gb": 128, "ram_gb": 8, "battery_hours": 22.0, "5g": True, "display_inches": 6.7}),
    ("PHN-005", "OnePlus 12", "OnePlus", "Snapdragon 8 Gen 3 flagship with ultra-fast 80W charging and Hasselblad tuned optics.", 799.0, 4.6, 1100, True, "OnePlus Official", 2, {"storage_gb": 256, "ram_gb": 12, "battery_hours": 28.0, "5g": True, "display_inches": 6.82}),
    ("PHN-006", "Pixel 8a", "Google", "The affordable AI smartphone with Google Tensor G3 and 7 years of OS updates.", 499.0, 4.5, 950, True, "Google Store", 2, {"storage_gb": 128, "ram_gb": 8, "battery_hours": 20.0, "5g": True, "display_inches": 6.1}),
    ("PHN-007", "Galaxy Z Fold 6", "Samsung", "Slim dual-screen foldable workstation with AI multitasking features.", 1899.0, 4.6, 680, True, "Samsung Official", 3, {"storage_gb": 512, "ram_gb": 12, "battery_hours": 21.0, "5g": True, "display_inches": 7.6}),
    ("PHN-008", "Xiaomi 14 Ultra", "Xiaomi", "Photography marvel with 1-inch sensor Leica quad-camera array.", 1299.0, 4.5, 430, True, "GlobalMobile", 4, {"storage_gb": 512, "ram_gb": 16, "battery_hours": 23.0, "5g": True, "display_inches": 6.73}),
    ("PHN-009", "iPhone 16", "Apple", "A18 chip with dynamic island, 48MP fusion camera, and Action button.", 799.0, 4.6, 2100, True, "Apple Authorized", 2, {"storage_gb": 128, "ram_gb": 8, "battery_hours": 22.0, "5g": True, "display_inches": 6.1}),
    ("PHN-010", "ASUS Zenfone 11 Ultra", "ASUS", "Compact flagship feel with massive 5500mAh endurance and headphone jack.", 899.0, 4.4, 320, True, "ASUS Store", 3, {"storage_gb": 256, "ram_gb": 12, "battery_hours": 30.0, "5g": True, "display_inches": 6.78}),
    ("PHN-011", "Motorola Edge 50 Ultra", "Motorola", "Real wood finish backing with Pantone validated display and AI color engine.", 799.0, 4.3, 260, True, "Moto Outlet", 3, {"storage_gb": 512, "ram_gb": 16, "battery_hours": 22.0, "5g": True, "display_inches": 6.7}),
    ("PHN-012", "Sony Xperia 1 VI", "Sony", "Professional camera tech with 85-170mm true optical telephoto zoom.", 1399.0, 4.4, 210, True, "Sony Hub", 4, {"storage_gb": 256, "ram_gb": 12, "battery_hours": 25.0, "5g": True, "display_inches": 6.5}),
    ("PHN-013", "Honor Magic6 Pro", "Honor", "Falcon camera system with AI eye tracking and tough jurhic glass.", 999.0, 4.5, 380, True, "GlobalTech", 5, {"storage_gb": 512, "ram_gb": 12, "battery_hours": 27.0, "5g": True, "display_inches": 6.8}),
    ("PHN-014", "Galaxy A55 5G", "Samsung", "Metal frame mid-ranger with Knox Vault security and 120Hz Super AMOLED.", 399.0, 4.3, 1400, True, "Samsung Official", 2, {"storage_gb": 128, "ram_gb": 8, "battery_hours": 26.0, "5g": True, "display_inches": 6.6}),
    ("PHN-015", "Nothing Phone (2)", "Nothing", "Premium Snapdragon 8+ Gen 1 experience with custom LED interface.", 599.0, 4.5, 870, True, "Nothing Direct", 3, {"storage_gb": 256, "ram_gb": 12, "battery_hours": 23.0, "5g": True, "display_inches": 6.7}),
    ("PHN-016", "Realme GT 6 AI", "Realme", "Snapdragon 8s Gen 3 flagship killer with 6000 nit ultra-bright panel.", 499.0, 4.2, 530, True, "Realme Store", 4, {"storage_gb": 256, "ram_gb": 12, "battery_hours": 28.0, "5g": True, "display_inches": 6.78}),
    ("PHN-017", "iPhone SE (Out of Stock)", "Apple", "Pocket-sized iPhone with Touch ID, currently waiting for restock.", 429.0, 4.2, 3100, False, "Discount Retail", 6, {"storage_gb": 64, "ram_gb": 4, "battery_hours": 15.0, "5g": True, "display_inches": 4.7}),
    ("PHN-018", "OnePlus Nord 4", "OnePlus", "Unibody all-metal 5G phone with long battery life and fast 100W SuperVOOC.", 399.0, 4.4, 620, True, "OnePlus Official", 3, {"storage_gb": 256, "ram_gb": 12, "battery_hours": 29.0, "5g": True, "display_inches": 6.74}),
    ("PHN-019", "ROG Phone 8 Pro", "ASUS", "Gaming powerhouse with AniMe Vision rear mini-LEDs and AirTriggers.", 1199.0, 4.6, 290, True, "ASUS Store", 2, {"storage_gb": 512, "ram_gb": 16, "battery_hours": 25.0, "5g": True, "display_inches": 6.78}),
    ("PHN-020", "Fairphone 5", "Fairphone", "Modular repairable smartphone with 10-year software commitment.", 699.0, 4.1, 190, True, "EcoShop", 5, {"storage_gb": 256, "ram_gb": 8, "battery_hours": 18.0, "5g": True, "display_inches": 6.46}),
]

for item in phones:
    PRODUCTS.append({
        "id": item[0], "name": item[1], "brand": item[2], "category": "phone",
        "description": item[3], "price": item[4], "currency": "USD",
        "rating": item[5], "review_count": item[6], "stock": item[7],
        "seller": item[8], "delivery_days": item[9], "features": item[10],
        "image_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500&auto=format&fit=crop&q=60"
    })

# 3. HEADPHONES (20)
headphones = [
    ("HDP-001", "Sony WH-1000XM5", "Sony", "Industry leading noise canceling wireless headphones with Auto NC Optimizer.", 398.0, 4.8, 4800, True, "Sony Authorized", 2, {"battery_hours": 30.0, "noise_cancelling": True, "wireless": True, "multipoint": True}),
    ("HDP-002", "Bose QuietComfort Ultra", "Bose", "World-class noise cancellation with spatial immersive audio and custom tuned sound.", 429.0, 4.7, 2400, True, "Bose Direct", 2, {"battery_hours": 24.0, "noise_cancelling": True, "wireless": True, "multipoint": True}),
    ("HDP-003", "AirPods Max", "Apple", "Computational audio with high-fidelity acoustic design and transparency mode.", 549.0, 4.6, 5200, True, "Apple Authorized", 2, {"battery_hours": 20.0, "noise_cancelling": True, "wireless": True, "multipoint": True}),
    ("HDP-004", "Sennheiser Momentum 4", "Sennheiser", "Audiophile acoustic profile with phenomenal 60-hour battery lifespan.", 349.0, 4.7, 1850, True, "AudioWorld", 3, {"battery_hours": 60.0, "noise_cancelling": True, "wireless": True, "multipoint": True}),
    ("HDP-005", "Audio-Technica ATH-M50xBT2", "Audio-Technica", "Legendary studio sound reproduction with Bluetooth convenience.", 199.0, 4.6, 3200, True, "SoundStudio Hub", 3, {"battery_hours": 50.0, "noise_cancelling": False, "wireless": True, "multipoint": True}),
    ("HDP-006", "Bowers & Wilkins Px7 S2e", "Bowers & Wilkins", "British high-fidelity audio design with luxurious memory foam ear cushions.", 399.0, 4.5, 780, True, "LuxuryAudio", 2, {"battery_hours": 30.0, "noise_cancelling": True, "wireless": True, "multipoint": True}),
    ("HDP-007", "Anker Soundcore Space One", "Anker", "Budget-friendly adaptive active noise cancelling with Hi-Res LDAC certification.", 99.0, 4.4, 2100, True, "Anker Direct", 2, {"battery_hours": 40.0, "noise_cancelling": True, "wireless": True, "multipoint": True}),
    ("HDP-008", "Sony WH-CH720N", "Sony", "Lightweight noise-canceling daily headphones powered by Sony V1 processor.", 148.0, 4.3, 1450, True, "Sony Authorized", 3, {"battery_hours": 35.0, "noise_cancelling": True, "wireless": True, "multipoint": True}),
    ("HDP-009", "Shure AONIC 50 Gen 2", "Shure", "Studio monitor grade acoustics with snapdragon sound and customizable EQ.", 349.0, 4.5, 410, True, "AudioExpress", 4, {"battery_hours": 45.0, "noise_cancelling": True, "wireless": True, "multipoint": True}),
    ("HDP-010", "Marshall Major IV", "Marshall", "Retro rock styling with 80+ hours of cordless playtime and wireless induction charging.", 149.0, 4.5, 1920, True, "Marshall Store", 3, {"battery_hours": 80.0, "noise_cancelling": False, "wireless": True, "multipoint": False}),
    ("HDP-011", "JBL Live 770NC", "JBL", "True adaptive noise cancelling with JBL signature sound and Personi-Fi 2.0.", 199.0, 4.3, 890, True, "JBL Direct", 2, {"battery_hours": 50.0, "noise_cancelling": True, "wireless": True, "multipoint": True}),
    ("HDP-012", "Beats Studio Pro", "Beats", "Custom acoustic platform with lossless audio via USB-C and spatial audio.", 349.0, 4.4, 2300, True, "Beats Outlet", 2, {"battery_hours": 40.0, "noise_cancelling": True, "wireless": True, "multipoint": True}),
    ("HDP-013", "Focal Bathys Hi-Fi", "Focal", "High-end French audiophile headphones with built-in USB-DAC mode.", 699.0, 4.8, 380, True, "Audiophile Prime", 3, {"battery_hours": 30.0, "noise_cancelling": True, "wireless": True, "multipoint": True}),
    ("HDP-014", "1MORE Sonoflow Pro", "1MORE", "Incredible price-to-performance ANC headphones with LDAC and 70h battery.", 79.0, 4.4, 1150, True, "AudioSuper", 4, {"battery_hours": 70.0, "noise_cancelling": True, "wireless": True, "multipoint": True}),
    ("HDP-015", "Beyerdynamic DT 770 Pro 80 Ohm", "Beyerdynamic", "Studio legend closed-back wired reference headphones for audio mixing and podcasting.", 169.0, 4.8, 6700, True, "ProAudio Store", 3, {"battery_hours": 0.0, "noise_cancelling": False, "wireless": False, "multipoint": False}),
    ("HDP-016", "Jabra Evolve2 85", "Jabra", "Enterprise business headset with 10-microphone technology and busy-light.", 499.0, 4.4, 620, True, "WorkplaceTech", 2, {"battery_hours": 37.0, "noise_cancelling": True, "wireless": True, "multipoint": True}),
    ("HDP-017", "SteelSeries Arctis Nova Pro Wireless", "SteelSeries", "Multi-system gaming headset with hot-swappable dual battery system.", 349.0, 4.7, 1800, True, "SteelSeries Hub", 2, {"battery_hours": 44.0, "noise_cancelling": True, "wireless": True, "multipoint": True}),
    ("HDP-018", "Sennheiser HD 600", "Sennheiser", "Iconic open-back audiophile benchmark headphones for critical analytical listening.", 399.0, 4.9, 4300, True, "AudioWorld", 3, {"battery_hours": 0.0, "noise_cancelling": False, "wireless": False, "multipoint": False}),
    ("HDP-019", "Skullcandy Crusher ANC 2", "Skullcandy", "Adjustable sensory bass headphones for deep bass enthusiasts.", 229.0, 4.2, 940, True, "BassShop", 3, {"battery_hours": 50.0, "noise_cancelling": True, "wireless": True, "multipoint": True}),
    ("HDP-020", "Philips Fidelio L3 (Out of Stock)", "Philips", "Muirhead leather crafted ANC wireless headphones currently out of stock.", 199.0, 4.1, 410, False, "Discount Audio", 5, {"battery_hours": 38.0, "noise_cancelling": True, "wireless": True, "multipoint": True}),
]

for item in headphones:
    PRODUCTS.append({
        "id": item[0], "name": item[1], "brand": item[2], "category": "headphones",
        "description": item[3], "price": item[4], "currency": "USD",
        "rating": item[5], "review_count": item[6], "stock": item[7],
        "seller": item[8], "delivery_days": item[9], "features": item[10],
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&auto=format&fit=crop&q=60"
    })

# 4. KEYBOARDS (20)
keyboards = [
    ("KBD-001", "Keychron Q1 Pro Wireless", "Keychron", "Full CNC aluminum 75% mechanical keyboard with hot-swappable switches and QMK/VIA.", 199.0, 4.8, 1420, True, "Keychron Official", 3, {"layout": "75%", "wireless": True, "hot_swappable": True, "switch_type": "Gateron Jupiter Brown"}),
    ("KBD-002", "Logitech MX Mechanical", "Logitech", "Low-profile tactile quiet switches with smart illumination and multi-device pairing.", 169.0, 4.7, 3100, True, "Logitech Direct", 2, {"layout": "Full Size", "wireless": True, "hot_swappable": False, "switch_type": "Tactile Quiet"}),
    ("KBD-003", "NuPhy Air75 V2", "NuPhy", "Ultra-thin wireless mechanical keyboard with 1000Hz polling rate and macOS/Windows compatibility.", 119.0, 4.6, 980, True, "NuPhy Hub", 3, {"layout": "75%", "wireless": True, "hot_swappable": True, "switch_type": "Gateron Low Profile Cowberry"}),
    ("KBD-004", "Corsair K70 MAX RGB", "Corsair", "Magnetic-mechanical keyboard with adjustable actuation switches from 0.4mm to 3.6mm.", 229.0, 4.6, 820, True, "Corsair Official", 2, {"layout": "Full Size", "wireless": False, "hot_swappable": False, "switch_type": "Corsair MGX Magnetic"}),
    ("KBD-005", "Razer BlackWidow V4 Pro", "Razer", "Battlestation command center keyboard with dedicated macro keys and Razer Command Dial.", 229.0, 4.5, 1150, True, "Razer Store", 2, {"layout": "Full Size", "wireless": False, "hot_swappable": False, "switch_type": "Razer Green Clicky"}),
    ("KBD-006", "Epomaker RT100 Retro", "Epomaker", "Retro 97-key mechanical keyboard with customizable smart mini-TV display and volume knob.", 105.0, 4.5, 750, True, "Epomaker Store", 4, {"layout": "96%", "wireless": True, "hot_swappable": True, "switch_type": "Sea Salt Silent"}),
    ("KBD-007", "Ducky One 3 RGB", "Ducky", "Quack mechanics acoustic dampening keyboard with dual-layer PCB and PBT seamless keycaps.", 139.0, 4.6, 920, True, "Ducky Authorized", 3, {"layout": "TKL", "wireless": False, "hot_swappable": True, "switch_type": "Cherry MX Red"}),
    ("KBD-008", "SteelSeries Apex Pro TKL", "SteelSeries", "OmniPoint 2.0 hypermagnetic switches with rapid trigger for competitive gaming.", 199.0, 4.7, 1890, True, "SteelSeries Hub", 2, {"layout": "TKL", "wireless": False, "hot_swappable": False, "switch_type": "OmniPoint 2.0"}),
    ("KBD-009", "Keychron V1 Custom", "Keychron", "Entry-level custom mechanical keyboard with screw-in stabilizers and sound absorbing foam.", 74.0, 4.5, 1100, True, "Keychron Official", 3, {"layout": "75%", "wireless": False, "hot_swappable": True, "switch_type": "Keychron K Pro Red"}),
    ("KBD-010", "HHKB Professional HYBRID Type-S", "PFU Fujitsu", "Electrostatic capacitive Topre key switches with near-silent operation and ergonomic layout.", 320.0, 4.8, 640, True, "Topre Direct", 4, {"layout": "60%", "wireless": True, "hot_swappable": False, "switch_type": "Topre 45g Silent"}),
    ("KBD-011", "Logitech Ergo K860", "Logitech", "Split ergonomic wireless keyboard with pillowed wrist rest for reduced muscle strain.", 129.0, 4.5, 4500, True, "Logitech Direct", 2, {"layout": "Ergo Split", "wireless": True, "hot_swappable": False, "switch_type": "Scissor Membrane"}),
    ("KBD-012", "Drop ALT High-Profile", "Drop", "Anodized aluminum compact keyboard with hot-swap sockets and dual USB-C connectors.", 180.0, 4.4, 530, True, "Drop Outlet", 4, {"layout": "65%", "wireless": False, "hot_swappable": True, "switch_type": "Halo Clear"}),
    ("KBD-013", "Akko 5075B Plus", "Akko", "Gasket-mounted mechanical keyboard with multi-modes wireless and side RGB glow.", 89.0, 4.4, 610, True, "Akko Store", 3, {"layout": "75%", "wireless": True, "hot_swappable": True, "switch_type": "Akko V3 Cream Yellow"}),
    ("KBD-014", "Wooting 60HE+", "Wooting", "Analog Hall effect keyboard with tachyon mode for sub-1ms input latency.", 175.0, 4.9, 1300, True, "Wooting Direct", 5, {"layout": "60%", "wireless": False, "hot_swappable": True, "switch_type": "Lekker Magnetic"}),
    ("KBD-015", "Apple Magic Keyboard with Touch ID", "Apple", "Ultra-slim wireless scissor keyboard with biometric Touch ID login for Mac.", 149.0, 4.6, 2700, True, "Apple Authorized", 2, {"layout": "Compact", "wireless": True, "hot_swappable": False, "switch_type": "Apple Scissor"}),
    ("KBD-016", "RK ROYAL KLUDGE RK61", "RK", "Budget friendly 60% triple-mode wireless mechanical keyboard for portable setups.", 49.0, 4.3, 3800, True, "RK Prime", 3, {"layout": "60%", "wireless": True, "hot_swappable": True, "switch_type": "RK Brown"}),
    ("KBD-017", "GMMK PRO 75%", "Glorious", "Ultra-premium enthusiast gasket-mounted barebones keyboard frame with rotary knob.", 169.0, 4.5, 870, True, "Glorious Gaming", 3, {"layout": "75%", "wireless": False, "hot_swappable": True, "switch_type": "Enthusiast Barebone"}),
    ("KBD-018", "Mistel BAROCCO MD770 Split", "Mistel", "Ergonomic split keyboard separating in two halves for neutral shoulder positioning.", 159.0, 4.3, 310, True, "ErgoShop", 4, {"layout": "75% Split", "wireless": False, "hot_swappable": False, "switch_type": "Cherry MX Silent Red"}),
    ("KBD-019", "Logitech G PRO X TKL LIGHTSPEED", "Logitech", "Esports tournament mechanical keyboard with dual-shot PBT keycaps and zero-lag wireless.", 199.0, 4.5, 940, True, "Logitech Direct", 2, {"layout": "TKL", "wireless": True, "hot_swappable": False, "switch_type": "GX Blue Clicky"}),
    ("KBD-020", "Redragon K552 Kumara (Out of Stock)", "Redragon", "Inexpensive entry mechanical keyboard, currently sold out.", 39.0, 4.2, 4900, False, "BudgetGamer", 6, {"layout": "TKL", "wireless": False, "hot_swappable": False, "switch_type": "Outemu Blue"}),
]

for item in keyboards:
    PRODUCTS.append({
        "id": item[0], "name": item[1], "brand": item[2], "category": "keyboard",
        "description": item[3], "price": item[4], "currency": "USD",
        "rating": item[5], "review_count": item[6], "stock": item[7],
        "seller": item[8], "delivery_days": item[9], "features": item[10],
        "image_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=500&auto=format&fit=crop&q=60"
    })

# 5. MONITORS (16)
monitors = [
    ("MON-001", "Dell UltraSharp 27 4K (U2723QE)", "Dell", "IPS Black technology monitor with 2000:1 contrast ratio and 90W USB-C hub.", 579.0, 4.7, 1850, True, "Dell Direct", 3, {"size_inches": 27.0, "resolution": "3840x2160 (4K)", "refresh_hz": 60, "panel": "IPS Black", "usb_c_hub": True}),
    ("MON-002", "LG 27GP850-B UltraGear", "LG", "Nano IPS gaming monitor with 180Hz refresh rate and 1ms GtG response.", 349.0, 4.6, 3200, True, "LG Electronics", 2, {"size_inches": 27.0, "resolution": "2560x1440 (QHD)", "refresh_hz": 180, "panel": "Nano IPS", "usb_c_hub": False}),
    ("MON-003", "ASUS ProArt PA329CRV 32 4K", "ASUS", "Factory calibrated professional display with 98% DCI-P3 and 96W USB-C power delivery.", 699.0, 4.8, 640, True, "ASUS Store", 3, {"size_inches": 32.0, "resolution": "3840x2160 (4K)", "refresh_hz": 60, "panel": "IPS", "usb_c_hub": True}),
    ("MON-004", "Samsung Odyssey OLED G9 49", "Samsung", "Immense 49-inch curved dual QHD OLED display with 0.03ms response and Neo Quantum Processor.", 1299.0, 4.7, 880, True, "Samsung Official", 2, {"size_inches": 49.0, "resolution": "5120x1440 (Dual QHD)", "refresh_hz": 240, "panel": "QD-OLED", "usb_c_hub": False}),
    ("MON-005", "BenQ PD2705U Designer Monitor", "BenQ", "Calman verified color accurate display with KVM switch and hotkey puck.", 449.0, 4.5, 710, True, "BenQ Direct", 3, {"size_inches": 27.0, "resolution": "3840x2160 (4K)", "refresh_hz": 60, "panel": "IPS", "usb_c_hub": True}),
    ("MON-006", "Alienware AW3423DWF QD-OLED", "Alienware", "Ultrawide curved QD-OLED monitor with infinite contrast and 165Hz refresh.", 899.0, 4.8, 1420, True, "Dell Direct", 2, {"size_inches": 34.0, "resolution": "3440x1440 (UWQHD)", "refresh_hz": 165, "panel": "QD-OLED", "usb_c_hub": False}),
    ("MON-007", "Gigabyte M27Q X", "Gigabyte", "SuperSpeed IPS panel with 240Hz refresh rate and integrated KVM switch.", 399.0, 4.5, 1250, True, "Gigabyte Hub", 3, {"size_inches": 27.0, "resolution": "2560x1440 (QHD)", "refresh_hz": 240, "panel": "SS IPS", "usb_c_hub": True}),
    ("MON-008", "Apple Studio Display 27 5K", "Apple", "5K Retina display with 12MP ultra-wide camera with Center Stage and studio quality mics.", 1599.0, 4.6, 1950, True, "Apple Authorized", 2, {"size_inches": 27.0, "resolution": "5120x2880 (5K)", "refresh_hz": 60, "panel": "IPS", "usb_c_hub": True}),
    ("MON-009", "MSI MAG 274UPF 4K 144Hz", "MSI", "Rapid IPS 4K monitor designed for both productivity workstations and next-gen gaming.", 429.0, 4.4, 520, True, "MSI Official", 3, {"size_inches": 27.0, "resolution": "3840x2160 (4K)", "refresh_hz": 144, "panel": "Rapid IPS", "usb_c_hub": True}),
    ("MON-010", "ViewSonic VA2447-MH 24", "ViewSonic", "Essential home office monitor with eye-care flicker-free technology.", 99.0, 4.2, 2800, True, "OfficeSupplies", 4, {"size_inches": 24.0, "resolution": "1920x1080 (FHD)", "refresh_hz": 75, "panel": "VA", "usb_c_hub": False}),
    ("MON-011", "LG 34WN80C-B UltraWide", "LG", "Curved 21:9 productivity monitor with USB-C 60W connectivity and HDR10.", 469.0, 4.5, 2300, True, "LG Electronics", 3, {"size_inches": 34.0, "resolution": "3440x1440 (UWQHD)", "refresh_hz": 60, "panel": "IPS", "usb_c_hub": True}),
    ("MON-012", "ASUS ROG Swift PG32UCDM", "ASUS", "Third-generation 4K QD-OLED gaming monitor with custom heatsink and 240Hz refresh.", 1299.0, 4.8, 410, True, "ASUS Store", 2, {"size_inches": 32.0, "resolution": "3840x2160 (4K)", "refresh_hz": 240, "panel": "QD-OLED", "usb_c_hub": True}),
    ("MON-013", "Dell S2722QC 27 4K USB-C", "Dell", "Sleek lifestyle monitor with dual 3W speakers and single-cable USB-C convenience.", 369.0, 4.6, 2100, True, "Dell Direct", 2, {"size_inches": 27.0, "resolution": "3840x2160 (4K)", "refresh_hz": 60, "panel": "IPS", "usb_c_hub": True}),
    ("MON-014", "Samsung Smart Monitor M8 32", "Samsung", "All-in-one Smart TV monitor with SlimFit camera and IoT hub integration.", 499.0, 4.3, 850, True, "Samsung Official", 3, {"size_inches": 32.0, "resolution": "3840x2160 (4K)", "refresh_hz": 60, "panel": "VA", "usb_c_hub": True}),
    ("MON-015", "KTC G27P6 OLED 240Hz", "KTC", "Budget OLED 1440p gaming monitor with instantaneous pixel response.", 649.0, 4.3, 310, True, "TechBargains", 4, {"size_inches": 27.0, "resolution": "2560x1440 (QHD)", "refresh_hz": 240, "panel": "OLED", "usb_c_hub": True}),
    ("MON-016", "Acer Nitro 24 FHD (Out of Stock)", "Acer", "Budget esports monitor currently out of inventory.", 119.0, 4.1, 1400, False, "Discount Retail", 5, {"size_inches": 23.8, "resolution": "1920x1080 (FHD)", "refresh_hz": 165, "panel": "IPS", "usb_c_hub": False}),
]

for item in monitors:
    PRODUCTS.append({
        "id": item[0], "name": item[1], "brand": item[2], "category": "monitor",
        "description": item[3], "price": item[4], "currency": "USD",
        "rating": item[5], "review_count": item[6], "stock": item[7],
        "seller": item[8], "delivery_days": item[9], "features": item[10],
        "image_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=500&auto=format&fit=crop&q=60"
    })

# 6. SMARTWATCHES (14)
watches = [
    ("WAT-001", "Apple Watch Ultra 2", "Apple", "Rugged 49mm titanium sports smartwatch with precision dual-frequency GPS and 36h battery.", 799.0, 4.9, 2400, True, "Apple Authorized", 2, {"battery_hours": 36.0, "gps": True, "water_resistant_meters": 100, "cellular": True}),
    ("WAT-002", "Galaxy Watch Ultra", "Samsung", "Cushion titanium design with Galaxy AI health insights and dual-frequency GPS.", 649.0, 4.7, 980, True, "Samsung Official", 2, {"battery_hours": 60.0, "gps": True, "water_resistant_meters": 100, "cellular": True}),
    ("WAT-003", "Garmin Forerunner 965", "Garmin", "AMOLED running smartwatch with advanced training readiness metrics and titanium bezel.", 599.0, 4.8, 1650, True, "Garmin Direct", 3, {"battery_hours": 550.0, "gps": True, "water_resistant_meters": 50, "cellular": False}),
    ("WAT-004", "Pixel Watch 3 45mm", "Google", "Actua display with comprehensive Fitbit fitness readiness coaching and Loss of Pulse Detection.", 399.0, 4.5, 780, True, "Google Store", 2, {"battery_hours": 24.0, "gps": True, "water_resistant_meters": 50, "cellular": True}),
    ("WAT-005", "Apple Watch Series 10", "Apple", "Thinnest Apple Watch ever with 40% brighter wide-angle OLED display and sleep apnea detection.", 399.0, 4.8, 3100, True, "Apple Authorized", 2, {"battery_hours": 18.0, "gps": True, "water_resistant_meters": 50, "cellular": False}),
    ("WAT-006", "Galaxy Watch 7 44mm", "Samsung", "3nm processor with dual-frequency GPS and FDA-authorized sleep apnea tracking.", 329.0, 4.6, 1200, True, "Samsung Official", 2, {"battery_hours": 40.0, "gps": True, "water_resistant_meters": 50, "cellular": False}),
    ("WAT-007", "Coros Pace 3", "Coros", "Featherlight 30g GPS sports watch with 38 hours of continuous standard GPS battery.", 229.0, 4.7, 890, True, "RunningPro", 3, {"battery_hours": 400.0, "gps": True, "water_resistant_meters": 50, "cellular": False}),
    ("WAT-008", "Garmin Venu 3", "Garmin", "Health and fitness GPS smartwatch with nap detection, voice calls, and wheelchair mode.", 449.0, 4.6, 1100, True, "Garmin Direct", 3, {"battery_hours": 330.0, "gps": True, "water_resistant_meters": 50, "cellular": False}),
    ("WAT-009", "Withings ScanWatch 2", "Withings", "Hybrid smartwatch with medical-grade ECG, continuous baseline temperature, and 30-day battery.", 349.0, 4.4, 420, True, "HealthTech", 4, {"battery_hours": 720.0, "gps": False, "water_resistant_meters": 50, "cellular": False}),
    ("WAT-010", "Amazfit Balance AI", "Amazfit", "Smart health watch with Zepp Flow AI natural voice assistant and dual-band GPS.", 229.0, 4.4, 650, True, "SmartFit Direct", 3, {"battery_hours": 336.0, "gps": True, "water_resistant_meters": 50, "cellular": False}),
    ("WAT-011", "OnePlus Watch 2", "OnePlus", "Dual-engine architecture running Wear OS 4 with up to 100 hours in Smart Mode.", 299.0, 4.5, 520, True, "OnePlus Official", 3, {"battery_hours": 100.0, "gps": True, "water_resistant_meters": 50, "cellular": False}),
    ("WAT-012", "Fitbit Charge 6", "Fitbit", "Premium fitness tracker with Google apps integration, YouTube music controls, and EDA scan.", 159.0, 4.3, 2900, True, "Google Store", 2, {"battery_hours": 168.0, "gps": True, "water_resistant_meters": 50, "cellular": False}),
    ("WAT-013", "Polar Vantage V3", "Polar", "Premium multisport watch with biosensing Elixir technology and offline mapping.", 599.0, 4.5, 230, True, "Polar Store", 4, {"battery_hours": 140.0, "gps": True, "water_resistant_meters": 50, "cellular": False}),
    ("WAT-014", "Garmin Instinct 2 Solar (Out of Stock)", "Garmin", "Solar powered unlimited battery rugged GPS watch, currently awaiting restock.", 399.0, 4.6, 1750, False, "Outdoor Outlet", 6, {"battery_hours": 999.0, "gps": True, "water_resistant_meters": 100, "cellular": False}),
]

for item in watches:
    PRODUCTS.append({
        "id": item[0], "name": item[1], "brand": item[2], "category": "smartwatch",
        "description": item[3], "price": item[4], "currency": "USD",
        "rating": item[5], "review_count": item[6], "stock": item[7],
        "seller": item[8], "delivery_days": item[9], "features": item[10],
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&auto=format&fit=crop&q=60"
    })

# 7. ACCESSORIES (18)
accessories = [
    ("ACC-001", "CalDigit TS4 Thunderbolt 4 Dock", "CalDigit", "18-port Thunderbolt 4 dock delivering 98W charging and dual 6K display support.", 399.0, 4.8, 1600, True, "CalDigit Direct", 2, {"ports": 18, "power_delivery_watts": 98, "type": "Docking Station"}),
    ("ACC-002", "Logitech MX Master 3S", "Logitech", "Ergonomic wireless performance mouse with 8K DPI sensor and quiet click switches.", 99.0, 4.8, 8500, True, "Logitech Direct", 2, {"dpi": 8000, "battery_days": 70, "wireless": True, "type": "Mouse"}),
    ("ACC-003", "Anker 737 Power Bank (PowerCore 24K)", "Anker", "24,000mAh portable charger with ultra-powerful 140W bi-directional fast charging.", 149.0, 4.7, 4200, True, "Anker Direct", 2, {"capacity_mah": 24000, "output_watts": 140, "type": "Power Bank"}),
    ("ACC-004", "Twelve South Curve Laptop Stand", "Twelve South", "Matte black aluminum desktop stand elevating laptop screen to ergonomic height.", 59.0, 4.7, 2100, True, "TwelveSouth Store", 2, {"material": "Aluminum", "type": "Laptop Stand"}),
    ("ACC-005", "Baseus 65W GaN5 Pro Fast Charger", "Baseus", "Compact 3-port GaN wall charger with fold-away prongs for laptops and phones.", 39.0, 4.5, 3400, True, "Baseus Official", 3, {"power_watts": 65, "ports": 3, "type": "Charger"}),
    ("ACC-006", "BenQ ScreenBar Halo", "BenQ", "Wireless light bar with rear ambient backlight and auto-dimming precision sensor.", 179.0, 4.7, 1950, True, "BenQ Direct", 3, {"wireless_controller": True, "type": "Monitor Light Bar"}),
    ("ACC-007", "Elgato Stream Deck MK.2", "Elgato", "15 customizable LCD keys to trigger studio workflows, audio levels, and hotkeys.", 149.0, 4.8, 3800, True, "Elgato Store", 2, {"keys": 15, "type": "Macro Controller"}),
    ("ACC-008", "Belkin 3-in-1 MagSafe Wireless Charger", "Belkin", "Fast 15W MagSafe wireless charging stand for iPhone, Apple Watch, and AirPods.", 149.0, 4.6, 2900, True, "Belkin Direct", 2, {"power_watts": 15, "type": "Wireless Charger"}),
    ("ACC-009", "Samsung T7 Shield 2TB Portable SSD", "Samsung", "Rugged external solid state drive with IP65 dust/water resistance and 1050MB/s speeds.", 179.0, 4.8, 4800, True, "Samsung Official", 2, {"capacity_gb": 2000, "speed_mbps": 1050, "type": "External SSD"}),
    ("ACC-010", "Logitech MX Palm Rest", "Logitech", "Premium cushioned wrist support offering memory foam comfort for mechanical keyboards.", 24.0, 4.5, 2300, True, "Logitech Direct", 2, {"material": "Memory Foam", "type": "Palm Rest"}),
    ("ACC-011", "Sony Alpha 4K WebCam (Cam Link 4K)", "Elgato", "HDMI to USB capture card turning DSLR camera into ultra-high-definition webcam.", 129.0, 4.6, 1700, True, "Elgato Store", 3, {"resolution": "4K30", "type": "Capture Card"}),
    ("ACC-012", "UGREEN Revodok 10-in-1 USB C Hub", "UGREEN", "Multi-port adapter with dual HDMI 4K, 100W PD pass-through, and Gigabit Ethernet.", 59.0, 4.4, 2800, True, "UGREEN Direct", 2, {"ports": 10, "power_delivery_watts": 100, "type": "USB Hub"}),
    ("ACC-013", "SteelSeries QcK Heavy XXL Mousepad", "SteelSeries", "Thick non-slip rubber base desktop cloth gaming and work mouse pad.", 29.0, 4.7, 5600, True, "SteelSeries Hub", 2, {"size": "XXL (900x400mm)", "type": "Desk Mat"}),
    ("ACC-014", "Shure MV7+ USB/XLR Podcast Mic", "Shure", "Dynamic microphone with auto-level mode and customizable onboard DSP reverb.", 279.0, 4.8, 1200, True, "SoundStudio Hub", 3, {"connection": "USB-C & XLR", "type": "Microphone"}),
    ("ACC-015", "Orico M.2 NVMe SSD Enclosure 10Gbps", "Orico", "Tool-free aluminum casing supporting high-speed M.2 SSD data transfers.", 25.0, 4.3, 1400, True, "StorageTech", 3, {"speed_gbps": 10, "type": "SSD Enclosure"}),
    ("ACC-016", "Anker MagGo Wireless Power Bank 10K", "Anker", "Qi2 certified 15W magnetic portable charger with built-in smart display stand.", 89.0, 4.6, 1650, True, "Anker Direct", 2, {"capacity_mah": 10000, "type": "Power Bank"}),
    ("ACC-017", "MOFT Invisible Laptop Stand", "MOFT", "Adhesive foldable ultra-thin ergonomic laptop riser with dual viewing angles.", 29.0, 4.4, 1850, True, "MOFT Direct", 3, {"angles": "15 and 25 deg", "type": "Laptop Stand"}),
    ("ACC-018", "Apple MagSafe Battery Pack (Out of Stock)", "Apple", "Compact snap-on wireless external battery, discontinued and out of stock.", 99.0, 4.2, 3800, False, "Discount Retail", 6, {"type": "Power Bank"}),
]

for item in accessories:
    PRODUCTS.append({
        "id": item[0], "name": item[1], "brand": item[2], "category": "accessory",
        "description": item[3], "price": item[4], "currency": "USD",
        "rating": item[5], "review_count": item[6], "stock": item[7],
        "seller": item[8], "delivery_days": item[9], "features": item[10],
        "image_url": "https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=500&auto=format&fit=crop&q=60"
    })

OUTPUT_FILE.write_text(json.dumps(PRODUCTS, indent=2), encoding="utf-8")
print(f"Generated {len(PRODUCTS)} products across 7 categories into {OUTPUT_FILE}")
